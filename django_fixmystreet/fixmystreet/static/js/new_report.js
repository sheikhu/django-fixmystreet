
$(document).ready(function() {

    var $form = $('#report-form');
    var $map = $('#map');

    function markerMoved (point) {
        $('#id_report-x').val(point.x);
        $('#id_report-y').val(point.y);

        window.location.assign('#x=' + point.x + '&y=' + point.y);

        retrieveAddress();

    }

    $map.one('markerdrag click movestart zoomend',function(evt,point){
        $('#cursor-instructions').fadeOut();
    });

    //On page load: The report overview needs to be hidden
    $('#report_overview_table_div').hide();
    $map.bind('markermoved',function(evt,point) {
        markerMoved(point);
    });

    $(fms.currentMap).bind('reportselected', function(evt, point, report){
        window.location.assign('/reports/' + report.id);
    });
});


function fillAdressField(lang, address) {
    $('#address-text').html(address.number + ' ' + address.street.name+ ' ' + address.street.postCode); // urbis must return the full text municipality
    $('#id_report-postalcode').val(address.street.postCode);
    $('#id_report-address_number').val(address.number);
}

function fillI18nAdressField(lang, address) {
    $('#id_report-address_' + lang).val(address.street.name);
}

function checkFileFieldValue(){
    if($("#id_file").val() == ""){
        alert("Please select a file to add.");
        return false;
    }
}

function retrieveAddress() {
    var languages = ['fr', 'nl'],
        currLang = LANGUAGE_CODE,
        $form = $('#report-form');

    $form.find('button, :submit').prop('disabled', true);
    $('#address-text').addClass('loading');

    fms.currentMap.getSelectedAddress(currLang, function(lang, response) {
        var address = response.result.address;
        $('#address-text').removeClass('loading');
        $form.find('.text-error').remove();

        if (typeof window.zipcodes != 'undefined' && address.street.postCode in zipcodes && !zipcodes[String(address.street.postCode)].participation) {

            fillAdressField(lang, address);
            //This commune does not participate to fixmystreet until now.
            $form.prepend('<div class="text-error span12">' + zipcodes[String(address.street.postCode)].msg + '</div>');

        } else if(response.status == 'success') {

            $form.find('button, :submit').prop('disabled', false);

            fillAdressField(currLang, address);
            fillI18nAdressField(currLang, address);

            //Search if the address is on a regional road or not.
            var pointX = $('#id_report-x').val();
            var pointY = $('#id_report-y').val();

            //Default False
            $('#id_report-address_regional').val('False');

            $.ajax({
                url: "http://gis.irisnet.be/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=urbis:URB_A_SS&maxFeatures=1&outputFormat=json&bbox="+(pointX-30)+","+(pointY-30)+","+(pointX+30)+","+(pointY+30),
                dataType: "json",
                type: "POST",
                success: function(responseData, textStatus, jqXHR) {
                    if (responseData.features[0].properties.ADMINISTRATOR != null) {
                        //ROUTE REGIONALE
                        $('#id_report-address_regional').val('True');
                    }
                }
            });

            //Does not work. Fill in the wrong input zone
            for (var i in languages) {
                if (languages[i] != currLang) {
                    fms.currentMap.getSelectedAddress(languages[i], function(langSecond, response) {
                        var address = response.result.address;
                        if(response.status == 'success') {
                            fillI18nAdressField(langSecond, address);
                        }
                    });
                }
            }

        } else {
            var msg = 'Error: ' + response.status;
            if(response.status == 'error') {
                msg = 'Unable to locate this address';
            }
            $('#address-text').removeClass('loading');
            $form.prepend('<p class="text-error">' + msg + '</p>');
        }
    });
}


/**
 * Create the overview popup content
 */
function createOverview(){
    var reportBody = $('#report-overview'),
        filesBody = $('#files-overview'),
        commentBody = $('#comment-overview');

    reportBody.empty();
    filesBody.empty();
    commentBody.empty();

    $("#report-form").find(".control-group").each(function(idx,val){
        reportBody.append($(val).find('label').clone());
        var input = $(val).find('select,input,textarea');

        if (input.length == 0) {
            reportBody.append($(val).find('.controls').clone());
        } else if (input.is("select")) {

            if(input.find(":selected").parent().is("optgroup")){
                reportBody.append("<i>"+input.find(":selected").parent().attr("label")+": </i>");
            }
            reportBody.append("<i>"+input.find(":selected").text()+'</i>');

        } else if (input.is("input")) {

            var type = input.attr("type");
            if(type != "hidden" && type != "file" && type != "checkbox") { // checkboxes are in label
                reportBody.append("<i>"+input.val()+"</i>");
            //} else if ($(value).attr("type")!="file") {
                //$("#validate_report_popup").find("[type='file']").hide();
            }

        //} else if (input.is("textarea")) {
            // comment, do nothing here
        }
        reportBody.find('checkbox').prop('disabled', true);
    });

    $("#form-files").children("div:not(#file-form-template)").each(function(idx,value){
        filesBody.append($(value).find("img").clone());
        filesBody.append("<i>"+$(value).find("textarea").val()+"</i>");
    });
    if (filesBody.children().length == 0) {
        filesBody.append("<i>-</i>");
    }

    commentBody.append("<i>"+$("#id_comment-text").val()+"</i>");
    if (commentBody.text().length == 0) {
        commentBody.append("<i>-</i>");
    }
    reportBody.find(".help-block").hide();
}