// Switch between list/map
(function() {
    var btnMap  = document.getElementById('btn-map');
    var btnList = document.getElementById('btn-list');
    var map = document.getElementById('map');
    var list = document.getElementById('list');

    // List view
    btnList.addEventListener('click', function() {
        console.log('btnList click');

        btnList.classList.add('active');
        btnMap.classList.remove('active');

        map.classList.add('hide');
        list.classList.remove('hide');
    });

    // Map view
    btnMap.addEventListener('click', function() {
        console.log('btnMap click');

        btnMap.classList.add('active');
        btnList.classList.remove('active');

        list.classList.add('hide');
        map.classList.remove('hide');
    });
})(document);

// Map
(function() {

    var btnMap  = document.getElementById('btn-map');
    var reportsAdded = false;
    btnMap.addEventListener('click', function() {
        if(!reportsAdded){
            for (var i=0, length=REPORT_JSON_LIST.length; i<length; i++) {
                var report = REPORT_JSON_LIST[i];
                var latlng = L.FixMyStreet.Util.urbisCoordsToLatLng({x:  report.point.x , y:  report.point.y });
                var marker = fms.map.addIncident({
                        id: report.id,
                        type: report.status,
                        latlng: latlng,
                    });

            }
            fms.map.addSizeToggle({state1: {size: 'small'}});
            fms.map.fitToMarkers();
            reportsAdded= true;
        }
    });

})(document, fms);
