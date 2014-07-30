
$(function () {
    fms.map = new fms.MapView();
    fms.map.render();
});

fms.MapView = Backbone.View.extend({
    render: function () {
        var self = this;

        this.map = L.FixMyStreet.Map('map');

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


fms.DragMarkerView = Backbone.View.extend({
    el: '#map',
    events: {
        'markermoved': 'loadAddress'
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
    drop: function (position, address, preventZoomIn) {
        cleanMap();

        draggableMarker = fms.currentMap.addDraggableMarker(position.x, position.y);
        fms.currentMap.centerOnDraggableMarker();

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

        if (!BACKOFFICE && address.street.postCode in zipcodes && !zipcodes[String(address.street.postCode)].participation) {
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
