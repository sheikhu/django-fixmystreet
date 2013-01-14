
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

    fms.currentMap.bind('reportselected', function(evt, point, report){
    	window.location.assign('/reports/' + report.id);
    });

    retrieveAddress();

    function retrieveAddress() {
    	$form.find('.error-msg').remove();
    	$form.find(':submit').prop('disabled',true);
    	$('#address-text').addClass('loading');

    	fms.currentMap.getSelectedAddress(function(response) {
    		$('#address-text').removeClass('loading');

    		if(response.status == 'success') {
                var postcode = response.result.address.street.postCode;
    			$('#id_report-postalcode').val(postcode);
    			$('#id_report-address').val(response.result.address.street.name);
    			$('#id_report-address_number').val(response.result.address.number);

                $('#address-text').html(response.result.address.street.name+ ', ' + response.result.address.number);
                $('#postcode-text').html(postcode);

				if (!(postcode in available_zipcodes)) {
	                //This commune does not participate to fixmystreet until now.
	                $form.find(':submit').prop('disabled',true);
	                alert(available_zipcodes_msg);
	                return false;
		        }

    			$form.find(':submit').prop('disabled',false);
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
    }
});

function checkFileFieldValue(){
	if($("#id_file").val() == ""){
		alert("Please select a file to add.");
		return false;
	}
}

