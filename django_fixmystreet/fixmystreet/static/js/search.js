function AddressResult(x, y, address)
{
    var self = this;

    this.x = x;
    this.y = y;
    this.el = document.createElement('li');

    this.address = address;

    this.render = function() {
        this.el.innerHTML = '<p>' + this.address.street.name +
                            '<br/>' +
                            '<strong>' + this.address.street.postCode + ' ' + this.address.street.municipality + '</strong>' +
                            '</p>';
        this.el.addEventListener('click', this.onclick);
        return  this.el;
    };

    this.onclick = function(event) {
        cleanMap();

        additionalInfo = {
            'streetName'   : self.address.street.name,
            'number'       : self.address.number,
            'postCode'     : self.address.street.postCode,
            'municipality' : self.address.street.municipality
        }

        initDragMarker(self.x, self.y, additionalInfo);
    }
}

function getAddressFromPoint(lang, x, y) {
    var self = this;
    $.ajax({
        url: 'http://service.gis.irisnet.be/urbis/Rest/Localize/getaddressfromxy',
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
            var municipality = zipcodes[postCode].commune;

            var x = response.result.point.x;
            var y = response.result.point.y;

            var popupContent = "<p>" + street + ", " + number;
            popupContent += "<br/>" + postCode + " " + municipality + "</p>";
            popupContent += "<a href='" + NEXT_PAGE_URL + "?x=" + x + "&y=" + y + "'>C'est ici !</a>";
            popupContent += '<div id="btn-streetview"><a href="/report/newmap/"><i class="icon-streetview"></i>Street View</a></div>';

            var popup = new OpenLayers.Popup(
                "popup",
                new OpenLayers.LonLat(x, y),
                new OpenLayers.Size(200,100),
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

function initDragMarker(x, y, additionalInfo) {
        // Remove message info
        var $map = $('#map');
        map.classList.remove("map-big-message");
        map.classList.add("map-big");

        var $proposalMessage = $('#proposal-message');
        $proposalMessage.slideUp();

        var draggableMarker = fms.currentMap.addDraggableMarker(x, y);
        fms.currentMap.centerOnDraggableMarker();
        fms.currentMap.map.zoomTo(6);

        var popupContent = "<p>Déplacez-moi à l'adresse exacte</p>";

        if (additionalInfo) {
            popupContent += "<p>" + additionalInfo.streetName + ", " + additionalInfo.number;
            popupContent += "<br/>" + additionalInfo.postCode + " " + additionalInfo.municipality + "</p>";

            if (additionalInfo.number) {
                popupContent += "<a href='" + NEXT_PAGE_URL + "?x=" + x + "&y=" + y + "'>C'est ici !</a>";
                popupContent += '<div id="btn-streetview"><a href="/report/newmap/"><i class="icon-streetview"></i>Street View</a></div>';
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
    var $proposal = $('#proposal');
    $proposal.slideUp();
}

$(function(){

    var $searchStreet = $('#input-search');
    var $searchStreetNumber = $('#input-streetnumber');
    var $searchMunicipality = $('#input-ward');
    var $searchAddressForm = $('#search-address-form');
    var $searchTicketForm = $('#search-ticket-form');
    var $searchButton = $('#widget-search-button');
    var $searchTicketButton = $('#widget-search-ticket-button');
    var $proposal = $('#proposal');
    var $proposalMessage = $('#proposal-message');

    var $map = $('#map');
    $map.bind('markermoved',function(evt,point) {
        getAddressFromPoint(LANGUAGE_CODE, point.x, point.y);
    });

    $searchTicketForm.submit(function(event){
        event.preventDefault();
        var searchValue = $('#input-ticket-search').val();

        if (searchValue && searchValue.length > 0) {
            //Get current language
            var currentLng = 'en';
            if (window.location.href.indexOf('/nl/') != -1) {
                currentLng = 'nl';
            } else if (window.location.href.indexOf('/fr/') != -1) {
                currentLng = 'fr'
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
        var searchValue = $searchStreet.val();
        $proposal.slideUp();

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
                $proposal.empty();
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
                    }

                    initDragMarker(pos.x, pos.y, additionalInfo);

                    map.classList.remove("map-big-message");
                    map.classList.add("map-big");
                }
                // Urbis response many results
                else {
                    var features = [];

                    fms.currentMap.homepageMarkersLayer = new OpenLayers.Layer.Vector("Overlay");

                    for(var i in response.result) {
                        var address = response.result[i].address;
                        var pos = response.result[i].point;

                        var newAddress = new AddressResult(pos.x, pos.y, address);
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
                                }
                            );
                        features.push(feature);

                        // Define message if needed
                        if ($searchMunicipality.val()) {
                            $proposalMessage.html("Cette rue n'est pas répertoriée dans cette commune");
                        } else if ($searchStreet.val().toLowerCase() == address.street.name.toLowerCase()) {
                            $proposalMessage.html("Cette rue existe dans plusieurs communes, merci de préciser");
                        }
                    }

                    // Add features to layer
                    fms.currentMap.homepageMarkersLayer.addFeatures(features);

                    // Zoom to markers
                    var markersBound = fms.currentMap.homepageMarkersLayer.getDataExtent();
                    fms.currentMap.map.zoomToExtent(markersBound);

                    // Add layer to map
                    fms.currentMap.map.addLayer(fms.currentMap.homepageMarkersLayer);

                    // Function to bind selector to initDragMarker
                    function bindClick(feature) {
                        var x = feature.geometry.x;
                        var y = feature.geometry.y;

                        cleanMap();
                        initDragMarker(x, y, feature.attributes.additionalInfo);
                    }

                    // Add the selector control to the vectorLayer
                    var clickCtrl = new OpenLayers.Control.SelectFeature(fms.currentMap.homepageMarkersLayer, { onSelect: bindClick });
                    fms.currentMap.map.addControl(clickCtrl);
                    clickCtrl.activate();

                    // Show/hide proposal and message
                    $proposal.slideDown();

                    if ($proposalMessage.html()) {
                        map.classList.add("map-big-message");
                        $proposalMessage.slideDown();
                    } else {
                        map.classList.remove("map-big-message");
                        map.classList.add("map-big");
                        $proposalMessage.slideUp();
                    }

                }

                // Enlarge map viewport
                mapViewPort.classList.add("olMapViewport-big");
            }
            else
            {
                $searchTicketForm.show();
                $searchStreet.removeClass('loading');
                $searchButton.prop('disabled',false);
                if(response.status == "noresult" || response.status == "success")
                {
                    $proposalMessage.html('<span class="error-msg">No corresponding address has been found</span>').slideDown();
                }
                else
                {
                    $proposalMessage.html('<span class="error-msg">' + response.status + '</span>').slideDown();
                }
            }
        }).error(function(xhr,msg,error){
            $searchStreet.removeClass('loading');
            $searchButton.prop('disabled',false);

            $proposalMessage.html('<span class="error-msg">Unexpected error.</span>').slideDown();
        });
    });

    $searchAddressForm.submit();
});

(function() {

    var streetKeywords = document.getElementById('input-search');
    var postalCode = document.getElementById('input-ward');
    var searchBtn = document.getElementById('widget-search-button')

    function enableSearch() {
        var enableSearchBtn = false;

        if (streetKeywords.value) {
            enableSearchBtn = true;
        }

        searchBtn.disabled = !enableSearchBtn;
    }

    function municipalityChange() {
        enableSearch();

        if ( !(streetKeywords.value) && (postalCode.value) ) {
            alert('middle of municipality : ' + postalCode.value);
        }
    }
    // Enable search button if one of fields contain a value
    streetKeywords.addEventListener('keyup', enableSearch);
    streetKeywords.addEventListener('change', enableSearch);
    postalCode.addEventListener('change', municipalityChange);

})(document);
