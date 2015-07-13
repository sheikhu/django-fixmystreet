$(function(){

    var latlng = L.FixMyStreet.Util.urbisCoordsToLatLng({x: REPORT_POINT_X, y: REPORT_POINT_Y});
    var marker = fms.map.addIncident({
        type: REPORT_STATUS_FOR_JS_MAP,
        latlng: latlng,
    }, {popup: null});
    fms.map.centerOnMarker(marker);
    fms.map.addSizeToggle({state1: {size: 'small'}});
    fms.map.addStreetViewButton({latlng: marker.getLatLng()});
});

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