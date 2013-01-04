$(function(){

    var $searchTerm = $('#input-search');
    var $searchWard = $('#input-ward');
    var $searchForm = $('#search-form');
    var $searchButton = $('#search-form :submit');
	var $proposal = $('#proposal');


    $searchForm.submit(function(event){
		event.preventDefault();

		var searchValue = $searchTerm.val();

		//If search a ticket then redirect
		if (searchValue && searchValue.length > 0 && searchValue[0] == "#") {
			window.location = "report/search_ticket?report_id="+searchValue.substring(1);
		} else {
			$proposal.slideUp();

			if (!$searchTerm.val()) { return; }

			$searchTerm.addClass('loading');
			$searchButton.prop('disabled',true);

			$.ajax({
				url: SERVICE_GIS_URL + '/urbis/Rest/Localize/getaddressesfields',
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
		}
    });

    $searchForm.submit();
});
