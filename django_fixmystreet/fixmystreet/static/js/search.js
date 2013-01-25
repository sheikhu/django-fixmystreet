$(function(){

    var $searchTerm = $('#input-search');
    var $searchWard = $('#input-ward');
    var $searchForm = $('.search-form');
    var $searchButton = $('#widget-search-button');
    var $searchTicketButton = $('#widget-search-ticket-button');
    var $proposal = $('#proposal');
    
    $searchTicketButton.click(function(event){
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
				window.location = "/"+currentLng+"/pro/report/search_ticket_pro?report_id="+searchValue.substring(1);
			} else {
				window.location = "/"+currentLng+"/report/search_ticket?report_id="+searchValue.substring(1);
			}
		}
    });


    $searchForm.submit(function(event){
		event.preventDefault();
		var searchValue = $searchTerm.val();
			$proposal.slideUp();

			if (!$searchTerm.val()) { 
				$("#ticket-div-section").show();
				return; 
			}

			$searchTerm.addClass('loading');
			$searchButton.prop('disabled',true);
                        $.ajax({
				url: URBIS_URL + 'service/urbis/Rest/Localize/getaddressesfields',
				dataType:'jsonp',
				data:{
					json:'{"language": "' + LANGUAGE_CODE + '",' +
					'"address": {' +
						'"street": {' +
							'"name": "' + $searchTerm.val().replace("\"","\\\"") + '",' +
							'"postcode": "' + $searchWard.val().replace("\"","\\\"") + '"' +
						'},"number": ""' +
					'}}'
				}
			}).success(function(response){
				if(response.status == 'success' && response.result.length > 0)
				{
					$("#ticket-div-section").hide();
					if(response.result.length == 1)
					{
						var pos = response.result[0].point;
						window.location.assign(NEXT_PAGE_URL + '?x=' + pos.x + '&y=' + pos.y);
					}
					else
					{
						$searchTerm.removeClass('loading');
						$searchButton.prop('disabled',false);
						$proposal.empty();
						for(var i in response.result)
						{
							var street = response.result[i].address.street;
							var pos = response.result[i].point;
							$('<a class="street button" href="' + NEXT_PAGE_URL + '?x=' + pos.x + '&y=' + pos.y + '">' + street.name + ' (' + street.municipality + ')</a>')
								.appendTo($proposal)
								.wrap('<li />');
						}
						$proposal.slideDown();
					}
				}
				else
				{
					$("#ticket-div-section").show();
					$searchTerm.removeClass('loading');
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
				console.log(arguments);
				console.log(error.message);
				$searchTerm.removeClass('loading');
				$searchButton.prop('disabled',false);

				$proposal.html('<p class="error-msg">Unexpected error.</p>').slideDown();
			});
    });

    $searchForm.submit();
});
