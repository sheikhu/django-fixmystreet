var results           = [];
var paginationResults;

var previousResults = document.getElementById("previousResults");
var nextResults     = document.getElementById("nextResults");

var draggableMarker;

previousResults.addEventListener('click', function() {
    paginationResults -= 1;
    renderResults();
});
nextResults.addEventListener('click', function() {
    paginationResults += 1;
    renderResults();
});

function renderResults() {
    var $proposal = $('#proposal');
    var $proposalMessage = $('#proposal-message');

    var $searchStreet = $('#input-search');
    var $searchMunicipality = $('#input-ward');

    $proposal.empty();
    var features = [];

    var iconIdx = 0;
    for(var i=paginationResults*5, length=results.length; i<length && features.length<5; i++) {
        var address = results[i].address;
        var pos = results[i].point;

        var newAddress = new AddressResult(pos.x, pos.y, address, iconIdx++);
        $proposal.append(newAddress.render());

        // Create feature on vectore layer
        var feature = new OpenLayers.Feature.Vector(
                new OpenLayers.Geometry.Point(pos.x, pos.y),
                { 'additionalInfo' :
                    {
                        'streetName'   : address.street.name,
                        'number'       : address.number,
                        'postCode'     : address.street.postCode,
                        'municipality' : address.street.municipality
                    }
                },
                {
                    externalGraphic: newAddress.iconSrc(),
                    graphicWidth: 25,
                    graphicHeight: 32,
                    graphicYOffset: -32
                }
            );
        features.push(feature);

        // Define message if needed
        if ($searchMunicipality.val()) {
            $proposalMessage.html(gettext('This street is not listed in this municipality.'));
        } else if ($searchStreet.val().toLowerCase() == address.street.name.toLowerCase()) {
            $proposalMessage.html(gettext('This street exists in several municipalities, please be more specific.'));
        }
    }

    // Mask/display pagination buttons
    if (paginationResults == 0) {
        previousResults.hidden = true;
    } else {
        previousResults.hidden = false;
    }

    if (results.length >= paginationResults * 5 + 6) {
        nextResults.hidden = false;
    } else {
        nextResults.hidden = true;
    }

    // Add features to layer
    cleanMap();
    fms.currentMap.homepageMarkersLayer.addFeatures(features);

    // Zoom to markers
    var markersBound = fms.currentMap.homepageMarkersLayer.getDataExtent();
    fms.currentMap.map.zoomToExtent(markersBound);

    // Show/hide proposal and message
    $proposalContainer = $('#proposal-container');
    $proposalContainer.slideDown();

    if ($proposalMessage.html()) {
        map.classList.add("map-big-message");
        $proposalMessage.slideDown();
    } else {
        map.classList.remove("map-big-message");
        map.classList.add("map-big");
        $proposalMessage.slideUp();
    }

}

function AddressResult(x, y, address, idx)
{
    var self = this;

    this.x = x;
    this.y = y;
    this.el = document.createElement('li');

    this.address = address;

    this.render = function() {
        this.el.innerHTML = '<p><img src="' + this.iconSrc() + '" />' + this.address.street.name +
                            '<br/>' +
                            '<strong>' + this.address.street.postCode + ' ' + this.address.street.municipality + '</strong>' +
                            '</p>';
        this.el.addEventListener('click', this.onclick);
        return  this.el;
    };

    this.iconSrc = function() {
        return "/static/images/marker/marker-" + idx + ".png";
    };

    this.onclick = function(event) {
        additionalInfo = {
            'streetName'   : self.address.street.name,
            'number'       : self.address.number,
            'postCode'     : self.address.street.postCode,
            'municipality' : self.address.street.municipality
        };

        initDragMarker(self.x, self.y, additionalInfo);
    };
}

function getAddressFromPoint(lang, x, y) {
    var self  = this;
    var origX = x;
    var origY = y;
    $.ajax({
        url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressfromxy',
        type:'POST',
        dataType:'jsonp',
        data: {
            json: ['{',
                '"language": "' + lang + '",',
                '"point":{x:' + x + ',y:' + y + '}',
                '}'].join('\n')
        },
        success:function(response)
        {
            cleanMap();

            var street = response.result.address.street.name;
            var number = response.result.address.number;
            var postCode = response.result.address.street.postCode;

            //console.log(origX,origY);
            var municipality = zipcodes[(postCode=="1041"?"1040":postCode)].commune;
            var popupTitleItsHere   = gettext('It is here');
            var popupTitle = gettext('Move the cursor');
            //var origX = response.result.point.x;
            //var origY= response.result.point.y;
            //console.log(x,y);
            //INJECTION
            if (!BACKOFFICE && response.result.address.street.postCode in zipcodes && !zipcodes[String(response.result.address.street.postCode)].participation) {
                //var popupContent = "<p>" + street + ", " + number;
                // Convert the point and url for google street view
                var popupContent = "<p class='popupMoveMe popupHeadingNonParticipating'>" + gettext('Non-participating municipality') + ".</p>";
                popupContent += "<p class='popupMoveMe popupContent'>" + gettext('Please contact the municipality') + ': '+ zipcodes[String(response.result.address.street.postCode)].phone + "</p>";
            } else {
                //var popupContent = "<p>" + street + ", " + number;
                // Convert the point and url for google street view
                var pointStreetView = UtilGeolocation.convertCoordinatesToWGS84(origX, y);
                var streetBiewLink = 'https://maps.google.be/maps?q=' + pointStreetView.y +','+ pointStreetView.origY +'&layer=c&z=17&iwloc=A&sll='+ pointStreetView.y + ',' + pointStreetView.x + '&cbp=13,240.6,0,0,0&cbll=' + pointStreetView.y + ',' + pointStreetView.x;
                var popupContent = "<p class='popupMoveMe popupHeading'>"+popupTitle+"</p>";
                popupContent += "<p class='popupMoveMe popupContent'>" + street + ", " + number;
                popupContent += "<br/>" + postCode + " " + municipality + "</p>";

                if (NEXT_PAGE_URL) {
                    popupContent +=
                    "<a class='btn-itshere' href='" + NEXT_PAGE_URL + "?x=" + origX + "&y=" + origY + "'>"+
                    popupTitleItsHere+
                    "</a>";
                }
                popupContent += '<div id="btn-streetview"><a href="' + streetBiewLink + '" target="_blank"><i class="icon-streetview"></i>Street View</a></div>';
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
        error:function(response)
        {
            // Error
            //~ var msg = 'Error: ' + response.status;
            //~ if(response.status == 'error') {
                //~ msg = 'Unable to locate this address';
            //~ }
        }
    });
}

function initDragMarker(x, y, additionalInfo, preventZoomIn) {
        cleanMap();

        // Remove message info
        var $map = $('#map');
        map.classList.remove("map-big-message");
        map.classList.add("map-big");

        var $proposalMessage = $('#proposal-message');
        $proposalMessage.slideUp();

        draggableMarker = fms.currentMap.addDraggableMarker(x, y);
        fms.currentMap.centerOnDraggableMarker();

        if (!preventZoomIn) {
            fms.currentMap.map.zoomTo(6);
        }

        var popupTitle = gettext('Move the cursor');
        var popupTitleItsHere   = gettext('It is here');
        var popupContent = "<p class='popupMoveMe popupHeading'>"+popupTitle+"</p>";

        if (additionalInfo) {
            popupContent += "<p class='popupMoveMe popupContent'>" + additionalInfo.streetName + ", " + additionalInfo.number;
            popupContent += "<br/>" + additionalInfo.postCode + " " + additionalInfo.municipality + "</p>";

            if (additionalInfo.number) {
                popupContent += "<a class='btn-itshere' href='" + NEXT_PAGE_URL + "?x=" + x + "&y=" + y + "'>"+popupTitleItsHere+"</a>";
                popupContent += '<div id="btn-streetview"><i class="icon-streetview"></i>Street View</div>';
            }
        }

        var popup = new OpenLayers.Popup(
            "popup",
            new OpenLayers.LonLat(x, y),
            new OpenLayers.Size(200,150),
            popupContent,
            true
        );
        popup.panMapIfOutOfView = true;

        fms.currentMap.map.addPopup(popup);
}

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

    // Hide results
    $proposalContainer = $('#proposal-container');
    $proposalContainer.slideUp();
}

var streetKeywords = document.getElementById('input-search');
var postalCode = document.getElementById('input-ward');
var searchBtn = document.getElementById('widget-search-button');

function enableSearch() {
    var enableSearchBtn = false;

    if (streetKeywords.value || postalCode.value) {
        enableSearchBtn = true;
    }

    searchBtn.disabled = !enableSearchBtn;
}

function municipalityChange() {
    enableSearch();
    fms.currentMap.centerOnMunicipality(postalCode.value);
    /*if ( !(streetKeywords.value) && (postalCode.value) ) {
        alert('middle of municipality : ' + postalCode.value);
    }*/
}
// Enable search button if one of fields contain a value
streetKeywords.addEventListener('keyup', enableSearch);
streetKeywords.addEventListener('change', enableSearch);
postalCode.addEventListener('change', enableSearch);





$(function(){

    var $searchStreet = $('#input-search');
    var $searchStreetNumber = $('#input-streetnumber');
    var $searchMunicipality = $('#input-ward');
    var $searchAddressForm = $('#search-address-form');
    var $searchTicketForm = $('#search-ticket-form');
    var $searchButton = $('#widget-search-button');
    var $searchTicketButton = $('#widget-search-ticket-button');
    var $proposal = $('#proposal');
    var $proposalContainer = $('#proposal-container');
    var $proposalMessage = $('#proposal-message');

    var $map = $('#map');
    $map.bind('markermoved',function(evt,point) {
        getAddressFromPoint(LANGUAGE_CODE, point.x, point.y);
    });

    /*$searchMunicipality.change(function(event){
        fms.currentMap.centerOnMunicipality($(this).val());
    });*/

    $searchTicketForm.submit(function(event){
        event.preventDefault();
        var searchValue = $('#input-ticket-search').val();

        if (searchValue && searchValue.length > 0) {
            //Get current language
            var currentLng = 'en';
            if (window.location.href.indexOf('/nl/') != -1) {
                currentLng = 'nl';
            } else if (window.location.href.indexOf('/fr/') != -1) {
                currentLng = 'fr';
            }
            if (window.location.href.indexOf('pro') != -1) {
                window.location = "/"+currentLng+"/pro/report/search?report_id="+searchValue;
            } else {
                window.location = "/"+currentLng+"/report/search?report_id="+searchValue;
            }
        }
    });


    $searchAddressForm.submit(function(event){
        event.preventDefault();

        paginationResults = 0;

        var searchValue = $searchStreet.val();
        var searchMunicipalityValue = $searchMunicipality.val();
        var searchStreetNumberValue = $searchStreetNumber.val();

        //If only municipality as input then center on it
        if (!searchValue && !searchStreetNumberValue && searchMunicipalityValue) {
            municipalityChange();
            return;
        }

        $proposalContainer.slideUp();

        if (!$searchStreet.val()) {
            $searchTicketForm.show();
            return;
        }

        var btnLocalizeviamap = document.getElementById('btn-localizeviamap');
        if (btnLocalizeviamap) {
            btnLocalizeviamap.parentNode.removeChild(btnLocalizeviamap);
        }

        $searchStreet.addClass('loading');
        $searchButton.prop('disabled',true);
        $.ajax({
            url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressesfields',
            dataType:'jsonp',
            data:{
                json:'{"language": "' + LANGUAGE_CODE + '",' +
                '"address": {' +
                    '"street": {' +
                        '"name": "' + $searchStreet.val().replace("\"","\\\"") + '",' +
                        '"postcode": "' + $searchMunicipality.val().replace("\"","\\\"") + '"' +
                    '},"number": "' + $searchStreetNumber.val() + '"' +
                '}}'
            }
        }).success(function(response){
            if(response.status == 'success' && response.result.length > 0)
            {
                var map = document.getElementById('map');
                var mapViewPort = document.getElementById('OpenLayers.Map_4_OpenLayers_ViewPort');

                cleanMap();

                $searchStreet.removeClass('loading');
                $searchButton.prop('disabled',false);
                $proposalMessage.empty();

                // Urbis response 1 result
                if(response.result.length == 1) {
                    var pos    = response.result[0].point;
                    var address = response.result[0].address;

                    additionalInfo = {
                        'streetName'   : address.street.name,
                        'number'       : address.number,
                        'postCode'     : address.street.postCode,
                        'municipality' : address.street.municipality
                    };

                    initDragMarker(pos.x, pos.y, additionalInfo);

                    map.classList.remove("map-big-message");
                    map.classList.add("map-big");
                }
                // Urbis response many results
                else {
                    features = [];

                    results = response.result;
                    document.getElementById('numberResults').innerHTML = results.length;

                    if (!fms.currentMap.homepageMarkersLayer) {
                        // Create vector layer
                        fms.currentMap.homepageMarkersLayer = new OpenLayers.Layer.Vector("Overlay", {
                            displayInLayerSwitcher: false
                        });

                        // Add layer to map
                        fms.currentMap.map.addLayer(fms.currentMap.homepageMarkersLayer);

                        // Function to bind selector to initDragMarker
                        function bindClick(feature) {
                            var x = feature.geometry.x;
                            var y = feature.geometry.y;

                            initDragMarker(x, y, feature.attributes.additionalInfo);
                        }

                        // Add the selector control to the vectorLayer
                        var clickCtrl = new OpenLayers.Control.SelectFeature(fms.currentMap.homepageMarkersLayer, { onSelect: bindClick });
                        fms.currentMap.map.addControl(clickCtrl);
                        clickCtrl.activate();
                    }

                    renderResults();

                }
            }
            else
            {
                $searchTicketForm.show();
                $searchStreet.removeClass('loading');
                $searchButton.prop('disabled',false);
                if(response.status == "noresult" || response.status == "success")
                {
                    $proposalMessage.html('<span class="error-msg">' + gettext('No corresponding address has been found') + '.</span>').slideDown();
                }
                else
                {
                    $proposalMessage.html('<span class="error-msg">' + response.status + '</span>').slideDown();
                }
            }
        }).error(function(xhr,msg,error){
            $searchStreet.removeClass('loading');
            $searchButton.prop('disabled',false);

            $proposalMessage.html('<span class="error-msg">' + gettext('Unexpected error') + '.</span>').slideDown();
        });
    });

    $searchAddressForm.submit();
});

// Localize report with map
(function() {

    var btnLocalizeviamap = document.getElementById('btn-localizeviamap');

    btnLocalizeviamap.addEventListener("click", function(evt) {
        evt.preventDefault();
        var center = fms.currentMap.map.getCenter();
        // Hard code center of map
        initDragMarker(center.lon, center.lat, null, true);

        btnLocalizeviamap.parentNode.removeChild(btnLocalizeviamap);
    });

})(document);
