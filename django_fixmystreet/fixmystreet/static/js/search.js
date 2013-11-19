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
                $searchTicketForm.hide();
                if(response.result.length == 1)
                {
                    var pos = response.result[0].point;
                    window.location.assign(NEXT_PAGE_URL + '?x=' + pos.x + '&y=' + pos.y);
                }
                else
                {
                    $searchStreet.removeClass('loading');
                    $searchButton.prop('disabled',false);
                    $proposal.empty();
                    $proposalMessage.empty();
                    var markers = [];

                    for(var i in response.result)
                    {
                        var street = response.result[i].address.street;
                        var pos = response.result[i].point;
                        $('<a class="street button" href="' + NEXT_PAGE_URL + '?x=' + pos.x + '&y=' + pos.y + '">' + street.name + '<br/><strong>' +street.postCode + ' ' + street.municipality + '</strong></a>')
                            .appendTo($proposal)
                            .wrap('<li />');

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
                    fms.currentMap.markersLayer.removeAllFeatures();
                    fms.currentMap.markersLayer.addFeatures(markers);
                    fms.currentMap.map.zoomTo(3);
                    fms.currentMap.map.updateSize();

                    // Enlarge map viewport
                    var map = document.getElementById('map');
                    var mapViewPort = document.getElementById('OpenLayers.Map_4_OpenLayers_ViewPort');
                    mapViewPort.classList.add("olMapViewport-big");

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

    function enableSearch() {
        var enableSearchBtn = false;

        if (this.value) {
            enableSearchBtn = true;
        } else {
            enableSearchBtn = enableSearchBtn || false;
        }

        document.getElementById('widget-search-button').disabled = !enableSearchBtn;
    }
    // Enable search button if one of fields contain a value
    document.getElementById('input-search').addEventListener('keyup', enableSearch);
    document.getElementById('input-search').addEventListener('change', enableSearch);
    document.getElementById('input-ward').addEventListener('change', enableSearch);

})(document);
