
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
    $('#address-text').html(address.number + ' ' + address.street.name+ ', ' + address.street.postCode + " " + zipcodes[address.street.postCode].commune); // urbis must return the full text municipality
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

            $('#phone').html(zipcodes[String(address.street.postCode)].phone)

            //This commune does not participate to fixmystreet until now.
            $('#nonparticipatingcommune').modal();
            $('#address-text').after('<p class="text-error">' + $('#nonparticipatingcommune .modal-body p').html() + '</p>');

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

    $("#report-form").find("fieldset").each(function(idx,fieldset){
        reportBody = $('#report-overview')
        reportBody.append("<div id="+idx+" class='bordered-box'>");
        reportBody = $("#"+idx);
        reportBody.append($("<h4/>").text($(fieldset).find('legend').text()));
        $(fieldset).find(".control-group").each(function(idx, control){

            if ($(control).find('label').text()) {
                console.log($(control).find('label').text());
                reportBody.append($("<strong/>").text($(control).find('label').text() + " "));
                // reportBody.append();
            }

            var input = $(control).find('select,input,textarea');

            if (input.length == 0) {
                if($(control).find("span").length != 0){
                    reportBody.append("<br>").append($(control).find("span").clone());
                }
                else{
                    reportBody.append($(control).find('div').children().clone().text());
                }
            } else if (input.is("select")) {

                if(input.find(":selected").parent().is("optgroup")){
                    reportBody.append(overviewLine(input.find(":selected").parent().attr("label")+"/"));
                }
                reportBody.append(overviewLine(input.find(":selected").text()));

            } else if (input.is(":file")) {
                if(control.id == "file-form-template") {
                    if (reportBody.find("img").length == 0) {
                        reportBody.append(overviewLine());
                    } else {
                        return; // continue, do not insert <br/>
                    }
                } else {
                    reportBody.append($(control).find("img").clone().css({'float': 'left'}));
                    reportBody.append(overviewLine($(control).find("textarea").val()));
                }

            } else if (input.is(":checkbox")) {
                reportBody.append(overviewLine(input.clone().prop('disabled', true)));
            } else if (input.is("input")) {

                if(input.attr("type") != "hidden") {
                    reportBody.append(overviewLine(input.val()));
                }

            } else if (input.is("textarea")) {
                reportBody.append(overviewLine(input.val()));
            }
            reportBody.append("</div>");
            reportBody.append("<br style='clear: left;'/>");
        });
    });
    reportBody.find(".help-block").hide();
}

function overviewLine(value) {
    // return $("<i/>").append(value || "-");
    return value || "-";
}
