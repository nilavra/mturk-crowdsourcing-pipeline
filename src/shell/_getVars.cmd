@echo off
set MTURK_PROJ_PATH="D:\CLOUD STORAGE\Box Sync\_PhD_PROJECTS\06 MAI\MTURK.EXP_01"

set MTURK_QSN=hit_exp_01.question
set MTURK_PRP=hit_exp_01.properties

set MTURK_QUAL_NAME=qual_MAI_custom_1
set MTURK_WORKER_LIST=workerlist.txt
set MTURK_REJECT_LIST=rejectlist.txt

rem b1:   100 image   =    20 HITs
rem b2:  1000 images  =   200 HITs
rem b3: 10000 images  =  2000 HITs
rem b4: 15000 images  =  3000 HITs

rem ------- TOGETHER ----
rem b5: 13386 images  =  2675 HITs
rem b6:    10 images  =  2 HITs

rem >>>>>>>>>>>> change these lines accordingly >>>>>>>>>>>>
rem set MTURK_LBL=hit_exp_01_b5
set MTURK_LBL=hit_exp_01_b5
rem test / live
set MTURK_MODE=live
rem <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<



