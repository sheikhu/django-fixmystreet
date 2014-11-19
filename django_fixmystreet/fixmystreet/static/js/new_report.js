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

/*
    var description = document.getElementById('description');
    var send        = document.getElementById('validate_button');

    // Only for citizen
    if (!proVersion) {
        // Switch between 2 steps
        var coordonnees = document.getElementById('coordonnees');

        var nextStep     = document.getElementById('nextStep');
        var previousStep = document.getElementById('previousStep');

        var stepDescription = document.getElementById('stepDescription');
        var stepCoordonnees = document.getElementById('stepCoordonnees');

        nextStep.addEventListener('click', function(event) {
            event.preventDefault();
            description.hidden = true;
            coordonnees.hidden = false;

            stepDescription.classList.remove('on');
            stepDescription.classList.add('off');

            stepCoordonnees.classList.remove('off');
            stepCoordonnees.classList.add('on');
        });

        previousStep.addEventListener('click', function(event) {
            event.preventDefault();
            coordonnees.hidden = true;
            description.hidden = false;

            stepCoordonnees.classList.remove('on');
            stepCoordonnees.classList.add('off');

            stepDescription.classList.remove('off');
            stepDescription.classList.add('on');
        });
    }

    // Validity step 1 : enable nexStep button if categories are setted
    var categoriesElements = description.getElementsByTagName("SELECT");
    var catego1            = categoriesElements[0];
    var catego2            = categoriesElements[1];

    function checkStep1Validity() {
        var photos = document.getElementsByClassName("thumbnail");

        if (photos.length > 1) {
            if ( (catego1.value) && (catego2.value) ) {
                if (proVersion) {
                    send.disabled = false;
                } else {
                    nextStep.disabled = false;
                }
            } else {
                if (proVersion) {
                    send.disabled = true;
                } else {
                    nextStep.disabled = true;
                }

                return true;
            }
        } else {
            if (proVersion) {
                send.disabled = true;
            } else {
                nextStep.disabled = true;
            }
        }

        return false;
    }

    // Hack to detect if at least 1 photo is present
    function checkPhotoValidity() {
        setTimeout(function() {
            checkStep1Validity();
            checkPhotoValidity();
        }, 500);
    }
    checkPhotoValidity();

    catego1.addEventListener('change', checkStep1Validity);
    catego2.addEventListener('change', checkStep1Validity);

    // Check validity in refresh browser.
    checkStep1Validity();

    if (!proVersion) {
        // Validity step 2 : enable send button if all required fields are ok
        var citizenMail      = document.getElementById('id_citizen-email');
        var termsOfUse       = document.getElementById('id_report-terms_of_use_validated');

        function checkStep2Validity() {
            var citizenQuality = $('input[name="citizen-quality"]:checked').val();

            if ( (citizenMail.value) && (citizenQuality) && (termsOfUse.checked) ) {
                send.disabled = false;
            } else {
                send.disabled = true;

                return true;
            }

            return false;
        }

        citizenMail.addEventListener('keyup', checkStep2Validity);
        citizenMail.addEventListener('change', checkStep2Validity);
        termsOfUse.addEventListener('change', checkStep2Validity);
        $("input[name=citizen-quality]").change(checkStep2Validity);

        // Check validity in refresh browser.
        checkStep2Validity();
    }
*/

});

function getAddressFromPoint(lang, x, y) {
    var self = this;
    $.ajax({
        url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressfromxy',
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

//DEPRECEATED?
function retrieveAddress() {
    var languages = ['fr', 'nl'],
        currLang = LANGUAGE_CODE,
        $form = $('#report-form');

    $form.find('button, :submit').prop('disabled', true);
    $('#address-text').addClass('loading');
    $('#citycode-text').addClass('loading');

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
            var msg = gettext('Error') + ': ' + response.status;
            if(response.status == 'error') {
                msg = gettext('Unable to locate this address');
            }
            $('#address-text').removeClass('loading');
            $form.prepend('<p class="text-error">' + msg + '</p>');
        }
    });
}
