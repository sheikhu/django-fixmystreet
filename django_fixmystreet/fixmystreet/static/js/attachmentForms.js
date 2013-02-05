

var allowed_file_types = ["image/png","image/jpeg","application/pdf","application/msword","application/vnd.ms-excel","application/vnd.oasis.opendocument.text","application/vnd.openxmlformats-officedocument.wordprocessingml.document","application/vnd.oasis.opendocument.spreadsheet"];
var file_max_size = 15000000; // 15MB

var file_form_template = $("#file-form-template");
var file_count = 0;

$(document).ready(function() {
    /**********************************************************/
    /* Attach a onchange listener to the file input field.    */
    /* This listener will verify the validity of the filesize */
    /**********************************************************/
    $(document.body).delegate(":file", "change", fileSelected);
    $("#file-upload").click(function (evt) {
        evt.preventDefault();
        file_form_template.find(":file").click();
    });
});

/********************************************************************************************/
/* This function checks the size of the current selected file in the file form input field. */
/********************************************************************************************/
    function fileSelected(evt) {
        var inputFile = evt.currentTarget;

        var file;
        //Internet Explorer 8 and older
        if (typeof inputFile.files == 'undefined') {
            var form_copy = file_form_template.clone();
            form_copy.attr('id', '');
            form_copy.find(":input").each(function(index, input) {
                input.id = input.id.replace(/__prefix__/g, file_count);
                input.name = input.name.replace(/__prefix__/g, file_count);
            })
            form_copy.find("label").each(function(index, label) {
                $(label).attr('for', $(label).attr('for').replace(/__prefix__/g, file_count));
            })
            $('#form-files').append(form_copy);
            form_copy.find("img").attr('src',"/static/images/icon-generic.png");
            form_copy.find("img").file = evt.target.value;

        //file = inputFile[0];
                file_count++;
                $("#id_files-TOTAL_FORMS").val(file_count);
        } else {
            file = inputFile.files[0];
        }

        if (file) {
            if(file.size == 0) {
                alert('Filesize must be greater than 0');
                $("#fileForm #id_file").val("");
                return;
            }
            //TODO determine max file size
            else if(file.size > file_max_size) {
                alert('File to large');
                $("#fileForm #id_file").val("");
                return;
            }
            else if(allowed_file_types.indexOf(file.type)==-1 ){
                alert('The type of the file is not correct. You can only upload files of type: jpg, png, pdf, doc and xls.');
                $("#fileForm #id_file").val("");
                return;
            }
            else {
                var title = $("#fileForm #id_title").val();
                if (title == "") {
                    $("#fileForm #id_title").val(file.name);
                }
            }

            var form_copy = file_form_template.clone();
            file_form_template.attr('id', '');
            file_form_template.find(":input").each(function(index, input) {
                input.id = input.id.replace(/__prefix__/g, file_count);
                input.name = input.name.replace(/__prefix__/g, file_count);
            })
            file_form_template.find("label").each(function(index, label) {
                $(label).attr('for', $(label).attr('for').replace(/__prefix__/g, file_count));
            })
            $('#form-files').append(file_form_template);
            $('#form-files').append(form_copy);

            //Append file creation date
            var fileDate = new Date(file.lastModifiedDate);
            day = fileDate.getDate();
            month = fileDate.getMonth()+1;
            year = fileDate.getFullYear();
            hour = fileDate.getHours();
            minute = fileDate.getMinutes();

        file_form_template.find("#id_files-"+file_count+"-file_creation_date").val(year+"-"+month+"-"+day+" "+hour+":"+minute);
            AddFileToView(file_form_template, file);

            //$(inputFile).val('');
            // inputFile.replaceWith(inputFile.val('').clone( true )); for IE8 complient
            file_form_template = form_copy;
            file_count++;
            $("#id_files-TOTAL_FORMS").val(file_count);
        }
    }

/************************************************************************************/
/* Add the submitted file to the view and save it in the session and on the server. */
/************************************************************************************/
function AddFileToView(elem, file){
    //Determine the type of the submited file
    var type = file.type.split("/")[1];
    //Structured Data of the file to add
    var title = elem.find(":file").val();
    if (title == ""){
        title = file.name;
    }

    var thumbnails = "", img = elem.find("img");
    if (type == "pdf"){
        thumbnails = "/static/images/icon-pdf.png";
    }
    else if (type == "msword"){
        thumbnails = "/static/images/icon-word.jpg";
    }
    else if(type == "vnd.ms-excel"){
        thumbnails = "/static/images/icon-excel.png";
    }
    else if (type == "vnd.openxmlformats-officedocument.wordprocessingml.document"){
        thumbnails = "/static/images/icon-word.jpg";
    } else {
        thumbnails = "/static/images/icon-file.png";
    }

    if (FileReader && (type == "jpeg" || type == "png")) {
        img[0].file = file;

        var reader = new FileReader();
        reader.onload = function(e) {
            img.attr("src", e.target.result);
        };
        reader.readAsDataURL(file);
    } else {
        img.attr("src", thumbnails);
    }
}
