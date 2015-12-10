$(document).ready(function(){

    $.each($(".matrixButton"),function(idx,value){
        if($(value).text().indexOf("No manager selected")!=-1){
            $(value).addClass("emptySelection");
        }
    });

    /*Hide empty selection zones*/
    if($("#54").is("button")){
        $('#54').hide();
    }
    if($("#38").is("button")){
        $('#38').hide();
    }
    if($("#58").is("button")){
        $('#58').hide();
    }
    $(function() {
        if(SHOW_MODAL){
            $("#dialog").modal();
        }
    });
});