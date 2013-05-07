

(function() {

    var allowed_file_types = [
            "image/png","image/jpeg","application/pdf","application/msword","application/vnd.ms-excel",
            "application/vnd.oasis.opendocument.text",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.oasis.opendocument.spreadsheet"
        ],
        file_max_size = 10000000, // 10MB
        file_count = 0,
        file_form_template = null;


    $(function() {
        file_form_template = $("#file-form-template");
        /**********************************************************/
        /* Attach a onchange listener to the file input field.    */
        /* This listener will verify the validity of the filesize */
        /**********************************************************/
        $(document.body).delegate(":file", "change", fileSelected);
    });

/********************************************************************************************/
/* This function checks the size of the current selected file in the file form input field. */
/********************************************************************************************/
    function fileSelected(evt) {
        var inputFile = evt.currentTarget;
        var file;


        var form_copy = file_form_template.clone();
        var form_new = file_form_template;
        file_form_template = form_copy;

        form_new.attr('id', '');
        form_new.find(":input").each(function(index, input) {
            input.id = input.id.replace(/__prefix__/g, file_count);
            input.name = input.name.replace(/__prefix__/g, file_count);
        });
        form_new.find("label").each(function(index, label) {
            $(label).attr('for', $(label).attr('for').replace(/__prefix__/g, file_count));
        });

        $('#form-files').append(form_new);
        $('#form-files').append(file_form_template);
        form_new.find("[data-toggle=popover]").remove();
        file_form_template.find("[data-toggle=popover]")
                .popover({
                    html : true,
                    content: function() {
                        return $(this).next().html();
                    }
                }).click(function(e) {
                    e.preventDefault();
                });


        if (typeof inputFile.files != 'undefined' && inputFile.files.length) {
            file = inputFile.files[0];
            if(file.size == 0) {
                alert('Filesize must be greater than 0');
                $("#fileForm #id_file").val("");
                return;
            }
            //TODO determine max file size
            else if(file.size > file_max_size) {
                alert('File to large');
                $("#id_files-"+file_count+"-file").val("");
                return;
            }
            else if(allowed_file_types.indexOf(file.type)==-1 ){
                alert('The type of the file is not correct. You can only upload files of type: jpg, png, pdf, doc and xls.');
                $("#id_files-"+file_count+"-file").val("");
                return;
            }

            // if (file.name) {
            //     $("#id_files-"+file_count+"-title").val(file.name);
            // }

            if(file.lastModifiedDate) {
                // Append file creation date
                var fileDate = new Date(file.lastModifiedDate);
                day = fileDate.getDate();
                month = fileDate.getMonth()+1;
                year = fileDate.getFullYear();
                hour = fileDate.getHours();
                minute = fileDate.getMinutes();

                form_new.find("#id_files-"+file_count+"-file_creation_date").val(year+"-"+month+"-"+day+" "+hour+":"+minute);
            }

            AddFileToView(form_new, file);
        } else {
            AddFileToView(form_new, null);
        }
        file_count++;
        $("#id_files-TOTAL_FORMS").val(file_count);
    }

    /************************************************************************************/
    /* Add the submitted file to the view and save it in the session and on the server. */
    /************************************************************************************/
    function AddFileToView(elem, file){
        //Determine the type of the submited file
        var type = (file && file.type.split("/")[1]) || null;
        //Structured Data of the file to add
        var title = elem.find(":file").val();
        if (title == ""){
            title = file.name;
        }

        var thumbnails = "", img = elem.find(".thumbnail");
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
            thumbnails = "/static/images/icon-generic.png";
        }

        if (typeof window.FileReader != 'undefined' && (type == "jpeg" || type == "png")) {
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
})();