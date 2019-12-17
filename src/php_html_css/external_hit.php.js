/**
 * Created by IntelliJ IDEA.
 * User: Nilavra Bhattacharya
 * Date: 2018-04-05
 * Time: 1:57 AM
 */

$(document).ready(function()
{
    var form = $("form#mturk_form");

    //populate HIT_ST_TIME
    form.find('input[name=HIT_ST_TIME]').val(new Date().getTime()+'');

    var numTraining = $('section.training').length;

    var selectedColor = '#d9edf7';

    // enable tooltips
    //$('[data-toggle="tooltip"]').tooltip();

    // close details when close button clicked
    $('#hideDtl').click(function()
    {
        $('#dtlPane').collapse('hide');
    });

    // set cookie when details pane is hidden
    $('#dtlPane').on('hidden.bs.collapse', function ()
    {
        // as user has hidden details, set cookie to keep it hidden
        // so it never comes back within 30 mins
        var date = new Date(); var delay_mins = 30;
        date.setTime(date.getTime() + (delay_mins * 60 * 1000));
        document.cookie = "DtlHide=true; expires=" + date.toGMTString() + "; path=/";
    });


    // delete cookie when user clicks show details
    $('#showDtl').click(function()
    {
        $('#dtlPane').collapse('hide');
        // as user has shown details, delete cookie to keep it shown
        document.cookie = "DtlHide=true; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/";
    });








    // docs: https://github.com/rstaib/jquery-steps/wiki/Settings
    form.steps(
    {
        // ---------- Appearance ----------
        headerTag: "h3",
        bodyTag: "section",
        transitionEffect: "none",
        enableFinishButton: false,
        enableKeyNavigation: false,

        // ---------- Labels ----------
        labels: {
            finish: "Finish" //possible to change?
        },

        // ---------- Events ----------
        // Fires when the wizard is initialized
        onInit: function (event, currentIndex)
        {
            // load image controls
            loadImageTools(currentIndex);

            // copy text
            $('button.copy-text-btn').on('click', function()
            {
                //if(confirm('Are you sure?'))
                //{
                    var caption = 'Quality issues are too severe ' +
                        'to recognize visual content.';

                    var textarea = $(this).closest('div.caption-area').
                    find('textarea[name="IMG_CAPTION"]');

                    textarea.val(caption);
                //}

                $.notify({ message: 'Please use this shortcut wisely.' }, {
                    type: 'warning',
                    delay: 3000,
                    placement: { from: "bottom", align: "right" }
                });

            });


            // change cell background when checkbox is clicked
            $('.checkbox.ans_choice input[type=checkbox]').on('change nb_change', function()
            {
                if ($(this).prop("checked"))
                {
                    $(this).closest('div.checkbox.ans_choice')
                        .css('background', selectedColor);
                }
                else
                {
                    $(this).closest('div.checkbox.ans_choice')
                        .css('background', '#fff');
                }
            });

            // change cell background when radio is clicked
            $('.radio.ans_choice input[type=checkbox]').on('change', function()
            {
                if ($(this).prop("checked"))
                {
                    var checkbox = $(this);

                    //unset all radios
                    checkbox.closest('div.text_detect')
                        .find('.radio.ans_choice input[type=checkbox]')
                        .each(function()
                    {
                        $(this).prop("checked", false);

                        $(this).closest('div.radio.ans_choice')
                            .css('background', '#fff');
                    });

                    // set "this" radio
                    checkbox.prop("checked", true);

                    checkbox.closest('div.radio.ans_choice')
                        .css('background', selectedColor);
                }
            });

            // if "other" selected, focus textbox
            $('input[type=checkbox][value="OTH"]').on('change', function()
            {
                if ($(this).prop("checked"))
                {
                    $(this).closest('div.input-group')
                        .find('input[name="Q_ISSUE_OTH"]').focus();
                }
            });

            // if "other" TEXTBOX value changes, update other CHECKBOX
            $('input[name="Q_ISSUE_OTH"]').on('change keyup', function()
            {
                var val = $.trim($(this).val());
                var checkbox = $(this).closest('div.input-group')
                    .find('input[type=checkbox][value="OTH"]');

                //if non-empty, check checkbox + deselect "NO ISSUES" checkbox
                if(val)
                {
                    checkbox.prop("checked", true);

                    checkbox.closest('div.quality_issues')
                        .find('input[type=checkbox][name="Q_ISSUE"][value="NONE"]')
                        .prop("checked", false);
                }
                else
                {
                    //do not auto-select NO ISSUE checkbox
                    checkbox.prop("checked", false);
                }

                triggerCheckboxChange();
            });

            // if "NO ISSUE" selected, deselect all other checkboxes and empty OTH textbox
            $('input[type=checkbox][name="Q_ISSUE"][value="NONE"]').on('change', function()
            {
                if ($(this).prop("checked"))
                {
                    $(this).closest('div.quality_issues')
                        .find('input[type=checkbox][name="Q_ISSUE"][value!="NONE"]').each(function()
                    {
                        // inside loop, $(this) refers to checkboxes with value != 'NONE'
                        $(this).prop("checked", false);
                    });

                    triggerCheckboxChange();

                    $(this).closest('div.quality_issues')
                        .find('input[type=text][name="Q_ISSUE_OTH"]').val('');
                }
            });

            //if any other checkbox is selected, deselect NO ISSUE checkbox
            $('input[type=checkbox][name="Q_ISSUE"][value!="NONE"]').on('change', function()
            {
                if ($(this).prop("checked"))
                {
                    $(this).closest('div.quality_issues')
                        .find('input[type=checkbox][name="Q_ISSUE"][value="NONE"]')
                        .prop("checked", false);

                    triggerCheckboxChange();
                }
            });
        },

        onStepChanging: function (event, currentIndex, newIndex)
        {
            // Fires before the step changes
            // Always allow to go back even if current page is not valid
            if (newIndex < currentIndex)
                return true;

            return pageValidation(currentIndex, numTraining);
        },


        onStepChanged: function (event, currentIndex, priorIndex)
        {
            // load image controls
            loadImageTools(currentIndex);
        },


        onFinishing: function (event, currentIndex)
        {
            var result = pageValidation(currentIndex, numTraining);
            return result;
        },

        onFinished: function (event, currentIndex)
        {
            //alert("Submitted!");
        }

    });


    //on submit actions
    form.on('submit', function ()
    {
        var result = true;
        var errorMsg = '';

        // check if worker selected english level
        if(form.find('select[name=WORKER_ENGLISH_LEVEL]').val() === '-1')
        {
            result = false;
            errorMsg = errorMsg
                + 'Please indicate your English skill Level.<br/>';
        }


        if(!result)
        {
            $.notify({ message: errorMsg }, {
                type: 'danger',
                delay: 7000,
                placement: { from: "top", align: "center" }
            });

            $.notify({ message: errorMsg }, {
                type: 'danger',
                delay: 7000,
                placement: { from: "bottom", align: "center" }
            });
        }
        else
        {
            // if user types "<END>" in textbox / textarea, replace it appropriately
            form.find('input[type=text][name=Q_ISSUE_OTH]').each(function()
            {
                var val = $(this).val();
                var find = '<END>';
                var replace = encodeURIComponent(find);
                var newval = val.replace(find, replace);
                $(this).val(newval)
            });

            form.find('textarea[name=IMG_CAPTION]').each(function()
            {
                var val = $(this).val();
                var find = '<END>';
                var replace = encodeURIComponent(find);
                var newval = val.replace(find, replace);
                $(this).val(newval)
            });

            //escape the characters in feedback comments
            form.find('textarea[name=WORKER_COMMENTS]').each(function()
            {
                //your code here
                var val = $(this).val();
                var newval = encodeURIComponent(val);
                $(this).val(newval)
            });


            //populate HIT_END_TIME
            form.find('input[name=HIT_END_TIME]').val(new Date().getTime()+'');
        }

        return result;
    });

    //prevent ENTER key function, except on textarea
    $(document).on('keypress keydown keyup', ':input:not(textarea)', function(e)
    {
        if (e.keyCode === 13)
        {
            e.preventDefault();

            $.notify({ message: "Sorry! Submission by pressing ENTER key is disabled for this task." }, {
                type: 'warning',
                placement: { from: "bottom", align: "center" }
            });

            return false;
        }
    });



/*------------------------ pageValidation --------------------*/
    //common validation for all pages
    function pageValidation(currentIndex, numTraining)
    {
        var result = true;
        var errorMsg = '';
        var pgno = currentIndex - numTraining + 1;


        //-------------- actual TASK --------------
        if(currentIndex >= numTraining)
        {
            //current page
            //var currPg = $('form#mturk_form section[data-pgno='+ pgno +']');
            var currPg = $('form#mturk_form section:eq('+ currentIndex + ')');

            //////////////////////////////////////
            // Quality Issue validation
            //////////////////////////////////////
            if(!currPg.find('div.quality_issues input[type=checkbox]:checked').length)
            {
                result = false;
                errorMsg = errorMsg
                    + 'Please select (a) either at least one quality issue, or (b) no quality issue.<br/>';
            }

            // if "other selected
            if(currPg.find('div.quality_issues input[type=checkbox][value=OTH]:checked').length)
            {
                // and if other skill not entered
                if(!$.trim(currPg.find('input[type=text][name=Q_ISSUE_OTH]').val()).length)
                {
                    result = false;
                    errorMsg = errorMsg
                        + 'Please specify "other" quality issue.<br/>';
                    currPg.find('input[type=text][name=Q_ISSUE_OTH]').focus();
                }
            }

            //////////////////////////////
            // Text detection validation
            //////////////////////////////
            if(currPg.find('div.text_detect input[type=checkbox]:checked').length !== 1)
            {
                result = false;
                errorMsg = errorMsg
                    + 'Please select if there is any text in the image, or not.<br/>';
            }


            ////////////////////////////
            // Caption validation
            ////////////////////////////

            if (!$.trim(currPg.find('div.caption-area textarea[name="IMG_CAPTION"]').val()))
            {
                // textarea is empty or contains only white-space
                result = false;
                errorMsg = errorMsg
                    + 'Please enter a description for the image.<br/>';
            }
            else
            {
                var caption = $.trim(currPg.find('textarea[name="IMG_CAPTION"]').val());

                // URL:
                var numOfWords = caption
                                .replace(/^[\s,.;]+/, "")
                                .replace(/[\s,.;]+$/, "")
                                .split(/[\s,.;]+/).length;

                // caption contains less than 8 words (without punctuations)
                if(numOfWords < 8)
                {
                    result = false;
                    errorMsg = errorMsg
                        + 'Please use at least 8 words for the description.<br/>';
                }

                // https://stackoverflow.com/a/49142391/3263362
                // counting periods
                // var numSentences = caption
                //     .split('.') // split the sentences
                //     .filter(sentence => sentence !== '') // remove empty sentences
                //     .length;


                // caption contains more than one sentence (without punctuations)
                // but allow periods within numbers

                var regexp = /\.\s+/g;
                var numSentences = 1;

                if(caption.match(regexp)) {
                    numSentences = 1 + caption.match(regexp).length;
                    // console.log(caption.match(/\.\s+/g).length)
                }

                // console.log(numSentences);

                if(numSentences > 1)
                {
                    result = false;
                    errorMsg = errorMsg
                        + 'Please write the description as ONE SENTENCE.<br/>';
                }

                var caption_upper = caption.toUpperCase();

                // caption starts with "There is"
                if(    caption_upper.startsWith("THERE IS")
                    || caption_upper.startsWith("THERE ARE")
                    || caption_upper.startsWith("THIS IS")
                    || caption_upper.startsWith("THESE ARE")
                    || caption_upper.startsWith("THE IMAGE")
                    || caption_upper.startsWith("THE PICTURE")
                    || caption_upper.startsWith("THIS IMAGE")
                    || caption_upper.startsWith("THIS PICTURE")
                    || caption_upper.startsWith("IT IS")
                    || caption_upper.startsWith("IT'S")
                )
                {
                    result = false;
                    errorMsg = errorMsg +
                        'Please do not start the description with: '+
                        '<ul>' +
                            '<li>There is/are</li>' +
                            '<li>This is / There are</li>' +
                            '<li>The image / picture</li>' +
                            '<li>This image / picture</li>'+
                            '<li>It is / It\'s</li>'+
                        '</ul>' +
                        '<br/>';
                }
            }
        }

        if(result)
        {
            //populate IMG_END_TIME, if not already populated (i.e. first visit)
            if(currPg.find('input[name=IMG_END_TIME]').val() === '-999')
            {
                currPg.find('input[name=IMG_END_TIME]').val(new Date().getTime()+'');
            }
        }
        else
        {
            $.notify({ message: errorMsg }, {
                type: 'danger',
                delay: 7000,
                placement: { from: "top", align: "center" }
            });

            $.notify({ message: errorMsg }, {
                type: 'danger',
                delay: 7000,
                placement: { from: "bottom", align: "center" }
            });
        }

        return result;
    }




    /*------------------------ loadImageTools --------------------*/
    //oading image browsing tools
    function loadImageTools(currentIndex)
    {
        var currPg = $('form#mturk_form section:eq('+ currentIndex + ')');
        var currImgSrc = currPg.find('span.img_src').data('img_src');

        // photo zoom and rotate
        // docs: https://github.com/natashawylie/iviewer/wiki
        if(currPg.find('.image_wrap > .viewer').length === 1)
        {
            var iv = currPg.find('.image_wrap > .viewer').iviewer(
            {
                src: currImgSrc,
                zoom: 'fit',
                zoom_min: '1%'
            });

            iv.iviewer('center');
            iv.iviewer('fit');
            iv.iviewer('update');

            iv.bind('iviewerangle', function(ev, angle)
            {
                //change FINAL_ANGLE
                currPg.find('input[name="FINAL_ANGLE"]').val(angle.angle);
            });

            iv.bind('ivieweronafterzoom', function(ev, new_zoom)
            {
                //change FINAL_ZOOM
                currPg.find('input[name="FINAL_ZOOM"]').val(new_zoom.toFixed(4));
            });

            currPg.find('.iviewer_zoom_in').attr('title', 'Zoom in');
            currPg.find('.iviewer_zoom_out').attr('title', 'Zoom out');
            currPg.find('.iviewer_zoom_fit').attr('title', 'Fit the entire image into view');
            currPg.find('.iviewer_rotate_left').attr('title', 'Rotate left');
            currPg.find('.iviewer_rotate_right').attr('title', 'Rotate right');

            // currPg.find('.iviewer_zoom_status').attr('title', 'Fit the entire image.');
            // currPg.find('.iviewer_zoom_zero').attr('title', 'View image at original (100%) size');
            // console.log('loading tool');
        }

        //populate IMG_ST_TIME, if not already populated (i.e. first visit)
        if(currPg.find('input[name=IMG_ST_TIME]').val() === '-999')
        {
            currPg.find('input[name=IMG_ST_TIME]').val(new Date().getTime()+'');
        }






        // photo zoom
        /******
         $('.imgBox').imgZoom({
                boxWidth: 500,
                boxHeight: 350,
                marginLeft: 10
            });
         **********/
    }


    function triggerCheckboxChange(){
        $('.checkbox.ans_choice input[type=checkbox]').trigger('nb_change');
    }


});