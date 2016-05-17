//remove zoom icons on the map image.
var mapOptions = {
    zoomControl: false,
    layersControl: false,
    zoom:16
};

//show incident marker on map
$(document).ready(function() {
    var latlng = L.FixMyStreet.Util.urbisCoordsToLatLng({x: REPORT_JSON.point.x, y: REPORT_JSON.point.y});
    var marker = fms.map.addIncident({
        type: REPORT_JSON.status,
        latlng: latlng
    }, {popup: null});
    fms.map.centerOnMarker(marker);
    var res = UtilGeolocation.convertCoordinatesToWGS84(REPORT_JSON.point.x,REPORT_JSON.point.y);
    document.getElementById("wgs84").innerHTML="L: " + res.x + " <br/>l: "+res.y;
});