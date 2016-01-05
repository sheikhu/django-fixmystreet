$(function(){
    $.each($("form :input"),function(idx,value) {
        $(value).prop("disabled", true);
    });
    $("form :submit, form .btn, .helptext").hide();
});