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

// Idea coming from: http://shahinalborz.se/2010/11/disable-double-click-to-prevent-multiple-execution/
function preventMultipleClicks(event) {
  // Enable link if undefined
  if (typeof(_linkEnabled)=="undefined") {
    _linkEnabled = true;
  }

  setTimeout(function() {
    // Disable link
    _linkEnabled = false;

    // If multiple clicks, clear the previous setTimeout...
    // ... to avoid multiple _linkEnabled=true
    if (typeof(timeoutId)!="undefined") {
      clearTimeout(timeoutId);
    }

    // Enable link after some seconds
    timeoutId = setTimeout(function() {
      _linkEnabled=true;
    }, 10000);

  }, 100);

  return _linkEnabled;
}
