
$(document).ready(function() {
	// Redefine the submit function for the add ReportFile form
	$("#fileForm").submit(function(){
		//Define a new FormData, in this object the file(s) will be saved
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
		return false;
	});

	var $form = $('#report_form');
	var $map = $('#map-bxl');

	
	$(window).hashchange(function(){
		if(window.location.hash == '#form')
		{
			$('#page_content_container').removeClass('form-hide').addClass('form-show');
			$form.show();
			$('#nearby-reports,#instructable').hide();
			$('#back').css({visibility: 'visible'});
			$("#addFileDiv").show();
			$("#addCommmentDiv").show();
			retrieveAddress();
		}
		else
		{
			$('#page_content_container').removeClass('form-show').addClass('form-hide');
			$form.hide();
			$('#nearby-reports').show();
			$('#back').css({visibility: 'hidden'});
			$("#addFileDiv").hide();
			$("#addCommmentDiv").hide();
			$('#instructable').fadeIn();
			$map.one('markerdrag click movestart zoomend',function(evt,point){
				$('#instructable').fadeOut();
			});
		}
	});
	$(window).hashchange();
	
    //On page load: The report overview needs to be hidden
    $('#report_overview_table_div').hide();
    
    
    $map.bind('markermoved',function(evt,point){
    	$('#id_x').val(point.x);
    	$('#id_y').val(point.y);
    	
    	if(window.location.hash != '#form')
    	{
    		window.location.assign('#form');
    		$("#addFileDiv").show();
    		$("#addCommmentDiv").show();
			return; // address is retrieved when form is shown
		}
		
		retrieveAddress();
	});

    $map.bind('reportselected', function(evt, point, report){
    	window.location.assign('/reports/' + report.id);
    });

    
	//On page load: the add comment and add file forms must be hidden
	$("#extraCommentsDiv").hide();
	$("#extraFilesDiv").hide();
	
	
});

function retrieveAddress()
    {
    	var $form = $('#report_form');
    	var $map = $('#map-bxl');
    	$form.find('.error-msg').remove();
    	$form.find(':submit').prop('disabled',true);
    	$('#id_address').addClass('loading');

    	$map.fmsMap('getSelectedAddress',function(response)
    	{
    		$('#id_address').removeClass('loading');
    		
    		if(response.status == 'success')
    		{
    			$('#id_postalcode').val(response.result.address.street.postCode);
    			$('#id_address').val(response.result.address.street.name+ ', ' + response.result.address.number);
    			$('#id_address_number').val(response.result.address.number);
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

