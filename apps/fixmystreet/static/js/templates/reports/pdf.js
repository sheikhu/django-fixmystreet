//remove zoom icons on the map image.
var mapOptions = {
    zoomControl: false,
    layersControl: false
};

//show incident marker on map
$(document).ready(function() {
    var latlng = L.FixMyStreet.Util.urbisCoordsToLatLng({x: REPORT_POINT_X, y: REPORT_POINT_Y});
    var marker = fms.map.addIncident({
        type: REPORT_STATUS_FOR_JS_MAP,
        latlng: latlng
    }, {popup: null});
    fms.map.centerOnMarker(marker);
    var res = UtilGeolocation.convertCoordinatesToWGS84(REPORT_POINT_X,REPORT_POINT_Y);
    document.getElementById("wgs84").innerHTML="L: " + res.x + " <br/>l: "+res.y;
});