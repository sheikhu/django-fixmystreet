$(function(){

    var latlng = L.FixMyStreet.Util.urbisCoordsToLatLng({x: REPORT_JSON.point.x, y: REPORT_JSON.point.y});
    var marker = fms.map.addIncident({
        type: REPORT_JSON.status,
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