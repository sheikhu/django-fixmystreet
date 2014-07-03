var MapView = Backbone.View.extend({
    initialize: function () {
        this.layers = {};
        this.layers.urbis = L.tileLayer.wms("/urbis/geoserver/gwc/service/wms", {
            layers: 'urbisFR', // + LANGUAGE_ODE
            // layers: 'urbisORTHO',
            format: 'image/png',
            transparent: true,
            crs: L.CRS.EPSG31370,
            attribution: "Realized by means of Brussels UrbIS &copy; &reg;"
        });

        this.layers.ortho = L.tileLayer.wms("/urbis/geoserver/gwc/service/wms", {
            layers: 'urbisORTHO',
            format: 'image/png',
            transparent: true,
            crs: L.CRS.EPSG31370,
            attribution: "Realized by means of Brussels UrbIS &copy; &reg;"
        });
    },
    render: function () {
        var self = this;

        this.map = L.map(this.el).setView([50.84535101789271, 4.351873397827148], 14);

        this.layers.urbis.addTo(this.map);
        // this.layers.ortho.addTo(this.map);

        this.$el.addClass('loading');
        $.get('/fr/ajax/map/filter/', function (data) {
            self.$el.removeClass('loading');
            L.geoJson(data, {
                style: function (feature) {
                    return {color: 'red'};
                },
                onEachFeature: function (feature, layer) {
                    layer.bindPopup(feature.properties.description);
                }
            }).addTo(self.map);
        });


        return this;
    }
});
