
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

    retrieveAddress();

    function retrieveAddress() {
        var languages = ['fr', 'nl'],
            currLang = fms.currentMap.options.apiLang;

        $form.find('button, :submit').prop('disabled', true);
        $('#address-text').addClass('loading');

        fms.currentMap.getSelectedAddress(currLang, function(lang, response) {
            var address = response.result.address;
            $('#address-text').removeClass('loading');
            $form.find('.text-error').remove();

            if (!(address.street.postCode in zipcodes) || !zipcodes[String(address.street.postCode)].participation) {

                fillAdressField(lang, address);
                //This commune does not participate to fixmystreet until now.
                $form.prepend('<div class="text-error">' + zipcodes[String(address.street.postCode)].msg + '</div>');

            } else if(response.status == 'success') {

                $form.find('button, :submit').prop('disabled', false);

                fillAdressField(lang, address);

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

                for (var i in languages) {
                    if (languages[i] != currLang) {
                        fms.currentMap.getSelectedAddress(languages[i], function(lang, response) {
                            if(response.status == 'success') {
                                fillI18nAdressField(lang, address);
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

