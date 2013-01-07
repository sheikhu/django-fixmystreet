
$(document).ready(function() {
	// Redefine the submit function for the add ReportFile form
	$("#fileForm").submit(function(evt) {
        evt.preventDefault();

		//Define a new FormData, in this object the file(s) will be saved

        // !!!!!!!!!!!!!!!!!!!!!!! FormData not supported before ie 10 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        // https://developer.mozilla.org/en-US/docs/DOM/XMLHttpRequest/FormData
		var data = new FormData();
		$.each($("#fileForm #id_file")[0].files, function(i, file) {
			//For each file in the file input field append the file to the FormData
			data.append('file',file);
		});
		//Process the data by sending it using ajax.
		$.ajax({
			data: data,
			type: $(this).attr('method'),
			url: $(this).attr('action'),
			processData: false,
			contentType: false,
			success: function(response) {
                //Nothing to be done
            }
        });
    });

    var $form = $('#report_form');
    var $map = $('#map');

    function markerMoved (point) {
        $('#id_x').val(point.x);
        $('#id_y').val(point.y);

        window.location.assign('#x=' + point.x + '&y=' + point.y);
        $("#addFileDiv").show();
        $("#addCommmentDiv").show();

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

    $map.bind('reportselected', function(evt, point, report){
    	window.location.assign('/reports/' + report.id);
    });
});

function retrieveAddress()
    {
    	var $form = $('#report_form');
    	$form.find('.error-msg').remove();
    	$form.find(':submit').prop('disabled',true);
    	$('#id_address').addClass('loading');

    	fms.currentMap.getSelectedAddress(function(response)
    	{
    		$('#id_address').removeClass('loading');

    		if(response.status == 'success')
    		{
    			$('#id_postalcode').val(response.result.address.street.postCode);
    			$('#id_address').val(response.result.address.street.name+ ', ' + response.result.address.number);
    			$('#id_address_number').val(response.result.address.number);

				if ($('#available_zipcodes option[value="'+$('#id_postalcode').val()+'"]').length == 0) {
		                	//This commune does not participate to fixmystreet until now.
		                	$form.find(':submit').prop('disabled',true);
		                	alert("{% trans 'This_commune_does_not_participate' %}: "+$('#available_zipcodes_as_string').html());
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
    			$('#id_address').removeClass('loading');
    			$('#id_address').after('<p class="error-msg">' + msg + '</p>');
    		}
    	});
    }

function checkFileFieldValue(){
	if($("#id_file").val() == ""){
		alert("Please select a file to add.");
		return false;
	}
}

