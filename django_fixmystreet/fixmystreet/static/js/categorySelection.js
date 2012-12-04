$(document).ready(function() {
    //Hide original list of elements
    $("#id_secondary_category_copy").hide();
    $("[for='id_secondary_category_copy']").hide();
	//If not pro
	if(window.location.href.indexOf("/pro/") == -1){
		/*Remove non-public categories*/
		$("#id_secondary_category").find("option[public='False']").hide();
	}


	$('#id_category').change(function(evt) {
                // updates entry notes
                var el_id = $('#id_category').val();
                var refSecondary = $("#id_secondary_category");
                if(el_id)
                {
                	refSecondary.find("option:eq(0)").attr("selected", "selected");
                	refSecondary.removeAttr("disabled");
                	$("#secondary_container").load("/ajax/categories/" + el_id);                	
                	refSecondary.html('');
                	refSecondary.html($('#id_secondary_category_copy').html());
                 //Keep the first element in memory (the headlabel)
                 var headLabelOption = refSecondary.find("option:first");
                 refSecondary.find("option[family!='"+el_id+"']").remove();                        
				 if(window.location.href.indexOf("/pro/") == -1){
                 	refSecondary.find("option[public='False']").remove();
                 }
				 //Prepend the headlabel again.						
                 refSecondary.prepend(headLabelOption);				 
                 /*remove empty optgroup*/
                 refSecondary.find("optgroup:not(:has(option))").remove();
                 /*Copy value to hiddendropdown */
			$('#id_secondary_category').change();// initialize notes
		}
		else
		{
			refSecondary.find("option:eq(0)").attr("selected", "selected");
			$("#secondary_container").html('');
			refSecondary.attr('disabled', 'disabled');
		}
	});
	$('#id_category').change();// initialize notes

	$('#id_secondary_category').change(function(evt) {
         	//Copy is necessary to avoid django validation problem
         	var el_id_copy = $('#id_secondary_category').val();
         	$('#id_secondary_category_copy').val(el_id_copy);
         });
	$('#id_secondary_category').change();// initialize notes
});
	