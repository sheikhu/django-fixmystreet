/******************************/
/* QUERY READY INITIALIZATION */
/******************************/
$(function(){
    $("#divMarkAsDone").hide();
    var latlng = L.FixMyStreet.Util.urbisCoordsToLatLng({x: REPORT_JSON.point.x, y:  REPORT_JSON.point.y});
    var marker = fms.map.addIncident({
        type: REPORT_JSON.status ,
        latlng: latlng,
    }, {popup: null});
    fms.map.centerOnMarker(marker);
    fms.map.addSizeToggle({state1: {size: 'small'}});
    fms.map.addStreetViewButton({latlng: marker.getLatLng()});

    $("#show-history").click(function(evt) {
        evt.preventDefault();
        $("#history_popup").modal();
    });

    //If running internet explorer then apply an extra span5 to comment and file div sections. Otherwise nothing is shown
 //    if ($.browser.msie) {
	// $('.report_update').addClass('span5');
 //    }

    $($(".update_text").find('#imgtoshow')).exifLoad(someCallback);

});
function setFileCreationDate(){
    var file = document.getElementById('id_file').files[0];
    var file_creation_date = new Date(""+file.lastModifiedDate);
    var dateString = file_creation_date.getFullYear() + "-"+ (file_creation_date.getMonth()+1) + "-" + file_creation_date.getDate()+ " " + file_creation_date.getHours()+":"+file_creation_date.getMinutes();

    $("[name='file_creation_date']").val(dateString);
}

/**
 * Mark as done function
 */
function markAsDone(){
    // $("#divMarkAsDone").show();

    $('#id_mark_as_done_motivation').val(TRAD_MARK_AS_DONE_MOTIVATION);
}


var someCallback = function(exifObject, index) {
    if (exifObject && exifObject.DateTimeOriginal){
        textAreas = $($(".update_text").find('#imagedate'));
        var datetosplit = exifObject.DateTimeOriginal;
        var splitted = datetosplit.split(/[:,\/ ]/)
        var pictureDate = new Date(splitted[0], splitted[1] -1, splitted[2], splitted[3], splitted[4], splitted[5], 0);
        textAreas[index].innerHTML = splitted[2] + '-' + splitted[1] + '-' + splitted[0] + " " +splitted[3] + ":" +splitted[4];
    }
}

$(function(event) {
    $("#btn-toggle-map a").click(function(evt) {
        evt.preventDefault();
        var mapEl = $('#map');
        if (mapEl.hasClass('map-big')) {
            mapEl.removeClass('map-big');
        } else {
            mapEl.addClass('map-big');
        }
    });
});