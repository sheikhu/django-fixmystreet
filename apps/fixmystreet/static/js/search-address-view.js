
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
        this.show('<span class="text-error">' + message + '</span>');
    },
    clear: function () {
        this.$el.empty().slideUp();
    }
});

var URBIS_GETADDRESS_URL = 'localization/Rest/Localize/getaddresses';

fms.AddressSearchView = Backbone.View.extend({
    el: '#search-address-form',
    events: {
        'submit': 'submitSearch',
    },

    render: function () {
        this.$searchStreet = this.$('#input-search');
        this.$searchStreetNumber = this.$('#input-streetnumber');
        this.$searchMunicipality = this.$('#input-ward');

        this.$searchButton = this.$('#widget-search-button');

        fms.map.addLocateOnMapButton();

        return this;
    },

    submitSearch: function (evt) {
        evt.preventDefault();
        this.search = {
            street: {
                name: this.$searchStreet.val(),
                postcode: this.$searchMunicipality.val()
            },
            number: this.$searchStreetNumber.val()
        };

        this.requestSearchResults();
    },

    requestSearchResults: function () {
        var self = this;

        $('#btn-localizeviamap').hide();
        fms.message.clear();

        //If only municipality as input then center on it
        if (!this.search.street.name && !this.search.number && this.search.street.postcode) {
            this.municipalityChange(this.search.street.postcode);
            return;
        }

        this.$searchStreet.addClass('loading');
        this.$searchButton.prop('disabled', true);

        $.ajax({
            url: URBIS_URL + URBIS_GETADDRESS_URL,
            dataType:'jsonp',
            data: {
                language: LANGUAGE_CODE,
                address: this.search.number + ' ' + this.search.street.name + ' ' + this.search.street.postcode,
                spatialReference:"4326"
            }
        }).success(function(response) {
            self.offsetFromHomeToStreet(response);
        }).error(function(xhr,msg,error){
            self.$searchStreet.removeClass('loading');
            self.$searchButton.prop('disabled',false);

            fms.message.error(gettext('Unexpected error'));
        });
    },
    // Tricky stuff: contact offset service with adnc
    offsetFromHomeToStreet: function(response) {
        for (var idx in response.result) {
            if (response.result[0].adNc) {
                this.getOffset(response, idx);
            }
        }

        this.$searchStreet.removeClass('loading');
        this.$searchButton.prop('disabled',false);
        this.processSearchResults(response);
    },
    getOffset: function(response, idx) {
        var URBIS_ADNCS_URL = 'https://geoservices-others.irisnet.be/geoserver/Urbis/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=Urbis:AdptOnSi&CQL_FILTER=%28Urbis:ADNCS%20like%20%27%25;param;%25%27%29&outputFormat=application%2Fjson';

        var url = URBIS_ADNCS_URL.replace('param', response.result[idx].adNc);

        $.ajax({
            url: url,
            dataType:'json',
            async: false
        }).success(function(adncResponse) {
            if (adncResponse.features.length) {

                var point = {
                    x: adncResponse.features[0].geometry.coordinates[0],
                    y: adncResponse.features[0].geometry.coordinates[1]
                }
                response.result[idx].point = L.FixMyStreet.Util.urbisCoordsToLatLng(point)

            }
        }).error(function(xhr,msg,error){
        });
    },
    processSearchResults: function (response) {
        if (response.status == 'success' && response.result.length > 0) {
            fms.map.removeSearchResults();
            fms.map.removeNewIncident();

            if (response.result.length === 1) {
              try{
                var model = {
                    type: 'new',
                    latlng: L.FixMyStreet.Util.toLatLng(response.result[0].point),
                    address: L.FixMyStreet.Util.urbisResultToAddress(response.result[0]),
                };
                fms.map.addIncident(model);
              }
              catch (error) {
                fms.map.removeSearchResults();
                fms.map.addSearchResults([]);
              }
            } else {
                var models = [];
                $.each(response.result, function (i, result) {
                    try{
                      var model = {
                        number: String.fromCharCode(65 + i),
                        latlng: L.FixMyStreet.Util.toLatLng(result.point),
                        address: L.FixMyStreet.Util.urbisResultToAddress(result),
                      };
                      models.push(model);
                    }
                    catch (error) {
                      console.log(error.message);
                    }
                });
                if(models.length > 0){
                  fms.map.addSearchResults(models);
                  this.showResultIntegrityMessage(response.result);
                }
                else{
                  fms.map.removeSearchResults();
                  fms.map.addSearchResults([]);
                }
            }
        } else if (response.status == "noresult" || response.status == "success") {
            fms.map.removeSearchResults();
            fms.map.addSearchResults([]);
        } else {
            fms.message.error(response.status);
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
        fms.map.centerOnMunicipality(postalCode);
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
        fms.newIncidentMarker.putMarker(this.position, this.address);
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
    proposalMarkers: [],

    render: function () {
        var self = this;

        this.$proposal = this.$('#proposal');
        this.$numberResults = this.$('#numberResults');
        this.$previousResults = this.$('#previousResults');
        this.$nextResults = this.$('#nextResults');

        fms.newIncidentMarker.on('put-marker', function () {
            self.cleanMap();
        });
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
        this.proposalMarkerLayer = new L.FeatureGroup();
        this.proposalMarkerLayer.addTo(fms.map);

        this.renderAddresses();
        this.$el.slideDown();
    },

    onSelect: function (feature) {
        this.close();

        fms.newIncidentMarker.putMarker(feature.geometry, feature.attributes);
    },

    renderAddresses: function () {
        var features = [],
             iconIdx = 0,
             i = this.paginationResults * 5;

        this.$proposal.empty();
        this.proposalMarkers = [];
        this.cleanMap();

        for(; i < this.addresses.length && this.proposalMarkers.length < 5; i++) {
            var address = this.addresses[i].address;
            var position = this.addresses[i].point;

            var newAddress = new fms.AddressResultView({
                position: position,
                address: address,
                index: iconIdx++
            });
            this.$proposal.append(newAddress.render().$el);

            // Create feature on vectore layer
            var feature = fms.map.addMarker(
                new L.LatLng(position.y, position.x), {
                    icon: L.icon({
                        iconUrl: newAddress.address.icon
                    }),
                    model: address
                }
            );

            feature.addTo(this.proposalMarkerLayer);
            this.proposalMarkers.push(feature);
        }
        this.$previousResults.toggle(this.paginationResults !== 0);
        this.$nextResults.toggle(this.addresses.length > (this.paginationResults + 1) * 5);

        // Add features to layer
        // fms.map.homepageMarkersLayer.addFeatures(features);

        var bounds = this.proposalMarkerLayer.getBounds();
        fms.map.fitBounds(bounds);
    },

    cleanMap: function () {
        if (fms.map.popups) {
            // Remove all popups
            while(fms.map.popups.length) {
                 fms.map.removePopup(fms.map.map.popups[0]);
            }
        }

        if (this.proposalMarkerLayer) {
            this.proposalMarkerLayer.clearLayers();
        }
    }
});
