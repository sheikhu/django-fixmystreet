{% load i18n %}
<script type="text/javascript" src="http://www.google.com/jsapi?key={{GOOGLE_KEY}}"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/jquery-ui.min.js"></script>

<script type="text/javascript">
//<![CDATA[
google.load("maps", "2.167");
jQuery.noConflict();

function url_for_geodata(geodata)
{
   return "/search" + "?lat=" + geodata.Point.coordinates[1] + "&lon=" + geodata.Point.coordinates[0];    	
}
    
function html_for_multiple_matches(array) 
{
  	var html = "<div id='error-msg'>";
  	html += '<p>{% trans "That address returned more than one result.  Please try again, or select an option below:"%}</p>';
   	html += '<ul>';
	for (var i=0; i<array.length; i++)
	{
	    html += '<li><a href="';
	    html += url_for_geodata( array[i] );
	    html += '">';
	    html += array[i].address;
	    html += '</a></li>';
	}
	html += '</ul>';
    html += '</div>'

    jQuery("#search-error").html(html).fadeIn(1000);
}
/*
function filter_matches(array) 
{
    var cp = array.slice(0); // clone the original array and iterate it from the end to avoid index modification
    for (var i=array.length-1; i>=0; i--)
    {
	if(!array[i].AddressDetails.Country
		|| array[i].AddressDetails.Country.CountryNameCode != 'BE'
		(||!array[i].AddressDetails.Country.AdministrativeArea
		||!array[i].AddressDetails.Country.AdministrativeArea.AdministrativeAreaName.contains('Brussels'))
	){ // check if inside BXL
	    cp.splice(i,1);
	}
    }
    return cp;
}*/

function html_for_no_results()
{
    var html = "<div id='error-msg'>";
    html += '<p>{% trans "Sorry, we couldn\\\'t find the address you entered. Please try again with another intersection, address or postal code, or add the name of the city to the end of the search."%}</p>';
    html += '</div>';
    console.log(html);
    jQuery("#search-error").html(html).fadeIn();
}

 
function handle_google_geocode_response(geodata)
{
    if ((geodata.Status.code == 200))
    {
	var matches = geodata.Placemark;
      	if ( matches && matches.length  > 1)
       	{
	    html_for_multiple_matches(matches);   		
       	}
	else if(matches && matches.length > 0 )
	{
	    var url = url_for_geodata(matches[0]);
	    document.location.assign(url);
	}
	else
	{
	    html_for_no_results();
	}
    }
    else
    {
	html_for_no_results();
    }
}
    
    
function do_search(search_term, ward)
{
    /*
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
    jQuery.ajax({
	url:'/api/locate/',
	type:'POST',
	contentType:'json',
	data:JSON.stringify(query),
	success:function(response){
	    console.log('success',response);
	},
	error:function(){
	    console.log('error',arguments);
	}
    });
    */
    if(search_term){
	var geocoder = new  GClientGeocoder();
	geocoder.setViewport(new GLatLngBounds(new GLatLng(50.899944,4.257545), new GLatLng(50.772236,4.493408)));
	geocoder.getLocations(search_term + " Brussels Belgium", handle_google_geocode_response);
    }
    
}


jQuery(document).ready(function($) 
{

    jQuery("#search_form").submit(function(event){
	event.preventDefault();
	var search_term = jQuery('#search_box').val();
	//var search_ward = jQuery('#search_ward').val();
	do_search(search_term);//,search_ward);
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
//]]>
</script>