<?php
/**
 * Created by IntelliJ IDEA.
 * User: Nilavra Bhattacharya
 * Date: 2019-01-31
 * Time: 4:44 PM
 */

$config_path = "config.ini.php";
$config = parse_ini_file($config_path);

$db_file = $config['db_file'];
$db_host = $config['db_host'];
$db_name = $config['db_name'];
$db_user = $config['db_user'];
$db_pass = $config['db_pass'];


$title = "Describe the Image";

$img_repo_vizwiz = "https://url.to.img.repo/";
$img_repo_vizwiz_v2 = "https://url.to.img.repo/";
$img_repo_vqa = "https://url.to.img.repo/";

$form_action = "https://www.mturk.com/mturk/externalSubmit";
$disabled = "";
$submit_btn_text = "Submit Your Work";


// VQA params
$img_list  = test_input(urldecode($_GET['img_list']));


// MTurk HIT params
$assignmentId = $_GET['assignmentId'];
$hitId = $_GET['hitId'];
$turkSubmitTo = $_GET['turkSubmitTo'];
$workerId = $_GET['workerId'];


try
{
    #$conn = new PDO($db_file);
    $conn = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_pass);
    // set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    //preparing CSV (a,b,c,d) to be put in SQL: "where IMG in (a,b,c,d)"
    $sql_where_in_clause = str_replace("|","', '", "'" . $img_list . "'");

    // order by random() shuffles resultset to prevent learning effect
    $sql =  "select * from MAI_ImgCaption.DATASET_VIZWIZ where IMG in (" . $sql_where_in_clause . ") order by rand()" ;

    // result set
    $rs = $conn->query($sql);



// Check if the worker is PREVIEWING the HIT or if they've ACCEPTED the HIT
    if($assignmentId == "ASSIGNMENT_ID_NOT_AVAILABLE") // Preview Mode
    {
        // If we're previewing, disable the button and give it a helpful message
        $disabled = "disabled";
        $submit_btn_text = "Please ACCEPT the HIT to submit.";
    }
    else if(!empty($_SERVER['HTTP_REFERER']) && stripos($_SERVER['HTTP_REFERER'],"workersandbox") > 0) // Sandbox Mode
    {
        $form_action = "https://workersandbox.mturk.com/mturk/externalSubmit";
    }



    $showDtl = "";

// if cookie not set (i.e. user never clicked "hide"),
// show details
    if(!isset($_COOKIE["DtlHide"]))
    {
        $showDtl = "in";
    }

    $slug = round(microtime(true) * 1000);

    ?>

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="./css/bootstrap.min.css">

        <!-- animate CSS -->
        <link rel="stylesheet" href="./css/animate.css"/>

        <!-- jQuery steps CSS -->
        <link rel="stylesheet" href="./css/jquery.steps.css"/>

        <!-- font awesome -->
        <!--link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.1/css/all.css"
              integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr"
              crossorigin="anonymous"-->

        <!-- image zoom and rotate -->
        <link rel="stylesheet" href="./css/jquery.iviewer.css"/>

        <!-- Custom CSS -->
        <link rel="stylesheet" href="external_hit.php.css?t=<?=$slug?>"/>

        <!-- jQuery 3.2.1 does not work with zoom -->
        <!--script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"></script-->

        <!--script src="https://code.jquery.com/jquery-1.12.4.min.js"></script-->

        <script src="./js/jquery.min.js"></script>
        <script src="./js/bootstrap.min.js"></script>

        <!-- notify (warning) -->
        <script src="./js/bootstrap-notify.min.js"></script>

        <!-- image zoom -->
        <!--script src="./js/jquery.imgzoom.js"></script-->
        <!--script src="./js/jquery.zoom.js"></script-->



        <!-- jQuery steps -->
        <script src="./js/jquery.steps.js"></script>

        <!-- jQuery rotate -->
        <!--script src="./js/jQueryRotate.js"></script-->


        <!-- image zoom and rotate -->
        <!-- docs: https://github.com/natashawylie/iviewer/wiki -->
        <!--script type="text/javascript" src="./js/jqueryui.js" ></script-->
        <script type="text/javascript" src="./js/jquery-ui.min.js" ></script>
        <script type="text/javascript" src="./js/jquery.mousewheel.min.js" ></script>
        <script type="text/javascript" src="./js/jquery.iviewer.js" ></script>

        <!-- modal wrapper -->
        <!--script src="./js/bootstrap.modal.wrapper.js"></script-->

        <!-- unique turker: http://uniqueturker.myleott.com/ -->
        <!---- Max # HITs / worker: 2 ---->
        <!--script src="//uniqueturker.myleott.com/lib.js" type="text/javascript"></script>
        <script type="text/javascript">
            (function(){
                var ut_id = "cf7cf99f8b337c9d757b2b6d4217a6d5";
                if (UTWorkerLimitReached(ut_id)) {
                    document.getElementById('mturk_form').style.display = 'none';
                    document.getElementsByTagName('body')[0].innerHTML =
                        "You have already completed the " +
                        "maximum number of HITs allowed " +
                        "by this requester. " +
                        "Please click 'Return HIT' to avoid " +
                        "any impact on your approval rating.";
                }
            })();
        </script-->

        <!---- Max # HITs / worker: 1 ---->
        <script src="//uniqueturker.myleott.com/lib.js" type="text/javascript"></script>
        <script type="text/javascript">
            (function(){
                var ut_id = "4361dcfba8f0a892d8610f2a5e6d65d0";
                if (UTWorkerLimitReached(ut_id)) {
                    document.getElementById('mturk_form').style.display = 'none';
                    document.getElementsByTagName('body')[0].innerHTML =
                        "You have already completed the " +
                        "maximum number of HITs allowed " +
                        "by this requester. " +
                        "Please click 'Return HIT' to avoid " +
                        "any impact on your approval rating.";
                }
            })();
        </script>



        <!-- Custom JS -->
        <script src="external_hit.php.js?t=<?=$slug?>"></script>


        <title><?=$title?></title>
    </head>
    <body>


    <div class="container-fluid" style="padding: 0 7%">

        <!---------- header area ------------>
        <div class="row">
            <div class="col-lg-12">
                <!--h3 style="text-align: center"><?=$title?></h3-->
                <br/>
                <!-- Button open collapse -->
                <button type="button" id="showDtl"
                        data-toggle="collapse" data-target="#dtlPane"
                        class="btn btn-default btn-sm center-block" >
                    Hide / Show Details
                </button>

                <!-- task details -->
                <div class="collapse <?=$showDtl?>" id="dtlPane">
                    <div class="alert alert-warning motivation">

                        <p>
                            <strong>Motivation:</strong>
                            Your work will help to build smart systems that can automatically
                            describe our visual world to people who are blind.
                        </p>


                        <p>
                            <strong>We ask you to:</strong>
                            carefully review images taken by people who are blind, and then
                            (1) describe the image as per the instructions,
                            (2) say if there is any text in the image, and
                            (3) select what (if anything) is wrong with the photographic
                                quality of the image.

                        </p>


                        <p>
                            PLEASE NOTE: It is possible that some images could be meaningless,
                            inappropriate, or offensive.
                            This is because we cannot control what pictures are taken.
                            Kindly use your best judgement for this task.
                        </p>

                        <p>
                            IMPORTANT: Please do not refresh the webpage once you have started
                            working, as you will lose all your progress, and have to start at the beginning.
                        </p>


                        <button id="hideDtl" type="button" class="btn btn-warning btn-sm center-block">
                            Hide
                        </button>

                        <small style="display: block; text-align: center; font-size: 13px; margin-top: 5px; font-style: italic">
                            You can see this information anytime by clicking "Hide / Show Details" button above.
                        </small>
                    </div>

                </div>

            </div>
        </div>





        <div class="row">
            <div class="col-sm-offset-2 col-sm-8">

                <div class="well well-sm" style="padding: 1px 5px 0px 20px; margin-top: 10px;">

                    <h4 style="margin-bottom: 5px; font-weight: bold; font-size: 16px;">
                        Instructions:
                    </h4>

                    <ol start="0" class="ins-steps" style="padding-left: 18px;">
                        <li class="ins">
                            Please review the image. You may adjust your view using the toolbar:

                            <ul style="padding-left: 25px;">
                                <li>
                                    Use the <strong>+</strong> and <strong> - </strong> buttons (or your mousewheel)
                                    to <strong><u>zoom in</u></strong> or <strong><u>zoom out</u></strong>.
                                </li>
                                <li>
                                    Click and drag on the zoomed image to <strong><u>pan around</u></strong>.
                                </li>
                                <li>
                                    If needed, <strong><u>rotate</u></strong> the image using the last two buttons on the toolbar.
                                </li>
                            </ul>

                        </li>

                        <li class="ins">
                            Please describe the image as per the given prompts.
                        </li>


                        <li class="ins">
                            Please indicate whether the image contains any form of text.
                            Partial texts should also be reported.
                        </li>


                        <li class="ins">
                            Please select what are the photographic <strong><u>quality issue(s)</u></strong> in the image.

                            <ul style="padding-left: 25px;">
                                <li class="text-danger">
                                    You may select more than one issue, or the "no issues" option.
                                </li>
                            </ul>

                        </li>




                    </ol>
                </div>


            </div>
        </div>



        <div class="row">

            <!---------- form ------------>
            <div class="col-lg-12 ">

                <form id="mturk_form" method="POST" action="<?=$form_action?>">

                    <input type="hidden" id="assignmentId" name="assignmentId" value="<?=$assignmentId?>">

                    <input type="hidden" name="HIT_ST_TIME" value="">
                    <input type="hidden" name="HIT_END_TIME" value="">


                    <!-- insert training section here -->


<?php
$pg_no = 0;
while($row = $rs->fetch( \PDO::FETCH_ASSOC ))
{
    $pg_no++;

    $img   = $row['IMG'];

    /***
     * the use of !== false is deliberate; strpos() returns
     * either the offset at which the needle string begins
     * in the haystack string, or the boolean false if the
     * needle isn't found. Since 0 is a valid offset and 0 is
     * "falsey", we can't use simpler constructs like !strpos($a, 'are')
     */
    if (strpos($img, 'VizWiz_v2_') !== false)
    {
        $img_src = $img_repo_vizwiz_v2 . $img;
    }
    elseif (strpos($img, 'VizWiz_') !== false)
    {
        $img_src = $img_repo_vizwiz . $img;
    }
    elseif (strpos($img, 'COCO_') !== false)
    {
        $img_src = $img_repo_vqa . $img;
    }


    ?>

                        <!-------- Page: <?=$pg_no?> -------->
                        <h3>Image <?=$pg_no?> </h3>

                        <section id="<?=$img?>" data-pgno="<?=$pg_no?>">

                            <!--hr style="border-top: 2px solid #eee; margin: 10px 0px 10px 0px;"/-->

                            <!-- v imp: will determine which VQ was in this current page -->
                            <input type="hidden" name="IMG" value="<?=$img?>">

                            <!-- image start and end times -->
                            <input type="hidden" name="IMG_ST_TIME" value="-999">
                            <input type="hidden" name="IMG_END_TIME" value="-999">


                            <!-------- main content ---------->
                            <div class="row">

                                <!------- image column ------->
                                <div class="col-sm-6">

                                    <!---------- Image ---------->
                                    <div class="image_wrap" style="overflow: hidden">

                                        <div class="viewer" style="
                                            height: 1000px;
                                            width: 100%;
                                            border: 1px solid black;
                                            position: relative;
                                        "></div>

                                        <span class="img_src" data-img_src="<?=$img_src?>"></span>

                                    </div>
                                </div>

                                <!----------- all tasks column ----------->
                                <div class="col-sm-6">


                                    <!----------  Step: Image Caption ------------>
                                    <div class="row border-around caption-area" style="">

                                        <div class="col-lg-12">
                                            <h4 style="
                                                text-align: center;
                                                font-weight: bold;
                                                border-bottom: 2px solid #ddd;
                                                padding: 5px;
                                                margin: 0px 0px 15px;
                                            ">
                                                Step 1: Please describe the image in one sentence.
                                            </h4>
                                        </div>


                                        <!----------  Caption Instructions ------------>
                                        <div class="col-sm-12" style="padding-right: 0px">

                                            <div class="instructions">


                                                <ul style="font-size: 16px; padding: 0px 10px 0px 25px">

                                                    <li>
                                                        Describe all parts of the image that may be
                                                        <span style="color: blue">
                                                            <strong>
                                                                important to a person who is blind.
                                                            </strong>
                                                        </span>
                                                        <br/>
                                                        <em>
                                                            E.g., imagine how you would describe this
                                                            image on the phone to a friend.
                                                        </em>
                                                    </li>



                                                    <!--li>
                                                        <span style="color: red">Do not</span>
                                                        start sentence(s) with "There is/are".
                                                    </li-->

                                                    <!--li>
                                                        <span style="color: red">Do not</span>
                                                        describe unimportant details.
                                                    </li-->

                                                    <li>
                                                        <span style="color: red">
                                                            <strong>DO NOT</strong>
                                                        </span>
                                                        speculate about what people in the image
                                                        might be saying or thinking.
                                                    </li>


                                                    <!--li>
                                                        <span style="color: red">Do not</span>
                                                        invent proper names for people.
                                                    </li-->


                                                    <li>
                                                        <span style="color: red">
                                                            <strong>DO NOT</strong>
                                                        </span>
                                                        describe things that may have happened in the
                                                        future or past.
                                                    </li>



                                                    <li>
                                                        <span style="color: red">
                                                            <strong>DO NOT</strong>
                                                        </span>
                                                        use more than one sentence.
                                                    </li>


                                                    <li>
                                                        <!----------
                                                        <span style="color: red">
                                                            <strong>DO NOT</strong>
                                                        </span>
                                                        write out the text in the image.
                                                        This will be captured based on your
                                                        response to Step 2 (via automated methods).
                                                        <!--If the text is an important part of the image,
                                                        you can summarize the content of the text.->
                                                        ---------->
                                                        If text is in the image, and is important, then you can
                                                        summarize what it says.
                                                        <br/>
                                                        <span style="color: red">
                                                            <strong>DO NOT</strong>
                                                        </span>
                                                        use all the specific phrases that you see in the image
                                                        as your description of the image.
                                                    </li>


                                                    <!--li>
                                                        If the image quality issues make it
                                                        <strong>
                                                            impossible to recognize the visual content
                                                        </strong>
                                                        (e.g., image is totally black or white),
                                                        then use the following description (you can copy-paste):
                                                    </li-->

                                                    <li>
                                                        <span style="color: red">
                                                            <strong>DO NOT</strong>
                                                        </span>
                                                        describe the image quality issues.
                                                        This is covered in Step 3.

                                                        <br/>

                                                        If the image quality issues make it
                                                        <strong>
                                                            impossible to recognize the visual content
                                                        </strong>
                                                        (e.g., image is totally black or white),
                                                        then use the following description (you can copy-paste):
                                                    </li>

                                                    <div class="well well-sm" style="
                                                            padding: 6px 10px;
                                                            margin: 8px 15px 8px 0px;
                                                        ">

                                                        Quality issues are too severe to recognize visual content.

                                                        &nbsp;

                                                        <button type="button" class="btn btn-default btn-xs copy-text-btn">
                                                            Copy to description
                                                        </button>
                                                    </div>


                                                    <li>
                                                        Your description should contain at least
                                                        <span style="color: blue"><strong>8 words</strong></span>.
                                                    </li>

                                                </ul>


                                                <!--div class="well well-sm" style="
                                                            padding: 6px 10px;
                                                            margin: 8px 15px 8px 0px;
                                                        ">

                                                    The image quality issues are too
                                                    severe to recognize the visual content.

                                                    &nbsp;

                                                    <button type="button" class="btn btn-default btn-xs copy-text-btn">
                                                        Copy to description
                                                    </button>
                                                </div-->

                                            </div>

                                        </div>


                                        <!----- caption area --->
                                        <div class="col-sm-12" style="">

                                            <textarea name="IMG_CAPTION"
                                                      placeholder="Type here. Do not start the description with:
 - &quot;There is/are ...&quot;
 - &quot;This is / These are ...&quot;
 - &quot;The/This image/picture ...&quot;
 - &quot;It is/ It's ...&quot;
                                                      "
                                                      style="font-size:18px"
                                                      class="form-control input-lg" rows="5"></textarea>

                                        </div>

                                    </div><!----------  Step: Image Caption ------------>




                                    <!----------  Step: Text Detection ------------>
                                    <div class="row">
                                        <div class="col-lg-12 text_detect border-around" style="margin-top: 30px;">

                                            <table class="ansChoices table table-condensed"
                                                   style="">
                                                <thead>
                                                <tr>
                                                    <th colspan="4" class="text-center" style="">
                                                        <h4 style="font-weight: bold; margin: 2px auto">
                                                            Step 2: Is there any text in the image?
                                                        </h4>

                                                    </th>
                                                </tr>
                                                </thead>

                                                <tbody>
                                                <tr>
                                                    <!-- Col 1 -->
                                                    <td style="width: 50%; padding-left: 0px">

                                                        <div class="radio ans_choice pull-right">
                                                            <label>
                                                                <input name="TEXT_DETECT" type="checkbox" value="Y">
                                                                <strong>YES:</strong>
                                                                The image contains text.
                                                            </label>
                                                        </div>
                                                    </td>

                                                    <!-- Col 2 -->
                                                    <td style="width: 50%; padding-right: 0px">

                                                        <div class="radio ans_choice pull-left">
                                                            <label>
                                                                <input name="TEXT_DETECT" type="checkbox" value="N">
                                                                <strong>NO:</strong>
                                                                The image has no text.
                                                            </label>
                                                        </div>
                                                    </td>
                                                </tr>
                                                </tbody>
                                            </table>

                                        </div>

                                    </div><!----------  Step: Text Detection ------------>


                                    <!---------- Step: Quality Issues ---------->
                                    <div class="row">

                                        <div class="col-sm-12 quality_issues border-around" style="margin-top: 30px;">

                                            <table class="ansChoices table table-condensed" style="">
                                                <thead>
                                                <tr>
                                                    <th colspan="4" class="text-center" style="">
                                                        <h4 style="font-weight: bold; margin: 2px auto">
                                                            Step 3: What are the quality issues in the image?
                                                        </h4>

                                                    </th>
                                                </tr>
                                                </thead>

                                                <tbody>
                                                <tr>
                                                    <!-- Col 1 -->
                                                    <td style="width: 32%; padding-left: 0px">

                                                        <div class="checkbox ans_choice">
                                                            <label>
                                                                <input name="Q_ISSUE" type="checkbox" value="BLR">
                                                                <strong>BLUR:</strong>
                                                                Is the image blurry?
                                                            </label>
                                                        </div>

                                                        <div class="checkbox ans_choice">
                                                            <label>
                                                                <input name="Q_ISSUE" type="checkbox" value="OBS">
                                                                <strong>OBSTRUCTION:</strong>
                                                                Is the scene obscured by the photographer's finger
                                                                over the lens, or another unintended object?
                                                            </label>
                                                        </div>

                                                    </td>

                                                    <!-- Col 2 -->
                                                    <td style="width: 34%">

                                                        <div class="checkbox ans_choice">
                                                            <label>
                                                                <input name="Q_ISSUE" type="checkbox" value="BRT">
                                                                <strong>BRIGHT:</strong>
                                                                Is the image too bright
                                                                (e.g., light is directly
                                                                behind the object)?
                                                            </label>
                                                        </div>

                                                        <div class="checkbox ans_choice">
                                                            <label>
                                                                <input name="Q_ISSUE" type="checkbox" value="FRM">
                                                                <strong>FRAMING:</strong>
                                                                Are parts of necessary items
                                                                missing from the image?
                                                            </label>
                                                        </div>


                                                    </td>


                                                    <!-- Col 3 -->
                                                    <td style="width: 31%; padding-right: 0px">


                                                        <div class="checkbox ans_choice">
                                                            <label>
                                                                <input name="Q_ISSUE" type="checkbox" value="DRK">
                                                                <strong>DARK:</strong>
                                                                Is the image too dark
                                                                (e.g., poor lighting in a room)?
                                                            </label>
                                                        </div>



                                                        <div class="checkbox ans_choice">
                                                            <label>
                                                                <input name="Q_ISSUE" type="checkbox" value="ROT">
                                                                <strong>ROTATION:</strong>
                                                                Does the image need to be rotated
                                                                for proper viewing?
                                                            </label>
                                                        </div>
                                                    </td>


                                                </tr>
                                                </tbody>
                                            </table>

                                            <div class="row">
                                                <div class="col-lg-12">

                                                    <div class="input-group ">
                                                        <span class="input-group-addon">
                                                            <div class="checkbox" style="margin-top: 0px; margin-bottom: 0px;">
                                                                <label style="margin-top: 0px; margin-bottom: 0px;">
                                                                    <input name="Q_ISSUE" type="checkbox" value="OTH">
                                                                    Any other issues:
                                                                </label>
                                                            </div>
                                                        </span>
                                                        <input name="Q_ISSUE_OTH" type="text"
                                                               placeholder="anything else not covered above"
                                                               title="Name any image quality issues not covered above"
                                                               class="form-control">
                                                    </div>

                                                    <p style="text-align: center; font-weight: bold;
                                                            margin: 10px 0px; font-size: 18px;">
                                                        OR
                                                    </p>

                                                    <div class="checkbox ans_choice"
                                                         style="width: 85%; margin: 0 auto; text-align: center">
                                                        <label>
                                                            <input name="Q_ISSUE" type="checkbox" value="NONE">
                                                            <strong>NO ISSUES:</strong>
                                                            There are no quality issues in the image.
                                                        </label>
                                                    </div>

                                                </div>
                                            </div>

                                        </div>
                                    </div> <!---------- Step: Quality Issues ---------->






                                </div>
                                <!--- end all tasks column --->

                            </div>



                            <input type="hidden" name="FINAL_ANGLE" value="0">
                            <input type="hidden" name="FINAL_ZOOM" value="100">


                            <!-- v imp: delimeter between multiple answers -->
                            <input type="hidden" name="Q_ISSUE" value="<END>">
                            <input type="hidden" name="Q_ISSUE_OTH" value="<END>">
                            <input type="hidden" name="TEXT_DETECT" value="<END>">
                            <input type="hidden" name="IMG_CAPTION" value="<END>">


                            <hr style="border-top: 2px solid #eee; margin: 10px 0px 10px 0px;"/>

                        </section>




<?php
}
?>


                    <h3>Finish</h3>
                    <section class="finish">
                        <div class="row">
                            <div class="col-sm-offset-1 col-sm-10">

                                <label class="h4" style="margin-bottom: 5px; margin-top: 25px; font-weight: bold">
                                    <!--Please indicate your English skill level:
                                    <!--span class="text-danger">(mandatory)</span-->

                                    <!--Is English your native language?-->
                                    Do you have close friends or family who are blind
                                    who you describe visual things to?
                                    <br/>
                                    <small>
                                        Your response will not affect the approval or rejection of your work.
                                    </small>
                                </label>


                                <div class="row">

                                    <div class="col-sm-5">

                                        <!--select name="WORKER_ENGLISH_LEVEL" class="form-control input-lg">
                                            <option value="-1">Please select...</option>
                                            <option value="0">A1 - Beginner</option>
                                            <option value="1">A2 - Elementary</option>
                                            <option value="2">B1 - Intermediate</option>
                                            <option value="3">B2 - Upper Intermediate</option>
                                            <option value="4">C1 - Advanced</option>
                                            <option value="5">C2 - Proficient</option>
                                        </select-->

                                        <!--select name="WORKER_ENGLISH_LEVEL" class="form-control input-lg"-->
                                        <select name="WORKER_RELATED_TO_BLIND" class="form-control input-lg">
                                            <option value="-1">Please select...</option>
                                            <option value="1">Yes</option>
                                            <option value="0">No</option>
                                        </select>


                                    </div>


                                    <!--div class="col-sm-6">
                                        <!-- https://www.bellenglish.com/useful-information/english-language-level-chart ->
                                        <img src="english_levels.png?t=<?=$slug?>" class="img-responsive">
                                    </div-->

                                </div>




                                <br/>
                                <br/>

                                <label style="margin-bottom: 5px">
                                    Do you have any suggestions, feedback, or general comments for us?
                                    <span class="text-muted">(optional)</span>
                                </label>

                                <textarea name="WORKER_COMMENTS" class="form-control" rows="4"></textarea>

                                <button type="submit" <?=$disabled?>
                                        class="btn btn-lg btn-success btn-block center-block"
                                        id="submitBtn"
                                >
                                    <?=$submit_btn_text?>
                                </button>

                                <h2 style="text-align: center; margin-bottom: 50px">
                                    Thank you so much for completing this task!
                                    <br/>
                                    <small>
                                        Your valuable work will go a long way in helping to describe scenes
                                        from our visual world to people who are blind.
                                    </small>
                                </h2>

                            </div>
                        </div>
                    </section>

                </form>
            </div>
        </div>


        <br/>



    </div>

    </body>
    </html>

    <?php
}
    /*catch(PDOException $e)
    {
        echo "Database error occurred: " . $e->getMessage();
    }*/
catch (Exception $e)
{
    echo "Exception occured: " . $e->getMessage();
}
finally
{
    $conn = null;
}

function test_input($data) {
    $data = trim($data);
    $data = stripslashes($data);
    $data = htmlspecialchars($data);
    return $data;
}

function IsNullOrEmptyString($str){
    return (!isset($str) || trim($str)==='');
}
?>