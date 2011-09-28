{% load i18n %}
<script type="text/javascript" src="http://openlayers.org/dev/OpenLayers.js"></script>

<script type="text/javascript">
//<![CDATA[
(function(){	
    function do_search(search_term, ward)
    {
	
	var query = {
	    "language": "fr",
	    "address": {
		"street": {
		    "name": search_term,
		    "postcode": ward
		},
		"number": "1"
	    }
	};
	$.ajax({
	    url:'/api/locate/',
	    type:'POST',
	    contentType:'json',
	    dataType:'json',
	    data:JSON.stringify(query),
	    success:function(response){
		if(response.status == 'success')
		{
		    document.location.assign('/reports/new?lon=' + response.result.point.x + '&lat=' + response.result.point.y + '&address=' + search_term + '&postalcode=' + ward);
		    // openMap(response.result.point);
		}
	    },
	    error:function(){
		console.log(arguments);
	    }
	});
    }
    
    
    $(document).ready(function($) 
    {
    
	$("#search_form").submit(function(event){
	    event.preventDefault();
	    var search_term = $('#search_box').val();
	    var search_ward = $('#search_ward').val();
	    do_search(search_term,search_ward);
	});
    
    {% if location %}
       
	function find_nearby_reports()
	{
	    var query = "{{location|escapejs}}";
	    do_search(query);
	}
    
	find_nearby_reports();
    {% endif %}
    
    });
}());
//]]>
</script>