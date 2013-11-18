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
        $proposalMessage.slideUp();

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

                        if ($searchMunicipality.val()) {
                            $proposalMessage.html("Cette rue n'est pas répertoriée dans cette commune");
                            $proposalMessage.slideDown();
                        } else if ($searchStreet.val().toLowerCase() == street.name.toLowerCase()) {
                            $proposalMessage.html("Cette rue existe dans plusieurs communes, merci de préciser");
                            $proposalMessage.slideDown();
                        }
                    }
                    // Add markers to the map
                    fms.currentMap.markersLayer.addFeatures(markers);

                    // Enlarge map viewport
                    var map = document.getElementById('map');
                    var mapViewPort = document.getElementById('OpenLayers.Map_4_OpenLayers_ViewPort');
                    map.classList.add("map-big");
                    mapViewPort.classList.add("olMapViewport-big");

                    $proposal.slideDown();
                }
            }
            else
            {
                $searchTicketForm.show();
                $searchStreet.removeClass('loading');
                $searchButton.prop('disabled',false);
                if(response.status == "noresult" || response.status == "success")
                {
                    $proposal.html('<p class="error-msg">No corresponding address has been found</p>').slideDown();
                }
                else
                {
                    $proposal.html('<p class="error-msg">' + response.status + '</p>').slideDown();
                }
            }
        }).error(function(xhr,msg,error){
            $searchStreet.removeClass('loading');
            $searchButton.prop('disabled',false);

            $proposal.html('<p class="error-msg">Unexpected error.</p>').slideDown();
        });
    });

    $searchAddressForm.submit();
});

(function() {

    function enableSearch() {
        var enableSearchBtn = false;

        for (var i=0, length=this.elements.length; i<length; i++) {
            if ( (this.elements[i].id != "widget-search-button") && (this.elements[i].value) ) {
                enableSearchBtn = true;
            } else {
                enableSearchBtn = enableSearchBtn || false;
            }
        }

        document.getElementById('widget-search-button').disabled = !enableSearchBtn;
    }
    // Enable search button if one of fields contain a value
    document.getElementById('search-address-form').addEventListener('keyup', enableSearch);
    document.getElementById('search-address-form').addEventListener('change', enableSearch);

})(document);
