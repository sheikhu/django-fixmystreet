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
    $("form").submit(function(evt) {
        if (!validateForm($(this))) {
            evt.preventDefault();
        }
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
        $(".pagination_next:not(.disabled)").click(function(evt) {
            evt.preventDefault();
            getUrlForPageNumber(pageNumber + 1);
        });
        $(".pagination_prev:not(.disabled)").click(function(evt) {
            evt.preventDefault();
            getUrlForPageNumber(pageNumber - 1);
        });
        paginator.delegate("a:not(.active)", "click", function(evt) {
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

    form.find('.required input, .required select, .required textarea').each(function(ind,input) {
        var $input = $(input);
        if(!$input.val()) {
            valid = false;
            $input.closest('.required').addClass('invalid');
        } else {
            $input.closest('.required').removeClass('invalid');
        }
    });

    if(!valid) {
        form.find('.invalid input, .invalid select').first().focus();
        form.find('.required-error-msg').fadeIn();
        form.addClass('required-invalid');

        return false;
    }
    return true;
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
	//Get current language
	var currentLng = 'en';
	if (window.location.href.indexOf('/nl/') != -1) {
	    currentLng = 'nl';
	} else if (window.location.href.indexOf('/fr/') != -1) {
	    currentLng = 'fr'
	}
	return currentLng;
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