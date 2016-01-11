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
    //$('#more_information_text').val(gettext("This is the initial text that needs to be defined. It's a suggestion for the gestionnaire. He can be edited as needed."))
}

//Following functions all seems deprecated. TODO : Remove in next version if no problem

///***************************************************************************/
///* refuseConfirmButton method is called when the user confirms his refusal */
///***************************************************************************/
//function refuseConfirmButton(){
//    window.location = URL_REPORT_REFUSE + '?more_info_text='+$('#more_information_text').val();
//}
//
///*************************************************************************/
///* refuseCancelButton method is called when the user cancels his refusal */
///*************************************************************************/
//function refuseCancelButton() {
//    $("#dialog").dialog('close');
//}


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

        var sending_type = $(this)[0].visibility.value;

        $.ajax({
            type: 'POST',
            url: URL_SEND_PDF,
            data: formData,
            success: function(response) {
                console.log("send mail success");
                if(sending_type == 'private'){
                  update_local_contacts(response.validRecipients);
                }
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

    //used for closing alerts message when sending PDF by mail
    $('.close_alert_pdf').click(function () {
      $(this).parent().addClass('hidden'); // hides alert with Bootstrap CSS3 implem
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

    $('#div-send-mail-pdf .collapse')
      .on('show', function () { $(this).parent().find('.accordion-heading a').addClass('open'); })
      .on('hide', function () { $(this).parent().find('.accordion-heading a').removeClass('open');         });

    //Animation to show the contact list when sending a PDF
    $("#div-send-mail-pdf").on("shown", function(){
        //if --> make sure you only the animation once (don't do it again it already opened, it's ugly).
        if($("#divDownloadPDFContactList").css("display") == "none"){
            $("#divDownloadPDFMain").animate({width:"475px"}, 100);
            $("#divDownloadPDFContactList").show();
        }
    });

    //Animation to hide the contact list when sending a PDF (all accordion submenu are closed)
    $("#div-send-mail-pdf").on("hidden", function(){
        var allAccordionAreClosed = $("#div-send-mail-pdf .accordion-body.in").length == 0;
        if(allAccordionAreClosed){
            $("#divDownloadPDFMain").animate({width:"100%"}, 100);
            $("#divDownloadPDFContactList").hide();
        }
    });

    $("#ulDownloadPDF li").on("click", function(){
      email_clicked($(this));
    });

    show_local_contacts();
});

function email_clicked(clicked_element){
    var clickedEmail = clicked_element.find(".contact_email").text();
    //email is the first textarea in the open accordion section (there is only 1 section open at any one time).
    var emailsToSend = $($("#div-send-mail-pdf .accordion-body.in form textarea").get(0)).val() || "";
    var array = emailsToSend.split(/,|;/);
    var emailInArray = false;
    for(var index in array){
        if(array[index].trim() == clickedEmail){
            emailInArray = true;
            break;
        }
    }
    if(!emailInArray) {
        if (emailsToSend.trim() != "" && !endsWith(emailsToSend.trim(), ',') && !endsWith(emailsToSend.trim(), ';')){
            emailsToSend += ",";
        }
        if (emailsToSend.trim().length > 0){
            emailsToSend += " ";
        }
        emailsToSend += clickedEmail;
        $($("#div-send-mail-pdf .accordion-body.in form textarea").get(0)).val(emailsToSend);
    }
}


function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

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

function show_local_contacts(local_contacts){
  if (local_contacts == null){
    local_contacts = get_local_contacts();
  }
  $('#local_contacts').html('');

  if(local_contacts.length == 0){
    $('#local_contacts').append('<p>' + gettext('No recent contact found') + '</p>');
  }
  else{
    var newul = $('#ulDownloadPDF').clone();
    newul.attr("id", "ulDownloadPDFLocal");
    newul.html('');

    var i = 0;
    for (contact in local_contacts){
      newul.append('<li><a><p class="contact_name">' + local_contacts[contact]['name'] + '</p><i class="icon-envelope"></i><p class="contact_email">' + local_contacts[contact]['email'] + '</p></a></li>');
      if(++i==10) break;
    }

    $('#local_contacts').append(newul);
    $("#ulDownloadPDFLocal li").on("click", function(){
      email_clicked($(this));
    });
  }
}

function get_local_contacts(){
  contacts = new Array();
  if(typeof(Storage) !== "undefined") {
    //Local storage might be old, we must refresh it
    contacts = save_local_contacts(JSON.parse(localStorage.getItem('local_contacts')));
  } else {
    contacts = new Array()
  }
  return contacts;
}

function save_local_contacts(contacts){
  var ordered_contacts = new Array();
  var contacts_to_keep = new Array();

  for (var c in contacts){
    var contact = contacts[c];
    var points = 0;

    var email_to_keep = new Array();
    for (var e in contact['emails']){
      if(date_diff_in_days(contact['emails'][e])<=60){
        points += 50/(Math.sqrt(date_diff_in_days(contact['emails'][e]))+1)
        email_to_keep.push(contact['emails'][e]);
      }
    }
    contact['emails'] = email_to_keep;
    points = Math.ceil(points);
    if(points > 0){
      if(null == contacts_to_keep[points]){
        contacts_to_keep[points] = new Array();
      }
      contacts_to_keep[points].push(contact);
    }
  }
  //ordering
  contacts_to_keep = contacts_to_keep.reverse();
  for (var c in contacts_to_keep){
    var contact =  contacts_to_keep[c];
    for (var i in contact){
      ordered_contacts.push(contact[i]);
    }
  }
  if (localStorage) {
    localStorage.setItem(
      'local_contacts',
      JSON.stringify(ordered_contacts)
    );
  }

  return ordered_contacts;
}

function update_local_contacts(valid_recipients){
  if (valid_recipients.length == 0){
    return true;
  }
  var local_contacts = get_local_contacts();
  var contacts = $('#ulDownloadPDF .contact_email');
  for(var r in valid_recipients){
    var found = false;
    for(var c in local_contacts){
      if(valid_recipients[r] == local_contacts[c]['email']){
        local_contacts[c]['emails'].push(jQuery.now());
        found = true;
        break;
      }
    }
    if(found){
      continue;
    }
    found = false;
    for(var c in contacts){
      if(valid_recipients[r] == contacts[c].textContent){
        found = true;
        break;
      }
    }
    if(!found){
      //create new local contact
      contact = {};
      contact['email'] = valid_recipients[r];
      contact['name'] = get_name_from_email(valid_recipients[r]);
      contact['emails'] = new Array();
      contact['emails'].push(jQuery.now());
      local_contacts.push(contact);
    }
  }

  show_local_contacts(save_local_contacts(local_contacts));
}

function get_name_from_email(email){
  return email.replace(/@.*$/i, "").replace(/[^a-z0-9]/i," ");;
}

function date_diff_in_days(date){
  return (jQuery.now() - date)/1000/60/60/24;
}
