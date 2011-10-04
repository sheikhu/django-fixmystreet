{% load i18n %}

<script type="text/javascript">
//<![CDATA[
$(function(){

    var $searchTerm = $('#search_box');
    var $searchWard = $('#search_ward');
    var $searchForm = $('#search_form');
    var $searchButton = $('#search_button');
    

    $searchForm.submit(function(event){
		event.preventDefault();
		
		$searchForm.find('.error-msg').remove();
		$searchTerm.addClass('loading');
		$searchButton.prop('disabled',true);
		
		$.ajax({
			url:'/api/locate/',
			type:'POST',
			contentType:'json',
			dataType:'json',
			data:JSON.stringify({
			"language": "fr",
			"address": {
				"street": {
				"name": $searchTerm.val(),
				"postcode": $searchWard.val()
				},
				"number": ""
			}
			}),
			success:function(response){
				if(response.status == 'success')
				{
					document.location.assign('/reports/new?lon=' + response.result.point.x + '&lat=' + response.result.point.y);// + '&address=' + $searchTerm.val());
					// openMap(response.result.point);
				}
				else
				{
					$searchTerm.removeClass('loading');
					$searchButton.prop('disabled',false);
					if(response.status == "noresult")
					{
						$searchForm.prepend('<p class="error-msg">No corresponding address has been found</p>');
					}
					else
					{
						$searchForm.prepend('<p class="error-msg">' + response.status + '</p>');
					}
				}
			},
			error:function(){
				$searchTerm.removeClass('loading');
				$searchButton.prop('disabled',false);
		
				$searchForm.prepend('<p class="error-msg">Unexpected error.</p>');
				console.log(arguments);
			}
		});
    });
    
    
    
    {% if location %}
       $searchForm.submit();
    {% endif %}

});
//]]>
</script>