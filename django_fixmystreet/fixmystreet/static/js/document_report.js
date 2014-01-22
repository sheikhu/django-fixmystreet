
$(document).ready(function() {
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

    // Validity step 1 : enable nexStep button if photo or comment
    var comment = document.getElementById("id_comment-text");

    function checkStep1Validity() {
        var photos = document.getElementsByClassName("thumbnail");

        if (comment.value || (photos.length > 1)) {

            if (proVersion) {
                send.disabled = false;
            } else {
                nextStep.disabled = false;
            }
            return true;
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
        console.log('check validaity');
        setTimeout(function() {
            checkStep1Validity();
            checkPhotoValidity();
        }, 500);
    }
    checkPhotoValidity();

    comment.addEventListener('keyup', checkStep1Validity);
    comment.addEventListener('change', checkStep1Validity);

    // Check validity in refresh browser.
    checkStep1Validity();

    if (!proVersion) {
        // Validity step 2 : enable send button if all required fields are ok
        var citizenMail    = document.getElementById('id_citizen-email');

        function checkStep2Validity() {
            var citizenQuality = $('input[name="citizen-quality"]:checked').val();

            if ( (citizenMail.value) && (citizenQuality)) {
                send.disabled = false;
            } else {
                send.disabled = true;

                return true;
            }

            return false;
        }

        citizenMail.addEventListener('keyup', checkStep2Validity);
        citizenMail.addEventListener('change', checkStep2Validity);
        $("input[name=citizen-quality]").change(checkStep2Validity);

        // Check validity in refresh browser.
        checkStep2Validity();
    }
});
