
$(document).ready(function() {

    var $form = $('#report-form');
    var $map = $('#map');

    function markerMoved (point) {
        $('#id_report-x').val(point.x);
        $('#id_report-y').val(point.y);

        window.location.assign('#x=' + point.x + '&y=' + point.y);

        retrieveAddress();

    }

	$map.one('markerdrag click movestart zoomend',function(evt,point){
		$('#cursor-instructions').fadeOut();
	});

    //On page load: The report overview needs to be hidden
    $('#report_overview_table_div').hide();
    $map.bind('markermoved',function(evt,point) {
		markerMoved(point);
	});

    $(fms.currentMap).bind('reportselected', function(evt, point, report){
    	window.location.assign('/reports/' + report.id);
    });

    retrieveAddress();

    function retrieveAddress() {
    	$form.find('.error-msg').remove();
    	$form.find(':submit').prop('disabled',true);
    	$('#address-text').addClass('loading');

    	fms.currentMap.getSelectedAddressNL(function(response) {
    		$('#address-text').removeClass('loading');

    		if(response.status == 'success') {
                var postcode = response.result.address.street.postCode;
    			$('#id_report-postalcode').val(postcode);
    			$('#id_report-address_nl').val(response.result.address.street.name);
    			$('#id_report-address_number').val(response.result.address.number);
                if(fms.currentMap.options.apiLang == "nl"){
                    $('#address-text').html(response.result.address.street.name+ ', ' + response.result.address.number);
                }
                $('#postcode-text').html(postcode);

		if (!(postcode in available_zipcodes)) {
	            //This commune does not participate to fixmystreet until now.
	            $("#validate_form_button").attr("disabled","disabled");
                    $("#validate_form_button").attr("onclick","return false;");
	                alert(zipcode_availability_msg_prefix+available_zipcodes_msg[postcode+""].name+"("+available_zipcodes_msg[postcode+""].phone+")"+"\n\n"+bxl_mobility_msg);
	                return false;
	        }
    		$("#validate_form_button").removeAttr("disabled");
                $("#validate_form_button").removeAttr("onclick");

		//Search if the address is on a regional road or not.
		var pointX = $('#id_report-x').val();
		var pointY = $('#id_report-y').val();
 		//Default False
                $('#id_report-address_regional').val('False');
		$.ajax({
                	url: "http://gis.irisnet.be/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=urbis:URB_A_SS&maxFeatures=1&outputFormat=json&bbox="+(pointX-30)+","+(pointY-30)+","+(pointX+30)+","+(pointY+30),
                        dataType: "json",
                        type: "POST",
                        success: function(responseData, textStatus, jqXHR) {
                        	if (responseData.features[0].properties.ADMINISTRATOR != null) {
					//ROUTE REGIONALE
                                	$('#id_report-address_regional').val('True');
				}
			}
		});
    		}
    		else
    		{
    			var msg = 'Error: ' + response.status;
    			if(response.status == 'error')
    			{
    				msg = 'Unable to locate this address';
    			}
    			$('#id_report-address').removeClass('loading');
    			$('#id_report-address').after('<p class="error-msg">' + msg + '</p>');
    		}
    	});

        fms.currentMap.getSelectedAddressFR(function(response) {
            $('#id_report-address_fr').val(response.result.address.street.name);
            if(fms.currentMap.options.apiLang == "fr"){
                    $('#address-text').html(response.result.address.street.name+ ', ' + response.result.address.number);
            }
        });
    }
});

function checkFileFieldValue(){
	if($("#id_file").val() == ""){
		alert("Please select a file to add.");
		return false;
	}
}

