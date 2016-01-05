$(document).ready(function() {
    // Get point x y from url
    $.urlParam = function(name){
        var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
        return results[1] || 0;
    };

    var x = $.urlParam('x');
    var y = $.urlParam('y');

    getAddressFromPoint('fr', x, y);
    getAddressFromPoint('nl', x, y);
});

var URBIS_GETADDRESSFROMXY_URL = 'service/urbis/Rest/Localize/getaddressfromxy';

function getAddressFromPoint(lang, x, y) {
    var self = this;
    $.ajax({
        url: URBIS_URL + URBIS_GETADDRESSFROMXY_URL,
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
            //Fix problem with postcode 1041
            if (response.result.address.street.postCode === "1041") {
                response.result.address.street.postCode = "1040";
            }

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
                msg = gettext('Unable to locate this address');
            }
            $('#address-text').html(msg);
            $('#citycode-text').html(msg);

        }
    });
}
function fillAdressField(address) {
    $('#address-text').html(address.number + ' ' + address.street.name); // urbis must return the full text municipality
    $('#citycode-text').html(address.street.postCode + " " + zipcodes[address.street.postCode].commune); // urbis must return the full text municipality

    $('#id_report-postalcode').val(address.street.postCode);
    $('#id_report-address_number').val(address.number);
}

function fillI18nAdressField(lang, address) {
    $('#id_report-address_' + lang).val(address.street.name);
}
