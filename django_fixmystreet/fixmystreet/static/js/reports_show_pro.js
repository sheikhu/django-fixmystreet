/******************************/
/* QUERY READY INITIALIZATION */
/******************************/
$(function(){
    var connected = true;

    $("#dialog").dialog({
        modal: true,
        autoOpen:false,
        width:'auto',
        resizable: false
    });

    /*******************************/
    /* When clicking any page form */
    /*******************************/
    $('form').submit(function(){
        if(!connected){
            evt.preventDefault();
        }
    });
    
    $('#map-bxl').hide();
    
   });

/******************************************/
/* showMap is used to show the mpa widget */
/******************************************/
function showMap() {
    $("#map-bxl").toggle();
}


/****************************************************************************/
/* Refuse method is called when the gestionnaire decides to refuse a report */
/****************************************************************************/
function refuse(){
    $("#dialog").dialog('open');
    $('#more_information_text').val("This is the initial text that needs to be defined. It's a suggestion for the gestionnaire. He can be edited as needed.")
}

/***************************************************************************/
/* refuseConfirmButton method is called when the user confirms his refusal */
/***************************************************************************/
function refuseConfirmButton(){
    window.location = '{% url report_refuse_pro report.id %}?more_info_text='+$('#more_information_text').val();
}

/*************************************************************************/
/* refuseCancelButton method is called when the user cancels his refusal */
/*************************************************************************/
function refuseCancelButton() {
    $("#dialog").dialog('close');
}
