
$(document).ready(function() {
    $.urlParam = function(name){
        var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
        return results[1] || 0;
    }

    var x = $.urlParam('x');
    var y = $.urlParam('y');

    getAddressFromPoint('fr', x, y);
    getAddressFromPoint('nl', x, y);
});

function getAddressFromPoint(lang, x, y) {
    var self = this;
    $.ajax({
        url: 'http://service.gis.irisnet.be/urbis/Rest/Localize/getaddressfromxy',
        type:'POST',
        dataType:'jsonp',
        data: {
            json: ['{',
                '"language": "' + lang + '",',
                '"point":{x:' + x + ',y:' + y + '}',
                '}'].join('\n')
        },
        success:function(response)
        {
            if (lang == LANGUAGE_CODE) {
                fillAdressField(response.result.address);
            }
            fillI18nAdressField(lang, response.result.address);
        },
        error:function(response)
        {
            // Error
            var msg = 'Error: ' + response.status;
            if(response.status == 'error') {
                msg = 'Unable to locate this address';
            }
            $('#address-text').html(msg);
        }
    });
}
function fillAdressField(address) {
    $('#address-text').html(address.number + ' ' + address.street.name+ ', ' + address.street.postCode + " " + zipcodes[address.street.postCode].commune); // urbis must return the full text municipality
    $('#id_report-postalcode').val(address.street.postCode);
    $('#id_report-address_number').val(address.number);
}

function fillI18nAdressField(lang, address) {
    $('#id_report-address_' + lang).val(address.street.name);
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

        if (!BACKOFFICE && address.street.postCode in zipcodes && !zipcodes[String(address.street.postCode)].participation) {

            fillAdressField(lang, address);

            $('#phone').html(zipcodes[String(address.street.postCode)].phone)

            //This commune does not participate to fixmystreet until now.
            $('#nonparticipatingcommune').modal();
            $('#address-text').after('<p class="text-error">' + $('#nonparticipatingcommune .modal-body p').html() + '</p>');

        } else if(response.status == 'success') {

            $form.find('button, :submit').prop('disabled', false);

            fillAdressField(currLang, address);
            fillI18nAdressField(currLang, address);

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


            //Search if the address is on a regional road or not.
            // var pointX = parseInt($('#id_report-x').val());
            // var pointY = parseInt($('#id_report-y').val());
            // regDetection(pointX, pointY);

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
