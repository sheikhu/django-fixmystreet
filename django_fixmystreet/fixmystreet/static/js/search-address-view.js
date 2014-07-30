
$(function () {
    fms.search = new fms.AddressSearchView();
    fms.search.render();
    fms.message = new fms.MessageView();
    fms.message.render();
});


fms.MessageView = Backbone.View.extend({
    el: "#proposal-message",
    show: function (message) {
        this.$el.append('<p>' + message + '</p>').slideDown();
    },
    error: function (message) {
        this.show('<span class="text-error">' + message + '.</span>');
    },
    clear: function () {
        this.$el.empty().slideUp();
    }
});

fms.AddressSearchView = Backbone.View.extend({
    el: '#search-address-form',
    events: {
        'submit': 'submitSeach',
    },

    render: function () {
        this.$searchStreet = this.$('#input-search');
        this.$searchStreetNumber = this.$('#input-streetnumber');
        this.$searchMunicipality = this.$('#input-ward');

        this.$searchButton = this.$('#widget-search-button');

        this.addressProposal = new fms.AddressProposalView();
        this.addressProposal.render();

        this.dragMarker = new fms.DragMarkerView();
        this.dragMarker.render();

        return this;
    },

    submitSeach: function (evt) {
        evt.preventDefault();
        this.search = {
            street: {
                name: this.$searchStreet.val(),
                postcode: this.$searchMunicipality.val()
            },
            number: this.$searchStreetNumber.val()
        };

        this.requestSeachResults();
    },

    requestSeachResults: function () {
        var self = this;

        $('#btn-localizeviamap').hide();
        this.addressProposal.close();
        fms.message.clear();

        //If only municipality as input then center on it
        if (!this.search.street.name && !this.search.number && this.search.street.postcode) {
            this.municipalityChange(this.search.street.postcode);
            return;
        }

        this.$searchStreet.addClass('loading');
        this.$searchButton.prop('disabled', true);

        $.ajax({
            url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressesfields',
            dataType:'jsonp',
            data: {
                json: JSON.stringify({
                    "language": LANGUAGE_CODE,
                    "address": this.search
                })
            }
        }).success(function(response) {
            self.$searchStreet.removeClass('loading');
            self.$searchButton.prop('disabled',false);

            self.processSeachResults(response);
        }).error(function(xhr,msg,error){
            self.$searchStreet.removeClass('loading');
            self.$searchButton.prop('disabled',false);

            fms.message.error(gettext('Unexpected error'));
        });
    },
    processSeachResults: function (response) {
        if(response.status == 'success' && response.result.length > 0) {

            $('#map').addClass("map-big");
            cleanMap();

            // Urbis response 1 result
            if(response.result.length == 1) {
                var position = response.result[0].point;
                var address = response.result[0].address;

                initDragMarker(position, address);
            } else {
                results = response.result;
                this.addressProposal.open(results);
                this.showResultIntegrityMessage(results);
            }
        } else {
            if(response.status == "noresult" || response.status == "success") {
                fms.message.error(gettext('No corresponding address has been found'));
            } else {
                fms.message.error(response.status);
            }
        }
    },
    showResultIntegrityMessage: function (results) {
        var thisMunicipalityExists = false,
            otherMunicipalityExists = false;

        for (var i in results) {
            var addr = results[i];
            if (this.search.street.postCode &&
                     this.search.street.postcode == addr.street.postCode &&
                     this.search.street.name.toLowerCase() == addr.street.name.toLowerCase()) {
                thisMunicipalityExists = true;
            }
            if (this.search.street.postCode &&
                     this.search.street.postcode != addr.street.postCode &&
                     this.search.street.name.toLowerCase() == addr.street.name.toLowerCase()) {
                otherMunicipalityExists = true;
            }
        }

        if (!thisMunicipalityExists && results.length) {
            fms.message.show(gettext('This street is not listed in this municipality.'));
        }
        if (otherMunicipalityExists && results.length) {
            fms.message.show(gettext('This street exists in several municipalities, please be more specific.'));
        }
    },

    municipalityChange: function (postalCode) {
        fms.currentMap.centerOnMunicipality(postalCode);
    }
});

/**
 * A single address proposal view in the address proposal container
 */
fms.AddressResultView = Backbone.View.extend({
    tagName: 'li',
    className: 'address-result',
    events: {
        'click': 'selectAddress'
    },
    template: _.template([
        '<p>',
        '  <img src="<%= icon %>" /><%= street.name %><br/>',
        '  <strong><%= street.postCode %> <%= street.municipality %></strong>',
        '</p>'
    ].join('\n')),
    constructor: function (options) {
        Backbone.View.apply(this, arguments);

        this.position = options.position;
        this.address = options.address;
        this.address.icon = "/static/images/marker/marker-" + options.index + ".png";
    },
    render: function() {
        this.$el.html(this.template(this.address));
        return this;
    },
    selectAddress: function(event) {
        fms.search.dragMarker.drop(this.position, this.address);
    }
});

/**
 * view for the list of multiple address search results.
 */
fms.AddressProposalView = Backbone.View.extend({
    el: '#proposal-container',
    events: {
        'click #previousResults': 'paginateResultsPrev',
        'click #nextResults': 'paginateResultsNext',
        'click .address-result': 'close',
    },

    render: function () {
        this.$proposal = this.$('#proposal');
        this.$numberResults = this.$('#numberResults');
        this.$previousResults = this.$('#previousResults');
        this.$nextResults = this.$('#nextResults');
        return this;
    },

    paginationResults: 0,
    paginateResultsPrev: function () {
        this.paginationResults -= 1;
        this.renderAddresses();
    },
    paginateResultsNext: function () {
        this.paginationResults += 1;
        this.renderAddresses();
    },
    close: function () {
        this.$el.slideUp();
        fms.message.clear();
    },
    open: function (addresses) {
        this.addresses = addresses;
        this.$numberResults.html(this.addresses.length);
        this.paginationResults = 0;

        if (!fms.currentMap.homepageMarkersLayer) {
            // Create vector layer
            fms.currentMap.homepageMarkersLayer = new OpenLayers.Layer.Vector("Overlay", {
                displayInLayerSwitcher: false
            });

            // Add layer to map
            fms.currentMap.map.addLayer(fms.currentMap.homepageMarkersLayer);

            // Function to bind selector to initDragMarker


            // Add the selector control to the vectorLayer
            var clickCtrl = new OpenLayers.Control.SelectFeature(
                fms.currentMap.homepageMarkersLayer, {
                    onSelect: this.onSelect
                }
            );
            fms.currentMap.map.addControl(clickCtrl);
            clickCtrl.activate();
        }

        this.renderAddresses();
        this.$el.slideDown();
    },

    onSelect: function (feature) {
        this.close();

        fms.search.dragMarker.drop(feature.geometry, feature.attributes);
    },

    renderAddresses: function () {
        var features = [],
             iconIdx = 0;

        this.$proposal.empty();

        for(var i = this.paginationResults * 5; i < this.addresses.length && features.length < 5; i++) {
            var address = this.addresses[i].address;
            var position = this.addresses[i].point;

            var newAddress = new fms.AddressResultView({
                position: position,
                address: address,
                index: iconIdx++
            });
            this.$proposal.append(newAddress.render().$el);

            // Create feature on vectore layer
            var feature = new OpenLayers.Feature.Vector(
                    new OpenLayers.Geometry.Point(position.x, position.y),
                    address,
                    {
                        externalGraphic: newAddress.address.icon,
                        graphicWidth: 25,
                        graphicHeight: 32,
                        graphicYOffset: -32
                    }
                );
            features.push(feature);
        }
        this.$previousResults.toggle(this.paginationResults !== 0);
        this.$nextResults.toggle(this.addresses.length > (this.paginationResults + 1) * 5);

        // Add features to layer
        cleanMap();
        fms.currentMap.homepageMarkersLayer.addFeatures(features);

        // Zoom to markers
        var markersBound = fms.currentMap.homepageMarkersLayer.getDataExtent();
        fms.currentMap.map.zoomToExtent(markersBound);
    }
});

function cleanMap() {
    // Remove all popups
    while(fms.currentMap.map.popups.length) {
         fms.currentMap.map.removePopup(fms.currentMap.map.popups[0]);
    }

    // Remove all features
    if (fms.currentMap.markersLayer) {
        fms.currentMap.markersLayer.destroyFeatures();
    }
    if (fms.currentMap.homepageMarkersLayer) {
        fms.currentMap.homepageMarkersLayer.destroyFeatures();
    }
}

// Localize report with map
(function() {
    $('#btn-localizeviamap').click(function(evt) {
        evt.preventDefault();
        var center = fms.currentMap.map.getCenter();
        // Hard code center of map
        fms.search.dragMarker.drop({
            x: center.lon,
            y: center.lat
        }, null, true);

        btnLocalizeviamap.parentNode.removeChild(btnLocalizeviamap);
    });

})(document);
