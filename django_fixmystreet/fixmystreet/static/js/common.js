$(document).ready(function(){
    $('#select-language').change(function(){
        $(this).closest('form').submit();
    });

    if ($("#leftMenuPanePro .positionable").length) {
        //Update menu entries with coordinates
        var USER_POSITION = new Object();
        if(navigator.geolocation){
            var options = {timeout:60000};
            var mapReference = this.map;
            navigator.geolocation.getCurrentPosition(
                //success
                function(position) {
                    var latitude = POSY = position.coords.latitude;
                    var longitude = POSX = position.coords.longitude;
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
    // $(":input, :select, ").submit(function(evt) {});
    $("form").submit(function(evt) {
        if (!validateForm($(this))) {
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


    // if (!$("#users_menu_item a").hasClass('active')) {
    //     $("#users_menu_item").hover(function(){$("#users_sub_menu").css("visibility","visible");},function(){$("#users_sub_menu").css('visibility','hidden');});
    //     $("#users_sub_menu").hover(function(){$("#users_sub_menu").css("visibility","visible");},function(){$("#users_sub_menu").css('visibility','hidden');});
    // } else {
    //     $("#users_sub_menu").css("visibility","visible");
    // }

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
});


function validateForm(form) {
    var valid = true;

    form.find('.required').each(function(ind, field) {
        var value = true;
        var $field = $(field);
        var $input = $field.find('input:visible, select:visible, textarea:visible');

        if ($field.find(":file").length) {
            value = form.find('.thumbnail:visible').length;
            $field = form.find('#file-form-template');
        } else if ($input.is(":checkbox")) {
            value = $input.is(":checked");
        } else if ($input[0].type === 'email' || $input.hasClass("validate-email")) {
            value = UtilValidator.validateEmail($input.val());
        } else {
            $input.each(function (ind, input) {
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
        console.log(this, valid? 'valid':'not valid');
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
