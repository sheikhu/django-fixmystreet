var MapView = Backbone.View.extend({
    render: function () {
        this.map = L.map(this.el).setView([50.84535101789271, 4.351873397827148], 14);

        var nexrad = L.tileLayer.wms("/urbis/geoserver/gwc/service/wms", {
            layers: 'urbisFR', // + LANGUAGE_ODE
            format: 'image/png',
            transparent: true,
        	crs: L.CRS.EPSG31370,
            attribution: "Realized by means of Brussels UrbIS &copy; &reg;"
        }).addTo(this.map);

        return this;
    }
});
