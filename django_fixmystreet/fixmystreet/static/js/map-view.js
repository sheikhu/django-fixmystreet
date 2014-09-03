
$(function () {
    fms.map = new L.FixMyStreet.Map('map');
    fms.newIncidentMarker = new fms.NewIncidentMarkerView();
    fms.newIncidentMarker.render();
});

fms.ReportMapView = Backbone.View.extend({
    el: '#map.report-map',
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
        'drag': 'loadAddress',
        'click #btn-localizeviamap': 'localizeViaMap'
    },
    moveMePopupTemplate: _.template([
        '<div>',
        '<p class="popupMoveMe popupHeading"><%= gettext("Move the cursor") %></p>',
        '<% if (address) { %>',
        '  <p class="popupMoveMe popupContent">',
        '    <%= address.street.name %>, <%= address.street.number %><br/>',
        '    <%= address.street.postCode %> <%= address.street.municipality %>',
        '  </p>',
        '  <% if (address.number) { %>',
        '    <a class="btn-itshere" href="<%= NEXT_PAGE_URL %>?x=<%= position.lng %>&y=<%= position.lat %>"><%= gettext("It is here") %></a>',
        '    <div id="btn-streetview">',
        '      <a href="<%= googleStreetViewLink %>" target="_blank">',
        '        <i class="icon-streetview"></i>Street View',
        '      </a>',
        '    </div>',
        '  <% } %>',
        '<% } %>',
        '</div>',
    ].join('\n')),
    render: function () {
        return this;
    },
    enlarge: function () {
        fms.map.setCssSize('map-size-big');
    },
    localizeViaMap: function (evt) {
        evt.preventDefault();
        this.enlarge();

        this.putMarker(fms.map.getCenter(), null, true);
    },

    putMarker: function (position, address, preventZoomIn) {
        var self = this;
        this.trigger('put-marker');
        this.position = new L.LatLng(position.y, position.x);
        this.address = address;

        fms.map.removeNewIncidentMarker();
        this.draggableMarker = fms.map.addNewIncidentMarker(this.position, {
            popup: this.renderPopup(),
        });

        this.latlng = this.draggableMarker.getLatLng();
        this.draggableMarker.on('dragend', function () {
            self.loadAddress();
        });

        if (!preventZoomIn) {
            fms.map.setView(this.position, 18);  // max zoom
        }
        window.setTimeout(function() { self.draggableMarker.openPopup(); }, 500);
    },

    loadAddress: function () {
        var self  = this;

        this.position = this.draggableMarker.getLatLng();
        // this.position = UtilGeolocation.convertCoordinatesToWMS(this.latlng);

        $.ajax({
            url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressfromxy',
            type:'POST',
            dataType:'jsonp',
            data: {
                json: JSON.stringify({
                    language: LANGUAGE_CODE,
                    point: {x: this.position.lat, y: this.position.lng}
                })
            },
            success:function(response)
            {
                // cleanMap();
                self.address = response.result.address;
                var content = self.renderPopup();
                self.draggableMarker.setPopupContent(content);
                self.draggableMarker.openPopup();

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
    },

    renderPopup: function() {
        var googleStreetViewLink = 'https://maps.google.be/maps?q=' +
                this.position.lat + ',' + this.position.lng + '&layer=c&z=17&iwloc=A&sll='+
                this.position.lat + ',' + this.position.lng + '&cbp=13,240.6,0,0,0&cbll=' +
                this.position.lat + ',' + this.position.lng;

        var popupContent = this.moveMePopupTemplate({
            position: this.position,
            address: this.address,
            googleStreetViewLink: googleStreetViewLink
        });

        if (!BACKOFFICE &&
                this.address &&
                this.address.street.postCode in zipcodes &&
                !zipcodes[String(this.address.street.postCode)].participation) {
            popupContent = "<p class='popupMoveMe popupHeadingNonParticipating'>" + gettext('Non-participating municipality') + ".</p>";
            popupContent += "<p class='popupMoveMe popupContent'>" + gettext('Please contact the municipality') + ': '+ zipcodes[String(address.street.postCode)].phone + "</p>";
        }

        return popupContent;
        // var popup = new OpenLayers.Popup(
        //     "popup",
        //     new OpenLayers.LonLat(fms.currentMap.draggableMarker.components[0].x, fms.currentMap.draggableMarker.components[0].y),
        //     new OpenLayers.Size(200,150),
        //     popupContent,
        //     true
        // );
        // popup.panMapIfOutOfView = true;
        //
        // fms.currentMap.map.addPopup(popup);
    }
});
