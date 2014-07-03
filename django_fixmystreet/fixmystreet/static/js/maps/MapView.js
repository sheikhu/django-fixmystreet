var MapView = Backbone.View.extend({
    render: function () {
        var map = L.map(this.el).setView([50.84331852979277,4.357895514064874], 12);

        var nexrad = L.tileLayer.wms("http://geoserver.gis.irisnet.be/urbis/wms/gwc", {
            layers: 'urbisFR', // + LANGUAGE_ODE
            format: 'image/png',
            transparent: true,
        	crs: L.CRS.EPSG31370,
            attribution: "Realized by means of Brussels UrbIS &copy; &reg;"
        }).addTo(map);

        return this;
    }
});
