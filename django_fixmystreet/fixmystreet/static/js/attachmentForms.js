
$(document).ready(function() {

    /************************************/
    /* Hide the annex forms per default */
    /************************************/
    $("#commentForm").hide();
    $("#fileForm").hide();

    /**********************************************************/
    /* Attach a onchange listener to the file input field.    */
    /* This listener will verify the validity of the filesize */
    /**********************************************************/
    $("#fileForm #id_file").attr("onchange","fileSelected();");
});

/**************************************************************/
/* toogleFileForm is used to show/hide the file annex section */
/**************************************************************/
	function toggleFileForm() {
        $("#fileForm #id_title").val("");
        $("#fileForm #id_file").val("");
        $("#fileForm").toggle();
        $("#showFileFormButton").toggle();
        $("#addCommmentDiv").toggle();
	}

/********************************************************************/
/* toogleCommentForm is used to show/hide the comment annex section */
/********************************************************************/
	function toggleCommentForm() {
        $("#commentTextTextArea").val("");
        $("#commentForm").toggle();
        $("#showCommentFormButton").toggle();
        $('#addFileDiv').toggle();
	}

/********************************************************************************************/
/* This function checks the size of the current selected file in the file form input field. */
/********************************************************************************************/
    function fileSelected() {
        var file = document.getElementById('id_file').files[0];
        var allowed_file_types = ["image/png","image/jpeg","application/pdf","application/msword","application/vnd.ms-excel","application/vnd.oasis.opendocument.text","application/vnd.openxmlformats-officedocument.wordprocessingml.document","application/vnd.oasis.opendocument.spreadsheet"];
        if (file) {
            if(file.size == 0){
                alert('Filesize must be greater than 0');
                $("#fileForm #id_file").val("");
            }
            //TODO determine max file size
            if(file.size > 100000){
                alert('File to large');
                $("#fileForm #id_file").val("");
            }
            if(allowed_file_types.indexOf(file.type)==-1 ){
                alert('The type of the file is not correct. You can only upload files of type: jpg, png, pdf, doc and xls.');
                $("#fileForm #id_file").val("");
            }
        }
    }

/************************************************************************************/
/* Add the submitted file to the view and save it in the session and on the server. */
/************************************************************************************/
function AddFileToView(langcode){
    //Submit the last form to save the file to the server
    // $("#fileForm").submit();
    // If no files are yet added: show the div containing the added files table list
    if(!$("#extraFilesDiv").is(":visible")){
        $("#extraFilesDiv").show();
    }
    //Get the file from the file input component
    var file = document.getElementById('id_file').files[0];
    //Determine the type of the submited file
    var type = $("#fileForm #id_file")[0].files[0].type.split("/")[1];
    //Structured Data of the file to add
    var title = $("#fileForm #id_title").val();
    if (title == ""){
        title = file.name;
    }
    var file_creation_date = new Date(""+file.lastModifiedDate);
    var dateString = file_creation_date.getFullYear() + "-"+ (file_creation_date.getMonth()+1) + "-" + file_creation_date.getDate()+ " " + file_creation_date.getHours()+":"+file_creation_date.getMinutes();
    var data = {"title":title,"file":$("#fileForm #id_file").val().replace('C:\\fakepath\\','files/'),"file_creation_date":""+dateString};
    //Put the file data in the session
    $.post("/"+langcode+"/ajax/create-file",data);
    //Create a file reader so that we can create a thumbnail of the submitted file.
    var reader = new FileReader();
    //Define the onload function of the reader
    reader.onload = function(ev){
        var url = ev.target.result;
        //Show a thumbnail of the file depending on the file type
        if (type == "pdf"){
            $('#fileImage'+($('#extraFilesTable').find('tr').length-1)).attr("src","/static/images/icon-pdf.png");
        }
        else if (type == "png"){
            $('#fileImage'+($('#extraFilesTable').find('tr').length-1)).attr("src",url);
        }
        else if (type == "jpeg"){
            $('#fileImage'+($('#extraFilesTable').find('tr').length-1)).attr("src",url);
        }
        else if (type == "msword"){
            $('#fileImage'+($('#extraFilesTable').find('tr').length-1)).attr("src","/static/images/icon-word.jpg");
        }
        else if(type == "vnd.ms-excel"){
            $('#fileImage'+($('#extraFilesTable').find('tr').length-1)).attr("src","/static/images/icon-xls.png");
        }
        else if (type == "vnd.openxmlformats-officedocument.wordprocessingml.document"){
            $('#fileImage'+($('#extraFilesTable').find('tr').length-1)).attr("src","/static/images/icon-word.jpg");
        }
        else {
            $('#fileImage'+($('#extraFilesTable').find('tr').length-1)).attr("src","/static/images/icon-file.png");
        }
        $("#fileForm").submit();
    
    }

    //Create the html to add in the view
    var htmlToAdd = "<tr><td class='annexesFirstTD'><div class='report_update'><h3>"+title+"</h3><img src='' id='fileImage"+$('#extraFilesTable').find('tr').length+"' style='max-width: 50px;'/></div></td></tr>";
    $("#extraFilesTable").append(htmlToAdd);
    // Read the file that is submited. If the file is read the onload function will be called.
    reader.readAsDataURL(file);
    
}

/*********************************************************/
/* Add a comment to the extra comment table in the view. */
/*********************************************************/
function AddCommentToView(langcode){
    // If no comments are added yet: show the div containing the extra comments div
    if(!$("#extraCommentsDiv").is(":visible")){
        $("#extraCommentsDiv").show();
    }
    // Structured Data of the comment to add
    var data = {"text":$("#commentTextTextArea").val()};
    //Create the html to add in the view
    var html = "<tr><td class='annexesFirstTD'><div class='report_update'><h3>"+"</h3><p>"+$("#commentTextTextArea").val()+"</p></div></td></tr>"
    
    //Put comment data in the session
    $.post("/"+langcode+"/ajax/create-comment",data);
    $(".extraCommentsTable").append(html);
    
    
}