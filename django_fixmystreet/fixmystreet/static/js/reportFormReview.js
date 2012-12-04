 /****************************************************************************************/
 /* On submit: validate if the current commune participates with the FixMyStreet project */
 /****************************************************************************************/
 $(document).delegate("#report_form", "submit", function(evt) {

 		if ($('#available_zipcodes option[value="'+$('#id_postalcode').val()+'"]').length == 0) {
		//This commune does not participate to fixmystreet until now.
		alert("{% trans 'This_commune_does_not_participate' %}: "+$('#available_zipcodes_as_string').html());
		return false;
			}
		//When the user presses the submit button for the first time: the overview must be shown.
		// The following code will popuplate the report_overview_table with the entered values
        if (!$(':submit').hasClass('confirm')) {
            evt.preventDefault();
            $("#locationView").children().remove();
			$("#category1View").children().remove();
			$("#category2View").children().remove();
			$("#descriptionView").children().remove();
			$("#emailView").children().remove();
			$("#firstNameView").children().remove();
			$("#nameView").children().remove();
			$("#photoView").children().remove();
            //TODO show overview hide form
            vals = [];
            i = 0;
            $('[type=text]').each(function() {
  			 vals[i]=this.value;
  			 i++;
			});
			$('select').each(function(){
				vals[i] = $(this).find("option[value="+this.value+"]").text();
				i++;
			});
			$('textarea').each(function(){
				vals[i]=this.value;
				i++;
			});
			$('[type=file]').each(function() {
  			 vals[i]=this.value;
  			 i++;
			});
			console.log(vals);
			$("#locationView").append("<p>"+vals[0]+"</p>");
			$("#category1View").append("<p>"+vals[7]+"</p>");
			$("#category2View").append("<p>"+vals[8]+"</p>");
			$("#descriptionView").append("<p>"+vals[12]+"</p>");
			$("#emailView").append("<p>"+vals[1]+"</p>");
			$("#firstNameView").append("<p>"+vals[2]+"</p>");
			$("#nameView").append("<p>"+vals[3]+"</p>");
			// $("#photoView").append("<p>"+vals[9].split("\\")[2]+"</p>");
            $('#new_report_citizen_form').hide();
            $('#report_overview_table_div').show();
            $(':submit').val('Confirm');
            $(':submit').addClass('confirm');
            $(':submit').attr('onclick','submitAnnexes();');
            $("#addFileDiv").hide();
            $("#addCommmentDiv").hide();
        }
    });

/*********************************************************************************************************************************************/
/* Method called when the edit button is pressed (when the user is already in the overview screen). This function will show all forms again. */
/*********************************************************************************************************************************************/
function showForm(){
	$('#new_report_citizen_form').show();
    $('#report_overview_table_div').hide();
    $(':submit').val('Submit');
    $(':submit').removeClass('confirm');
    $(':submit').attr('onclick','');
    $("#addFileDiv").show();
    $("#addCommmentDiv").show();
}