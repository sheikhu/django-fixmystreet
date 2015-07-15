$(function(){
    $("input:checkbox").attr("value","off");
    $("input:checkbox").bind("change",function(){

        if ($(this).attr("value")!="on"){
            $(this).attr("value","on");
        }
        else {
            if($(this).attr("checked")=="checked"){
                $(this).attr("value","on");
                return false;
            }
            $(this).attr("value","off");
        }
    });
});