from sshtunnel import SSHTunnelForwarder
import pymysql
import sys
from urllib.parse import unquote
import numpy as np
from datetime import datetime
import time


# -------------------- CONNECTION PARAMS -------------------------------
ssh_host = sys.argv[1]
ssh_port = int(sys.argv[2])
ssh_user = sys.argv[3]
ssh_pass = sys.argv[4]

db_host = sys.argv[5]
db_port = int(sys.argv[6])
db_user = sys.argv[7]
db_pass = sys.argv[8]
db_name = sys.argv[9]

# -------------------- PROCESSING PARAMS -------------------------------
_delimiter = "|<END>"
CANNED_TEXT_Q_SEVERE = "QUALITY ISSUES ARE TOO SEVERE TO RECOGNIZE VISUAL CONTENT"

BULK_THRESH = 500
WQ_TEXT_THRESH = 4  # if >= WQ_TEXT_THRESH workers say text exists
WQ_JOB_TIME_THRESH = 1.95  # if z-score of JOB_TIME is > WQ_JOB_TIME_THRESH
WQ_CAPS_THRESH = 50  # if more than WQ_CAPS_THRESH% of characters is in uppercase
WQ_Q_SEVERE_THRESH = 4  # if >= WQ_q_severe_THRESH workers quality is too severe
SPAM_1_THRESH = 50  # if more than SPAM_1_THRESH % of images have canned text

# ------------------------------ MAIN ---------------------------

if __name__ == '__main__':

    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_pass,
        remote_bind_address=(db_host, db_port)
    )

    tunnel.start()

    conn = pymysql.connect(
        host=db_host,
        port=tunnel.local_bind_port,
        user=db_user,
        passwd=db_pass,
        db=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    selectBlockedWorkersSql = (
        " select *"
        " from MAI_ImgCaption.BLOCKED_WORKERS "
    )

    selectRawSql = (
        " select *"
        " from MAI_ImgCaption.EXP_01_RAW_CROWD_RESULTS "
        " where PARSE_DT is null "
    )

    updateRawSql = (
        " update MAI_ImgCaption.EXP_01_RAW_CROWD_RESULTS "
        " set PARSE_DT = NOW() "
        " where ASSIGNMENTID = %s "
    )

    insertResultsSql = (
        " insert into MAI_ImgCaption.EXP_01_CROWD_RESULTS ( "
        "   IMG "
        " , WORKERID "
        " , Q_ISSUE_NONE "
        " , Q_ISSUE_BLR "
        " , Q_ISSUE_BRT "
        " , Q_ISSUE_DRK "
        " , Q_ISSUE_OBS "
        " , Q_ISSUE_FRM "
        " , Q_ISSUE_ROT "
        " , Q_ISSUE_OTH "
        " , OTH_ISSUE "
        " , TEXT_DETECT "
        " , IMG_CAPTION "
        " , FINAL_ANGLE "
        " , FINAL_ZOOM "
        " , ASSIGNMENTID "
        " , WORKER_DISP_SRL "
        #" , WORKER_ENGLISH_LEVEL "
        " , WORKER_RELATED_TO_BLIND "
        " , JOB_TIME "
        " , JOB_TIME_MEAN "
        " , JOB_TIME_SD "
        " , JOB_TIME_PER_IMG "
        " , JOB_TIME_PER_IMG_MEAN "
        " , JOB_TIME_PER_IMG_SD "
        " , JOB_TIME_MTURK "
        " , JOB_TIME_MTURK_MEAN "
        " , JOB_TIME_MTURK_SD "
        " , WQ_TEXT "
        " , WQ_JOB_TIME "
        " , WQ_JOB_TIME_PER_IMG "
        " , WQ_JOB_TIME_MTURK "
        " , WQ_CAPS "
        " , WQ_IMG_QUALITY "
        " , WQ_IMG_Q_SEVERE_4_5 "
        " , WQ_IMG_Q_SEVERE_1_5 "
        " , WQ_SPAM_1 "
        " , WQ_MANUAL_FLAG "
        " , BATCH_NUM "
        " ) "
        " values ( "
        "    %s, %s, %s, %s, %s, "
        "    %s, %s, %s, %s, %s, "
        "    %s, %s, %s, %s, %s, "
        "    %s, %s, %s, %s, %s, "
        "    %s, %s, %s, %s, %s, "
        "    %s, %s, %s, %s, %s, "
        "    %s, %s, %s, %s, %s, "
        "    %s, %s, %s "
        " )"
    )

    insertCommentsSql = (
        " insert into MAI_ImgCaption.EXP_01_CROWD_COMMENTS ( "
        "   ASSIGNMENTID "
        " , COMMENTS "
        " ) "
        " values ( "
        "    %s, %s "
        " )"
    )

    selectRawCur = conn.cursor()
    updateRawCur = conn.cursor()
    insertResultsCur = conn.cursor()
    insertCommentsCur = conn.cursor()

    BLOCKED_WORKERS_LIST = []

    print('Start parsing...')

    try:

        print('Collecting blocked worker list')

        selectRawCur.execute(
            " select *"
            " from MAI_ImgCaption.BLOCKED_WORKERS "
        )

        for row in selectRawCur:
            BLOCKED_WORKERS_LIST.append(row['WORKERID'])


        print('Done. No. of Blocked workers = %d. Fetching raw data...' % len(BLOCKED_WORKERS_LIST))

        selectRawCur.execute(selectRawSql)

        print('Done.')
        print('Start processing...')

        rowCount = 0
        totRows = selectRawCur.rowcount
        print("Rows to process: ", totRows)

        bulkInsertData = []
        bulkInsertData_dict = {}
        bulkInsertComment = []
        bulkUpdateRaw = []

        # for storing list of all job times for a single image
        """
        job times are calculated in three ways:
        1. from overall hit start and end times (dividing by no. of images)
        2. from individual image start and end times (*_per_img_*)
        3. from hit start and end times provided by MTurk (*_mturk_*)
        """
        dict_job_time_list = {}
        dict_job_time_per_img_list = {}
        dict_job_time_mturk_list = {}

        # for storing mean job-time for a single image
        dict_job_time_mean = {}
        dict_job_time_sd = {}

        # for storing mean job-time for a single image
        dict_job_time_per_img_mean = {}
        dict_job_time_per_img_sd = {}

        # for storing sd of job-time for a single image
        dict_job_time_mturk_mean = {}
        dict_job_time_mturk_sd = {}

        # for storing how many workers said text is present
        dict_text_detect = {}

        # for storing how many workers said "Quality issues are too severe"
        dict_q_severe_detect = {}

        # for storing count of images worker worked on
        dict_worker_img_n = {}

        # for storing count of images where worker used CANNED text
        dict_worker_canned_n = {}

        for row in selectRawCur:

            ASSIGNMENTID = row['ASSIGNMENTID']
            WORKERID = row['WORKERID']
            WQ_MANUAL_FLAG = 0

            # adding worker counts
            if WORKERID not in dict_worker_img_n:
                dict_worker_img_n[WORKERID] = 0
                dict_worker_canned_n[WORKERID] = 0


            if WORKERID in BLOCKED_WORKERS_LIST:
                print(">>> ERROR: Blocked Worker %s in ASSIGNMENTID %s" % (WORKERID, ASSIGNMENTID))

            BATCH_NUM = row['BATCH_NUM']

            if BATCH_NUM is None:
                print(">>> ERROR: BATCH_NUM not present for ASSIGNMENTID %s" % ASSIGNMENTID)
                exit(2)

            ASSIGNMENTACCEPTTIME = row['ASSIGNMENTACCEPTTIME']
            ASSIGNMENTSUBMITTIME = row['ASSIGNMENTSUBMITTIME']

            if row['ANS_HIT_ST_TIME'] is not None:
                ANS_HIT_ST_TIME = int(row['ANS_HIT_ST_TIME'])
            else:
                ANS_HIT_ST_TIME = int(round(time.time() * 1000))
                # WQ_MANUAL_FLAG = 1

            if row['ANS_HIT_END_TIME'] is not None:
                ANS_HIT_END_TIME = int(row['ANS_HIT_END_TIME'])
            else:
                ANS_HIT_END_TIME = int(round(time.time() * 1000))
                # WQ_MANUAL_FLAG = 1


            ANS_IMG = row['ANS_IMG']
            ANS_IMG_CAPTION = row['ANS_IMG_CAPTION']

            ANS_IMG_ST_TIME = row['ANS_IMG_ST_TIME']
            ANS_IMG_END_TIME = row['ANS_IMG_END_TIME']

            ANS_Q_ISSUE = row['ANS_Q_ISSUE']
            ANS_Q_ISSUE_OTH = row['ANS_Q_ISSUE_OTH']

            ANS_TEXT_DETECT = row['ANS_TEXT_DETECT']

            ANS_FINAL_ANGLE = row['ANS_FINAL_ANGLE']
            ANS_FINAL_ZOOM = row['ANS_FINAL_ZOOM']

            # ANS_WORKER_ENGLISH_LEVEL = row['ANS_WORKER_ENGLISH_LEVEL']
            ANS_WORKER_RELATED_TO_BLIND = row['ANS_WORKER_RELATED_TO_BLIND']

            # if ANS_WORKER_ENGLISH_LEVEL == -1:
            if ANS_WORKER_RELATED_TO_BLIND == -1:
                WQ_MANUAL_FLAG = 1


            ANS_WORKER_COMMENTS = row['ANS_WORKER_COMMENTS']

            ans_img_list = list(filter(None, ANS_IMG.split("|")))

            ans_img_st_time_list = list(filter(None, ANS_IMG_ST_TIME.split("|")))
            ans_img_end_time_list = list(filter(None, ANS_IMG_END_TIME.split("|")))

            n_images = len(ans_img_list)

            # job time
            JOB_TIME_HIT = ANS_HIT_END_TIME - ANS_HIT_ST_TIME  # in milliseconds
            JOB_TIME = JOB_TIME_HIT / n_images / 1000

            # job time MTurk. format: 'Sun Mar 03 12:56:25 CST 2019'

            if 'CST' in ASSIGNMENTACCEPTTIME:
                t1 = datetime.strptime(ASSIGNMENTACCEPTTIME, '%a %b %d %H:%M:%S CST %Y')
                t2 = datetime.strptime(ASSIGNMENTSUBMITTIME, '%a %b %d %H:%M:%S CST %Y')
            else:
                t1 = datetime.strptime(ASSIGNMENTACCEPTTIME, '%a %b %d %H:%M:%S CDT %Y')
                t2 = datetime.strptime(ASSIGNMENTSUBMITTIME, '%a %b %d %H:%M:%S CDT %Y')

            JOB_TIME_MTURK_HIT = (t2 - t1).total_seconds()  # in seconds
            JOB_TIME_MTURK = JOB_TIME_MTURK_HIT / n_images

            #####################################################
            # 1. parse quality issues, text presence and caption
            #####################################################

            # removes the last occurence of delimeter ("|<END>") in the strings
            # to avoid an empty last element,
            # and then splits the string based on the _delimeter
            q_issue_list = (ANS_Q_ISSUE[:-len(_delimiter)]
                            if ANS_Q_ISSUE.endswith(_delimiter) else ANS_Q_ISSUE
                            ).split(_delimiter)

            q_issue_oth_list = (ANS_Q_ISSUE_OTH[:-len(_delimiter)]
                            if ANS_Q_ISSUE_OTH.endswith(_delimiter) else ANS_Q_ISSUE_OTH
                            ).split(_delimiter)

            text_detect_list = (ANS_TEXT_DETECT[:-len(_delimiter)]
                                if ANS_TEXT_DETECT.endswith(_delimiter) else ANS_TEXT_DETECT
                                ).split(_delimiter)

            img_caption_list = (ANS_IMG_CAPTION[:-len(_delimiter)]
                                if ANS_IMG_CAPTION.endswith(_delimiter) else ANS_IMG_CAPTION
                                ).split(_delimiter)

            ans_final_angle_list = list(filter(None, ANS_FINAL_ANGLE.split("|")))

            ans_final_zoom_list = list(filter(None, ANS_FINAL_ZOOM.split("|")))

            # for each IMG
            for i, IMG in enumerate(ans_img_list):

                # adding job times
                if IMG not in dict_job_time_list:
                    dict_job_time_list[IMG] = []
                    dict_job_time_per_img_list[IMG] = []
                    dict_job_time_mturk_list[IMG] = []
                    dict_text_detect[IMG] = 0
                    dict_q_severe_detect[IMG] = 0
                # --- end of "first time" loop ----

                # updating worker's image count
                dict_worker_img_n[WORKERID] += 1

                # issues
                img_q_issue_list = list(filter(None, q_issue_list[i].split("|")))
                img_q_issue_oth_list = list(filter(None, q_issue_oth_list[i].split("|")))

                q_issue_dict = {
                    "Q_ISSUE_NONE": 0,
                    "Q_ISSUE_BLR": 0, "Q_ISSUE_BRT": 0, "Q_ISSUE_DRK": 0,
                    "Q_ISSUE_OBS": 0, "Q_ISSUE_FRM": 0, "Q_ISSUE_ROT": 0,
                    "Q_ISSUE_OTH": 0,
                }
                OTH_ISSUE = None
                WORKER_DISP_SRL = i + 1

                # for each Q_ISSUE
                for j, q_issue in enumerate(img_q_issue_list):

                    # set the particular reason as 1
                    q_issue_dict["Q_ISSUE_" + q_issue] = 1

                    if img_q_issue_oth_list and q_issue == 'OTH':
                        # multiple unquote() just to be sure (Mturk adds addtional urlencode)
                        OTH_ISSUE = unquote(unquote(img_q_issue_oth_list[0])).strip()

                # end of q_issue loop


                # check if no labels selected
                sum_labels = 0
                for key, value in q_issue_dict.items():
                    sum_labels += value

                if sum_labels < 1:
                    print("No-labels: workerid: %s \t img: %s" %(WORKERID, IMG))

                ################
                # text presence
                ################

                TEXT_DETECT = list(filter(None, text_detect_list[i].split("|")))
                TEXT_DETECT = unquote(unquote(TEXT_DETECT[0])).strip()

                if TEXT_DETECT == "Y":
                    TEXT_DETECT = 1
                elif TEXT_DETECT == "N":
                    TEXT_DETECT = 0
                else:
                    print("TEXT_DETECT_ERROR (%s): workerid: %s \t img: %s"
                          % (TEXT_DETECT, WORKERID, IMG))

                ###################################
                # caption, final angle, final zoom
                ###################################

                IMG_CAPTION = list(filter(None, img_caption_list[i].split("|")))
                IMG_CAPTION = unquote(unquote(IMG_CAPTION[0])).strip()

                FINAL_ANGLE = ans_final_angle_list[i]
                FINAL_ZOOM = ans_final_zoom_list[i]

                #################################################
                # WQ_CAPS: check if more than WQ_CAPS_THRESH%
                # of characters is in uppercase
                #################################################

                WQ_CAPS = 0

                caption_len, upper_cnt = len(IMG_CAPTION), 0

                for c in IMG_CAPTION:
                    if c.isupper():
                        upper_cnt += 1

                if upper_cnt / caption_len * 100 > WQ_CAPS_THRESH:
                    WQ_CAPS = 1



                #################################################
                # WQ_IMG_QUALITY: Flag as candidates for review
                # captions that have the words
                # "Quality", "Blur", or "Blurry"
                # However, ignore the sentence "Quality issues are too severe to recognize visual content."
                #################################################

                WQ_IMG_QUALITY = 0

                flag_word_list = [
                    'QUALITY', 'BLUR'
                ]

                if any(s in IMG_CAPTION.upper() for s in flag_word_list):
                    WQ_IMG_QUALITY = 1

                if WQ_IMG_QUALITY == 1 and CANNED_TEXT_Q_SEVERE in IMG_CAPTION.upper():
                    WQ_IMG_QUALITY = 0

                ###################
                # job time per img
                ###################

                img_st_time = int(ans_img_st_time_list[i])
                img_end_time = int(ans_img_end_time_list[i])

                if img_st_time == -999 or img_end_time == -999:
                    JOB_TIME_PER_IMG = -1
                else:
                    JOB_TIME_PER_IMG = int(ans_img_end_time_list[i]) - int(ans_img_st_time_list[i])
                    JOB_TIME_PER_IMG = JOB_TIME_PER_IMG / 1000


                ######################################
                # for calculating aggregate measures
                ######################################

                if JOB_TIME > 0:
                    dict_job_time_list[IMG].append(JOB_TIME)

                if JOB_TIME_PER_IMG > 0:
                    dict_job_time_per_img_list[IMG].append(JOB_TIME_PER_IMG)

                if JOB_TIME_MTURK > 0:
                    dict_job_time_mturk_list[IMG].append(JOB_TIME_MTURK)

                dict_text_detect[IMG] += TEXT_DETECT

                if CANNED_TEXT_Q_SEVERE in IMG_CAPTION.upper():
                    dict_q_severe_detect[IMG] += 1
                    dict_worker_canned_n[WORKERID] += 1

                # bulk insert data preparation
                bulkInsertData_dict[str(IMG) + '_' + str(WORKERID)] = {
                    'IMG': str(IMG),
                    'WORKERID': str(WORKERID),
                    'Q_ISSUE_NONE': str(q_issue_dict['Q_ISSUE_NONE']),
                    'Q_ISSUE_BLR': str(q_issue_dict['Q_ISSUE_BLR']),
                    'Q_ISSUE_BRT': str(q_issue_dict['Q_ISSUE_BRT']),
                    'Q_ISSUE_DRK': str(q_issue_dict['Q_ISSUE_DRK']),
                    'Q_ISSUE_OBS': str(q_issue_dict['Q_ISSUE_OBS']),
                    'Q_ISSUE_FRM': str(q_issue_dict['Q_ISSUE_FRM']),
                    'Q_ISSUE_ROT': str(q_issue_dict['Q_ISSUE_ROT']),
                    'Q_ISSUE_OTH': str(q_issue_dict['Q_ISSUE_OTH']),
                    'OTH_ISSUE': str(OTH_ISSUE),
                    'TEXT_DETECT': TEXT_DETECT,
                    'IMG_CAPTION': IMG_CAPTION,
                    'FINAL_ANGLE': FINAL_ANGLE,
                    'FINAL_ZOOM': FINAL_ZOOM,
                    'ASSIGNMENTID': str(ASSIGNMENTID),
                    'WORKER_DISP_SRL': str(WORKER_DISP_SRL),
                    # 'WORKER_ENGLISH_LEVEL': ANS_WORKER_ENGLISH_LEVEL,
                    'WORKER_RELATED_TO_BLIND': ANS_WORKER_RELATED_TO_BLIND,
                    'JOB_TIME': JOB_TIME,
                    'JOB_TIME_MEAN': -1,
                    'JOB_TIME_SD': -1,
                    'JOB_TIME_PER_IMG': JOB_TIME_PER_IMG,
                    'JOB_TIME_PER_IMG_MEAN': -1,
                    'JOB_TIME_PER_IMG_SD': -1,
                    'JOB_TIME_MTURK': JOB_TIME_MTURK,
                    'JOB_TIME_MTURK_MEAN': -1,
                    'JOB_TIME_MTURK_SD': -1,
                    'WQ_TEXT': -1,
                    'WQ_JOB_TIME': -1,
                    'WQ_JOB_TIME_PER_IMG': -1,
                    'WQ_JOB_TIME_MTURK': -1,
                    'WQ_CAPS': WQ_CAPS,
                    'WQ_IMG_QUALITY': WQ_IMG_QUALITY,
                    'WQ_IMG_Q_SEVERE_4_5': -1,
                    'WQ_IMG_Q_SEVERE_1_5': -1,
                    'WQ_SPAM_1': -1,
                    'WQ_MANUAL_FLAG': WQ_MANUAL_FLAG,
                    'BATCH_NUM': BATCH_NUM
                }

            # ----- end of IMG loop -----------

            pass

            #########################
            # 2. add worker comments
            #########################

            comments_pretty = ''

            if ANS_WORKER_COMMENTS is not None:
                # multiple unquote just to be sure (Mturk adds addtional urlencode)
                comments_pretty = unquote(unquote(unquote(ANS_WORKER_COMMENTS))).strip()

            if len(comments_pretty) > 0:
                bulkInsertComment.append([
                    str(ASSIGNMENTID),
                    str(comments_pretty)
                ])

            # 3. update RAW table with parse_dt
            bulkUpdateRaw.append([
                str(ASSIGNMENTID)
            ])

            rowCount += 1

        # ----- end of cursor loop -----------

        print('Finished first pass -- creating bulk-insert data dictionary.')
        print('Calculating aggregate measures...')

        pass

        #################################
        # calculate aggregate measures:
        # job time mean + sd
        #################################

        for img, job_time_list in dict_job_time_list.items():

            # -------- overall --------
            dict_job_time_mean[img] = float(np.mean(
                np.array(dict_job_time_list[img])
            ))

            dict_job_time_sd[img] = float(np.std(
                np.array(dict_job_time_list[img])
            ))

            # -------- _per_img --------
            dict_job_time_per_img_mean[img] = float(np.mean(
                np.array(dict_job_time_per_img_list[img])
            ))

            dict_job_time_per_img_sd[img] = float(np.std(
                np.array(dict_job_time_per_img_list[img])
            ))


            # -------- mturk --------
            dict_job_time_mturk_mean[img] = float(np.mean(
                np.array(dict_job_time_mturk_list[img])
            ))

            dict_job_time_mturk_sd[img] = float(np.std(
                np.array(dict_job_time_mturk_list[img])
            ))

        print('Done. Updating bulk-insert data dictionary...')

        ############################################
        # update bulk insert data
        # job time mean + sd; wq_job_time, wq_text
        ############################################

        for img_worker_pair, row in bulkInsertData_dict.items():

            row_img = row['IMG']
            row_workerid = row['WORKERID']

            x = bulkInsertData_dict[img_worker_pair]['JOB_TIME']
            mu = dict_job_time_mean[row_img]
            sigma = dict_job_time_sd[row_img]

            x_per_img = bulkInsertData_dict[img_worker_pair]['JOB_TIME_PER_IMG']
            mu_per_img = dict_job_time_per_img_mean[row_img]
            sigma_per_img = dict_job_time_per_img_sd[row_img]

            x_mturk = bulkInsertData_dict[img_worker_pair]['JOB_TIME_MTURK']
            mu_mturk = dict_job_time_mturk_mean[row_img]
            sigma_mturk = dict_job_time_mturk_sd[row_img]


            # ------- populating mean and std-dev times -------
            bulkInsertData_dict[img_worker_pair]['JOB_TIME_MEAN'] = mu
            bulkInsertData_dict[img_worker_pair]['JOB_TIME_SD'] = sigma

            bulkInsertData_dict[img_worker_pair]['JOB_TIME_PER_IMG_MEAN'] = mu_per_img
            bulkInsertData_dict[img_worker_pair]['JOB_TIME_PER_IMG_SD'] = sigma_per_img

            bulkInsertData_dict[img_worker_pair]['JOB_TIME_MTURK_MEAN'] = mu_mturk
            bulkInsertData_dict[img_worker_pair]['JOB_TIME_MTURK_SD'] = sigma_mturk


            # ------- popl worker quality: time outlier -------
            z_score = (x - mu) / sigma
            z_score_per_img = (x_per_img - mu_per_img) / sigma_per_img
            z_score_mturk = (x_mturk - mu_mturk) / sigma_mturk

            if abs(z_score) > WQ_JOB_TIME_THRESH or x < 0:
                bulkInsertData_dict[img_worker_pair]['WQ_JOB_TIME'] = 1
            else:
                bulkInsertData_dict[img_worker_pair]['WQ_JOB_TIME'] = 0


            if abs(z_score_per_img) > WQ_JOB_TIME_THRESH or x_per_img < 0:
                bulkInsertData_dict[img_worker_pair]['WQ_JOB_TIME_PER_IMG'] = 1
            else:
                bulkInsertData_dict[img_worker_pair]['WQ_JOB_TIME_PER_IMG'] = 0


            if abs(z_score_mturk) > WQ_JOB_TIME_THRESH or x_mturk < 0:
                bulkInsertData_dict[img_worker_pair]['WQ_JOB_TIME_MTURK'] = 1
            else:
                bulkInsertData_dict[img_worker_pair]['WQ_JOB_TIME_MTURK'] = 0


            # ------- popl worker quality: text-detection outlier -------
            tot_text_detect = dict_text_detect[row_img]
            curr_worker_text_detect = bulkInsertData_dict[img_worker_pair]['TEXT_DETECT']

            # if 4/5 workers have detected text, and current worker hasn't
            if tot_text_detect >= WQ_TEXT_THRESH and curr_worker_text_detect == 0:
                bulkInsertData_dict[img_worker_pair]['WQ_TEXT'] = 1
            else:
                bulkInsertData_dict[img_worker_pair]['WQ_TEXT'] = 0


            # ------- popl worker quality: image quality severe detection outlier -------
            tot_q_severe_detect = dict_q_severe_detect[row_img]

            curr_worker_q_severe_detect = 0

            if CANNED_TEXT_Q_SEVERE in bulkInsertData_dict[img_worker_pair]['IMG_CAPTION'].upper():
                curr_worker_q_severe_detect = 1

            # if 4/5 workers have said about severe quality issues (via canned text),
            # and current worker hasn't
            if tot_q_severe_detect >= WQ_Q_SEVERE_THRESH and curr_worker_q_severe_detect == 0:
                bulkInsertData_dict[img_worker_pair]['WQ_IMG_Q_SEVERE_4_5'] = 1
            else:
                bulkInsertData_dict[img_worker_pair]['WQ_IMG_Q_SEVERE_4_5'] = 0

            # if only current worker has said about severe quality issues (via canned text)
            if tot_q_severe_detect == 1 and curr_worker_q_severe_detect == 1:
                bulkInsertData_dict[img_worker_pair]['WQ_IMG_Q_SEVERE_1_5'] = 1
            else:
                bulkInsertData_dict[img_worker_pair]['WQ_IMG_Q_SEVERE_1_5'] = 0


            # ------- popl worker quality: spam: more than 50% images uses canned text -------
            canned_pct = dict_worker_canned_n[row_workerid] / dict_worker_img_n[row_workerid] * 100

            # if canned-text %age > 50 and current row has canned text
            if canned_pct >= SPAM_1_THRESH and curr_worker_q_severe_detect == 1:
                bulkInsertData_dict[img_worker_pair]['WQ_SPAM_1'] = 1
            else:
                bulkInsertData_dict[img_worker_pair]['WQ_SPAM_1'] = 0

        # ---- end update loop ----

        print('Done. Transforming bulk-insert data to list...')

        ###################
        # insert ALL rows
        ###################

        # 1a. prepare main insert list from dict
        for img_worker_pair, row in bulkInsertData_dict.items():

            bulkInsertData.append([
                row['IMG'],
                row['WORKERID'],
                row['Q_ISSUE_NONE'],
                row['Q_ISSUE_BLR'],
                row['Q_ISSUE_BRT'],
                row['Q_ISSUE_DRK'],
                row['Q_ISSUE_OBS'],
                row['Q_ISSUE_FRM'],
                row['Q_ISSUE_ROT'],
                row['Q_ISSUE_OTH'],
                row['OTH_ISSUE'],
                row['TEXT_DETECT'],
                row['IMG_CAPTION'],
                row['FINAL_ANGLE'],
                row['FINAL_ZOOM'],
                row['ASSIGNMENTID'],
                row['WORKER_DISP_SRL'],
                # row['WORKER_ENGLISH_LEVEL'],
                row['WORKER_RELATED_TO_BLIND'],
                float(round(row['JOB_TIME'], 4)),
                float(round(row['JOB_TIME_MEAN'], 4)),
                float(round(row['JOB_TIME_SD'], 4)),
                float(round(row['JOB_TIME_PER_IMG'], 4)),
                float(round(row['JOB_TIME_PER_IMG_MEAN'], 4)),
                float(round(row['JOB_TIME_PER_IMG_SD'], 4)),
                float(round(row['JOB_TIME_MTURK'], 4)),
                float(round(row['JOB_TIME_MTURK_MEAN'], 4)),
                float(round(row['JOB_TIME_MTURK_SD'], 4)),
                row['WQ_TEXT'],
                row['WQ_JOB_TIME'],
                row['WQ_JOB_TIME_PER_IMG'],
                row['WQ_JOB_TIME_MTURK'],
                row['WQ_CAPS'],
                row['WQ_IMG_QUALITY'],
                row['WQ_IMG_Q_SEVERE_4_5'],
                row['WQ_IMG_Q_SEVERE_1_5'],
                row['WQ_SPAM_1'],
                row['WQ_MANUAL_FLAG'],
                row['BATCH_NUM'],
            ])
        # ------ end list creation loop ----

        print('Done. Inserting bulk data...')

        # 1b. insert data
        insertResultsCur.executemany(insertResultsSql, bulkInsertData)

        # 2. insert comments
        insertCommentsCur.executemany(insertCommentsSql, bulkInsertComment)

        # 3. update raw
        updateRawCur.executemany(updateRawSql, bulkUpdateRaw)

        print('Done.')
        print('Processed: %5d / %5d  rows' % (rowCount, totRows))
        print('Inserted:  %5d  rows' % totRows)

        ###########
        # commit
        ###########
        conn.commit()
        print('FINISHED')

    finally:
        selectRawCur.close()
        updateRawCur.close()
        insertResultsCur.close()
        insertCommentsCur.close()

        conn.close()
        tunnel.stop()
        tunnel.close()