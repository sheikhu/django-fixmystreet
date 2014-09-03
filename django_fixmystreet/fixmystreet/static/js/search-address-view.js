
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

        this.addressProposal = new fms.AddressProposalView();
        this.addressProposal.render();

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
            url: URBIS_URL + 'service/urbis/Rest/Localize/getaddresses',
            dataType:'jsonp',
            data: {
                language: LANGUAGE_CODE,
                address: this.search.number + ' ' + this.search.street.name + ' ' + this.search.street.postcode,
                spatialReference:"4326"
            }
        }).success(function(response) {
            self.$searchStreet.removeClass('loading');
            self.$searchButton.prop('disabled',false);

            self.processSearchResults(response);
        }).error(function(xhr,msg,error){
            self.$searchStreet.removeClass('loading');
            self.$searchButton.prop('disabled',false);

            fms.message.error(gettext('Unexpected error'));
        });
    },
    processSearchResults: function (response) {
        if(response.status == 'success' && response.result.length > 0) {

            fms.newIncidentMarker.enlarge();
            this.addressProposal.cleanMap();

            // Urbis response 1 result
            if(response.result.length == 1) {
                var position = response.result[0].point;
                var address = response.result[0].address;

                fms.newIncidentMarker.putMarker(position, address);
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
