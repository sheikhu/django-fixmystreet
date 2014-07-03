var MapView = Backbone.View.extend({
    render: function () {
        var map = L.map(this.el).setView([55.75, 37.58], 10);

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
