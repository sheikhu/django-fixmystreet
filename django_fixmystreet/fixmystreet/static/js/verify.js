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

    btnMap.addEventListener('click', function() {
        fms.currentMap = new fms.Map('map', {
            apiLang:     LANGUAGE_CODE,
            localizeUrl: URBIS_URL + 'service/urbis/Rest/Localize/getaddressfromxy',
            urbisUrl:    WMS_SERVICE_URL
        });

        var markers = [];
        for (var i=0, length=reportJSONList.length; i<length; i++) {
            var marker = fms.currentMap.addReport(reportJSONList[i], i +1, proVersion);

            markers.push(marker);
        }

        fms.currentMap.markersLayer.addFeatures(markers);
    });

})(document, LANGUAGE_CODE, URBIS_URL, WMS_SERVICE_URL, fms);


