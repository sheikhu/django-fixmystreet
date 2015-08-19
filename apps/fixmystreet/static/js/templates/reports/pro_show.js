/******************************/
/* QUERY READY INITIALIZATION */
/******************************/
$(function(){
    var connected = true;

    // $("#dialog").dialog({
    //     modal: true,
    //     autoOpen:false,
    //     width:'auto',
    //     resizable: false
    // });

    /*******************************/
    /* When clicking any page form */
    /*******************************/
    $('form').submit(function(){
        if(!connected){
            evt.preventDefault();
        }
    });

    $('#map-bxl').hide();
});

/******************************************/
/* showMap is used to show the mpa widget */
/******************************************/
function showMap() {
    $("#map-bxl").toggle();
}


/****************************************************************************/
/* Refuse method is called when the gestionnaire decides to refuse a report */
/****************************************************************************/
function refuse(){
    $("#divRefuse").modal();
    $('#more_information_text').val(gettext("This is the initial text that needs to be defined. It's a suggestion for the gestionnaire. He can be edited as needed."))
}

/***************************************************************************/
/* refuseConfirmButton method is called when the user confirms his refusal */
/***************************************************************************/
function refuseConfirmButton(){
    window.location = URL_REPORT_REFUSE + '?more_info_text='+$('#more_information_text').val();
}

/*************************************************************************/
/* refuseCancelButton method is called when the user cancels his refusal */
/*************************************************************************/
function refuseCancelButton() {
    $("#dialog").dialog('close');
}


window.onload = function() {
    // Handle 'I want to create a new report' checkbox
    var createNewReport = document.getElementById('createNewReport');

    if (createNewReport) {
        messageButton.addEventListener('click', function() {
            if (createNewReport.checked) {
                window.location.href = "/";
            }
        });
    }
};

/**
 * ExifCallback method
 */
var someCallback = function(exifObject, index) {
    // realy used ???
    if (exifObject && exifObject.DateTimeOriginal){
        textAreas = $(".update_text").find('#imagedate');
        var datetosplit = exifObject.DateTimeOriginal;
        var splitted = datetosplit.split(/[:,\/ ]/)
        var pictureDate = new Date(splitted[0], splitted[1] -1, splitted[2], splitted[3], splitted[4], splitted[5], 0);
        textAreas[index].innerHTML = splitted[2] + '-' + splitted[1] + '-' + splitted[0] + " " +splitted[3] + ":" +splitted[4];
    }
};

function setStatusMessage(e, type, msg) {
    var $e = $(e);
    $e.html(msg);
    $e.parent().removeClass(function (index, css) { return (css.match(/\balert-\S+/g) || []).join(' '); })
        .addClass('alert-' + type);
}

$(document).ready(function() {

    function sendPdf(event) {
        event.preventDefault();

        this.classList.add('loading');

        var self = this;

        var statusMessage = document.getElementById(self.id + '-status');
        var status        = statusMessage.parentNode;

        var formData = $(this).serialize();
        if (!formData) {
            setStatusMessage(statusMessage, 'error', ERROR_MSG);
            return;
        }

        $.ajax({
            type: 'POST',
            url: URL_SEND_PDF,
            data: formData,
            success: function(response) {
                console.log("send mail success");
                var statusType = response.status == 'success' ? 'success' : 'error';
                var msg = '' + response.message;
                for (var i = 0; i < response.logMessages.length; i++) {
                    msg += '<br />' + response.logMessages[i];
                }
                setStatusMessage(statusMessage, statusType, msg);
                if(statusType=='success'){
                    var list = self.getElementsByTagName('textarea');
                    for (var i = 0; i<list.length; i++){
                        list[i].value='';
                    }
                }
            },
            error: function(response) {
                console.log("send mail error");
                setStatusMessage(statusMessage, 'error', gettext('Error'));
            },
            complete: function() {
                status.classList.remove('hidden');

                self.classList.remove('loading');
            }
        });
    }

    $('#mail-pdf-pro').submit(function(event) {
        sendPdf.call(this, event);
    });

    $('#mail-pdf-citizen').submit(function(event) {
        sendPdf.call(this, event);
    });

    $('.dropdown-menu li a').mouseover(function(evt) {
        evt.stopPropagation();

        var $this = $(this);
        $this.closest('li').siblings().each(function() {
            jQuery(this).removeClass('open');
        });
        $this.closest('li').addClass('open');
    });

    $('.dropdown-toggle').click(function(e) {
        jQuery(this).parent().find('li').each(function() {
            jQuery(this).removeClass('open');
        });
    });

});

$(function() {
    $(".changeStatus").delegate("input[type=radio]", "click", function () {
        var id = $(this).data('attachmentId');
        var level = $(this).val();
        var elem = $(this).closest('.changeStatus');
        elem.addClass('loading');
        $.get(URL_REPORT_UPDATE_ATTACHMENT + '?attachmentId=' + id + '&updateType=' + level)
            .success(function (result) {
                console.log(elem);
                elem.html(result);
            }).error(function () {
                alert("Somethings went wrong...");
            }).done(function () {
                elem.removeClass('loading');
            });
    });

//Clear the comment textarea after each POST
    $("#id_comment-text").val('');

    //Select report category
    $("#main_cat_select").val(REPORT_CAT_ID);

    //fill secondary cat based on main category
    $.ajax({
        url:URL_SEC_CAT_FOR_MAIN_CAT + "?main_category=" + REPORT_CAT_ID,
        type:"GET",
        success:function(data){
            sortAndAppendSecCat(data);
        }
    });

    //reset second category when main category changes
    $('#main_cat_select').change(function(){
        if(this.value !== "0"){
            $("#sec_cat_select").removeAttr("disabled");
            $("#sec_cat_select").empty();

            $.ajax({
                url:URL_SEC_CAT_FOR_MAIN_CAT + "?main_category=" +this.value,
                type:"GET",
                success:function(data){
                    sortAndAppendSecCat(data);
                }
            });
        }
        else {
            $("#sec_cat_select").attr("disabled","disabled");
        }
    });

    $(".update_text").find('#imgtoshow').exifLoad(someCallback);

    $('.priority select').change(function () {
        $("#prio_result").html(parseInt($("#id_probability").val()) * parseInt($("#id_gravity").val()));
    });

    $('#update_cat_form').submit(function(e){
        if(validateCategories()==false) {
            e.preventDefault();
        }
    });

    //value change on subscription
    $("#id_pro-subscription").change(function(){
        if($(this).attr("value")== "on"){
            $(this).attr("value","off");
            $.ajax(URL_UNSUBSCRIBE_PRO);
        }
        else{
            $(this).attr("value","on");
            $.ajax(URL_SUBSCRIBE_PRO);
        }
    });

    SetSubscribeCheckbox();
});

function SetSubscribeCheckbox(){
    if(SUBSCRIBED == "True"){
        $("#id_pro-subscription").attr("value","on").prop('checked', true);
    }else{
        $("#id_pro-subscription").attr("value","off");
    }
}