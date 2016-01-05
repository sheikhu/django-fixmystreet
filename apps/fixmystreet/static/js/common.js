$(document).ready(function(){
    $('#select-language').change(function(){
        $(this).closest('form').submit();
    });

    if ($("#leftMenuPanePro .positionable").length) {
        //Update menu entries with coordinates
        var USER_POSITION = {};
        if(navigator.geolocation){
            var options = {timeout:60000};
            var mapReference = this.map;
            navigator.geolocation.getCurrentPosition(
                //success
                function(position) {
                    var latitude = position.coords.latitude;
                    var longitude = position.coords.longitude;
                    var p = new Proj4js.Point(longitude, latitude);
                    Proj4js.transform(new Proj4js.Proj("EPSG:4326"), new Proj4js.Proj("EPSG:31370"), p);
                    USER_POSITION.x = p.x;
                    USER_POSITION.y = p.y;
                    updateMenuEntries(p.x,p.y);
                },
                function() {},
            options);
        }
    }


    /* form validation */
    $("form").submit(function(evt) {
        var $this = $(this);
        var isValid = validateForm($this);
        $this.find('[data-one-click]').prop('disabled', isValid && $('#coordonnees').is(':visible'));
        if (!isValid) {
            evt.preventDefault();
            evt.stopImmediatePropagation();
        }
    });

    $("[data-toggle=popover]")
        .popover({
            html : true,
            content: function() {
                return $(this).next().html();
            }
        })
        .click(function(e) {
            e.preventDefault();
        });

    // Add the active class to the active page number
    var paginator = $(".pagination");
    if (paginator.length) {
        paginator.delegate("a:not(.active), .pagination_prev:not(.disabled) .pagination_next:not(.disabled)", "click", function(evt) {
            evt.preventDefault();
            var page = $(this).data("page");
            if(page) {
                getUrlForPageNumber(page);
            }
        });
    }

    var description = $('#description'),
        coordonnees = $('#coordonnees'),
        stepDescription = $('#stepDescription'),
        stepCoordonnees = $('#stepCoordonnees');
    if(description.length) {
        $('#description').closest('form').submit(function (evt) {
            if(coordonnees.length && description.is(':visible')) {
                evt.preventDefault();
                description.hide();
                coordonnees.show();
                stepDescription.removeClass("on").addClass("off");
                stepCoordonnees.removeClass("off").addClass("on");
            } else {
                coordonnees.find('[data-one-click]').prop('disabled', false);
            }
        });
        $('#previousStep').click(function (evt) {
            evt.preventDefault();
            coordonnees.hide();
            description.show();
            stepDescription.removeClass("off").addClass("on");
            stepCoordonnees.removeClass("on").addClass("off");
            coordonnees.find('[data-one-click]').prop('disabled', false);
        });
    }

    if(coordonnees.length && citizen_error){
      description.hide();
      coordonnees.show();
      stepDescription.removeClass("on").addClass("off");
      stepCoordonnees.removeClass("off").addClass("on");
    }
});


function validateForm(form) {
    var valid = true;

    form.find('.required input:visible, .required select:visible, .required textarea:visible').each(function(ind, field) {
        var value = true;
        var $field = $(field);

        if ($field.is(":radio")) {
            //check all the value of the current radio button group and return true if one of them is checked
            value = !!($(':radio[name=' + $field[0].name + ']:checked', form).val());
        }
        else if ($field.is(":checkbox")) {
            value = $field.is(":checked");
        } else if ($field[0].type === 'email' || $field.hasClass("validate-email")) {
            value = UtilValidator.validateEmail($field.val());
        } else {
            $field.each(function (ind, input) {
                if (!$(input).val()) {
                    value = false;
                }
            });
        }
        if(!value) {
            valid = false;
            $field.addClass('invalid');
        } else {
            $field.removeClass('invalid');
        }
    });

    if(!valid) {
        form.find('.invalid input, .invalid select').first().focus();
        form.find('.required-error-msg').fadeIn();
        form.addClass('required-invalid');
    }
    return valid;
}

function updateMenuEntries(x,y) {
    //Update the left menu coordinates
    var currentHref;
    $("#leftMenuPanePro .positionable").each(function(idx,value){
            currentHref = $(value).attr('href');
            $(value).attr('href',currentHref+'?x='+x+'&y='+y);
    });
        //End update menu
}

function getCurrentLanguage() {
    return LANGUAGE_CODE;
}


function getUrlForPageNumber(number) {
    var url = window.location.href;
    if(url.indexOf("page=")!=-1){

        var list = url.split("page=");
        url1= list[0].replace(/\&amp;/g,'&');
        url1 = url1.replace("amp;","");
        url = url1 + "page="+ number;

    } else if(url.indexOf("?")!=-1) {
        url += "&page="+number;
    } else {
        url += "?page="+number;
    }

    window.location = url;
}
