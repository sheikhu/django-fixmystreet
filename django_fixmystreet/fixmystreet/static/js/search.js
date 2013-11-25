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

        var popupContent = "";
        popupContent = "<p>" + self.address.street.name + ", " + self.address.number;
        popupContent += "<br/>" + self.address.street.postCode + " " + self.address.street.municipality + "</p>";

        if (address.number) {
            popupContent += "<a href='" + NEXT_PAGE_URL + "?x=" + self.x + "&y=" + self.y + "'>C'est ici !</a>";
        }

        initDragMarker(self.x, self.y, popupContent);
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
            var municipality = response.result.address.street.municipality;

            var x = response.result.point.x;
            var y = response.result.point.y;

            var popupContent = "<p>" + street + ", " + number;
            console.log(zipcodes);
            popupContent += "<br/>" + postCode + " " + zipcodes[postCode].commune + "</p>";
            popupContent += "<a href='" + NEXT_PAGE_URL + "?x=" + x + "&y=" + y + "'>C'est ici !</a>";

            var popup = new OpenLayers.Popup(
                "popup",
                new OpenLayers.LonLat(x, y),
                new OpenLayers.Size(200,75),
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
        var draggableMarker = fms.currentMap.addDraggableMarker(x, y);
        fms.currentMap.centerOnDraggableMarker();
        fms.currentMap.map.zoomTo(6);

        var popupContent = "<p>Déplacez-moi à l'adresse exacte</p>";

        if (additionalInfo) {
            popupContent += additionalInfo;
        }

        var popup = new OpenLayers.Popup(
            "popup",
            new OpenLayers.LonLat(x, y),
            new OpenLayers.Size(200,120),
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

    // Hide results
    var $proposalContainer = $('#proposal-container');
    $proposalContainer .slideUp();
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
    var $proposalContainer = $('#proposal-container');
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
        $proposalContainer.slideUp();

        if (!$searchStreet.val()) {
            $searchTicketForm.show();
            return;
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

                if(response.result.length == 1) {
                    var pos    = response.result[0].point;
                    var address = response.result[0].address;

                    var popupContent = "";
                    popupContent = "<p>" + address.street.name + ", " + address.number;
                    popupContent += "<br/>" + address.street.postCode + " " + address.street.municipality + "</p>";

                    if (address.number) {
                        popupContent += "<a href='" + NEXT_PAGE_URL + "?x=" + pos.x + "&y=" + pos.y + "'>C'est ici !</a>";
                    }

                    initDragMarker(pos.x, pos.y, popupContent);

                    map.classList.remove("map-big-message");
                    map.classList.add("map-big");
                }
                else {
                    $searchStreet.removeClass('loading');
                    $searchButton.prop('disabled',false);
                    $proposal.empty();
                    $proposalMessage.empty();
                    var markers = [];

                    for(var i in response.result) {
                        var street = response.result[i].address.street;
                        var pos = response.result[i].point;

                        var newAddress = new AddressResult(pos.x, pos.y, response.result[i].address);
                        $proposal.append(newAddress.render());

                        // Create marker for this address
                        markers.push(fms.currentMap.addReport(response.result[i], i));

                        // Define message if needed
                        if ($searchMunicipality.val()) {
                            $proposalMessage.html("Cette rue n'est pas répertoriée dans cette commune");
                        } else if ($searchStreet.val().toLowerCase() == street.name.toLowerCase()) {
                            $proposalMessage.html("Cette rue existe dans plusieurs communes, merci de préciser");
                        }
                    }
                    // Add markers to the map
                    fms.currentMap.markersLayer.addFeatures(markers);
                    //~ fms.currentMap.map.zoomTo(3);
                    //~ fms.currentMap.map.updateSize();

                    // Zoom to markers
                    var markersBound = fms.currentMap.markersLayer.getDataExtent();
                    fms.currentMap.map.zoomToExtent(markersBound);
                    // Harcode zoom because getDataExtent set zoom to max :(
                    //~ fms.currentMap.map.zoomTo(7);
                }

                // Enlarge map viewport
                mapViewPort.classList.add("olMapViewport-big");

                // If many results only
                if (markers) {
                    // Show/hide proposal and message
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

        if ( (streetKeywords.value) || (postalCode.value) ) {
            enableSearchBtn = true;
        }

        searchBtn.disabled = !enableSearchBtn;
    }
    // Enable search button if one of fields contain a value
    streetKeywords.addEventListener('keyup', enableSearch);
    streetKeywords.addEventListener('change', enableSearch);
    postalCode.addEventListener('change', enableSearch);

})(document);
