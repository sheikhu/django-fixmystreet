//Test if console.log exists (does not exists on ie8 and <) tips to avoid console.log to block js on those env.
if (typeof console=='undefined') {
        window.console = new Object();
    window.console.log = function(msg) {/*Does nothing*/};
}

// this was between {% if messages %} ...{% endif %} but probably not needed so code was moved here.
$(function(){
    $('.message').modal();
});

$(function(){
    if (($.browser.msie && parseInt($.browser.version.split(".")[0]) < 10) || ($.browser.mozilla && !navigator.userAgent.match(/Trident.*rv\:11\./) && parseInt($.browser.version.split(".")[0]) < 24) || $.browser.chrome && parseInt($.browser.version.split(".")[0]) < 31) {
        //$('#browser_support_popup').alert();
        $('#browser_support_popup').css('display', "block");
    }
    // If on iphone ==> redirect to mobile page
    // if(navigator.platform.indexOf("iPhone") != -1){
    //     window.location="{{request.get_full_path}}../static/iphone_download.html";
    // }
});

$('.myTooltip').tooltip();