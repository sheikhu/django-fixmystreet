
$(function () {
    fms.map = new L.FixMyStreet.Map('map');
    fms.newIncidentMarker = new fms.NewIncidentMarkerView();
    fms.newIncidentMarker.render();
});

fms.ReportMapView = Backbone.View.extend({
    el: '.report-map',
    render: function () {
        var self = this;

        if (this.el) {
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
        }

        return this;
    }
});


fms.NewIncidentMarkerView = Backbone.View.extend({
    el: '#map',
    events: {
        'markermoved': 'loadAddress',
        'click #btn-localizeviamap': 'localizeViaMap'
    },
    moveMePopupTemplate: _.template([
        '<p class="popupMoveMe popupHeading"><%= gettext("Move the cursor") %></p>',
        '<% if (address) { %>',
        '  <p class="popupMoveMe popupContent">',
        '    <%= address.street.name %>, <%= address.street.number %><br/>',
        '    <%= address.street.postCode %> <%= address.street.municipality %>',
        '  </p>',
        '  <% if (address.number) { %>',
        '    <a class="btn-itshere" href="<%= NEXT_PAGE_URL %>?x=<%= position.x %>&y=<%= position.y %>"><%= gettext("It is here") %></a>',
        '    <div id="btn-streetview">',
        '      <a href="<%= googleStreetViewLink %>" target="_blank">',
        '        <i class="icon-streetview"></i>Street View',
        '      </a>',
        '    </div>',
        '  <% } %>',
        '<% } %>',
    ].join('\n')),

    localizeViaMap: function (evt) {
        evt.preventDefault();
        this.$el.addClass("map-big");

        this.putMarker(fms.map.getCenter(), null, true);
    },

    putMarker: function (position, address, preventZoomIn) {
        this.trigger('put-marker');

        draggableMarker = fms.map.addNewIncidentMarker(position);

        if (!preventZoomIn) {
            fms.currentMap.map.zoomTo(6);
        }

        this.renderPopup(position, address);
    },

    renderPopup: function(position, address) {
        var pointStreetView = UtilGeolocation.convertCoordinatesToWGS84(position.x, position.y);
        var googleStreetViewLink = 'https://maps.google.be/maps?q=' + pointStreetView.y + ',' + pointStreetView.y + '&layer=c&z=17&iwloc=A&sll='+ pointStreetView.y + ',' + pointStreetView.x + '&cbp=13,240.6,0,0,0&cbll=' + pointStreetView.y + ',' + pointStreetView.x;

        var popupContent = this.moveMePopupTemplate({
            position: position,
            address: address,
            googleStreetViewLink: googleStreetViewLink
        });

        if (!BACKOFFICE && address && address.street.postCode in zipcodes && !zipcodes[String(address.street.postCode)].participation) {
            popupContent = "<p class='popupMoveMe popupHeadingNonParticipating'>" + gettext('Non-participating municipality') + ".</p>";
            popupContent += "<p class='popupMoveMe popupContent'>" + gettext('Please contact the municipality') + ': '+ zipcodes[String(address.street.postCode)].phone + "</p>";
        }

        var popup = new OpenLayers.Popup(
            "popup",
            new OpenLayers.LonLat(fms.currentMap.draggableMarker.components[0].x, fms.currentMap.draggableMarker.components[0].y),
            new OpenLayers.Size(200,150),
            popupContent,
            true
        );
        popup.panMapIfOutOfView = true;

        fms.currentMap.map.addPopup(popup);
    },

    loadAddress: function (evt, position) {
        var self  = this;
        var origX = position.x;
        var origY = position.y;
        $.ajax({
            url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressfromxy',
            type:'POST',
            dataType:'jsonp',
            data: {
                json: JSON.stringify({
                    "language": LANGUAGE_CODE,
                    "point": position,
                })
            },
            success:function(response)
            {
                cleanMap();
                self.renderPopup(position, response.result.address);
            },
            error:function(response)
            {
                 if(response.status == 'error') {
                    fms.message.error('Unable to locate this address');
                } else {
                    fms.message.error('Error: ' + response.status);
                }
            }
        });
    }
});
