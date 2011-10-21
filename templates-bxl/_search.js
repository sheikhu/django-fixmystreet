{% load i18n %}

<script type="text/javascript">
//<![CDATA[
$(function(){

    var $searchTerm = $('#search_box');
    var $searchWard = $('#search_ward');
    var $searchForm = $('#search_form');
    var $searchButton = $('#search_button');
	var $proposal = $('#proposal');


    $searchForm.submit(function(event){
		event.preventDefault();
		
		$proposal.slideUp();
		$searchTerm.addClass('loading');
		$searchButton.prop('disabled',true);
		
		$.ajax({

			url:'/api/search/',
			type:'POST',
			contentType:'text/json',
			dataType:'json',
			data:JSON.stringify({
				"language": "{{ LANGUAGE_CODE }}",
				"address": {
					"street": {
						"name": $searchTerm.val(),
						"postcode": $searchWard.val()
					},
					"number": ""
				}
			}),
			success:function(response){
				if(response.status == 'success' && response.result.length > 0)
				{
					if(response.result.length == 1)
					{
						window.location.assign(resToHref(response.result[0]));
					}
					else
					{
						$searchTerm.removeClass('loading');
						$searchButton.prop('disabled',false);
						$proposal.empty();
						for(var i in response.result)
						{
							var street = response.result[i].address.street;
							$proposal.append('<p><a href="' + resToHref(response.result[i]) + '">' + street.name + ' (' + street.postCode + ')</a></p>');
						}
						$proposal.slideDown();
					}
					// window.location.assign('/reports/new?lon=' + response.result.point.x + '&lat=' + response.result.point.y);
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
			},
			error:function(){
				$searchTerm.removeClass('loading');
				$searchButton.prop('disabled',false);
		
				$proposal.html('<p class="error-msg">Unexpected error.</p>');
			}
		});
    });
    
	function resToHref(res)
	{
		return '/reports/new?lon=' + res.point.x + '&lat=' + res.point.y;
	}

    {% if location %}
	$searchForm.submit();
    {% endif %}

});
//]]>
</script>