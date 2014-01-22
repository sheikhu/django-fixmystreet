

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
/* This function used to retrieve the exif data from an image asynchronously                */
/********************************************************************************************/

    
/********************************************************************************************/
/* This function checks the size of the current selected file in the file form input field. */
/********************************************************************************************/
    function fileSelected(evt) {
        var inputFile = evt.currentTarget;
        var file;

        if (typeof inputFile.files != 'undefined' && inputFile.files.length) {
            file = inputFile.files[0];
        }


        var form_copy = file_form_template.clone();

        if (file) {
            // validation of the file
            if(file.size === 0) {
                alert('Filesize must be greater than 0');
                return false;
            }
            else if(file.size > file_max_size) {
                $('#file-too-large-error').modal();
                return false;
            }
            else if(allowed_file_types.indexOf(file.type)==-1 ){
                $('#file-type-error').modal();
                return false;
            }
        }
        var form_copy = file_form_template.clone();
        var form_new = file_form_template;
        file_form_template = form_copy;
            // if (file.name) {
            //     $("#id_files-"+file_count+"-title").val(file.name);
            // }

        if (file) {
            var exifCallback = function(exifObject) {
                var day;
                var month;
                var year;
                var hour;
                var minute;
                if (exifObject.DateTimeOriginal){
                    var datetosplit = exifObject.DateTimeOriginal;
                    var splitted = datetosplit.split(/[:,\/ ]/)
                    var pictureDate = new Date(splitted[0], splitted[1] -1, splitted[2], splitted[3], splitted[4], splitted[5], 0);
                    day = pictureDate.getDate();
                    month = pictureDate.getMonth()+1;
                    if (month < 10)
                        month = '0' + month;
                    year = pictureDate.getFullYear();
                    hour = pictureDate.getHours();
                    minute = pictureDate.getMinutes();
                } else if (file.lastModifiedDate){
                    // Append file creation date
                    var fileDate = new Date(file.lastModifiedDate);
                    day = fileDate.getDate();
                    month = fileDate.getMonth()+1;
                    year = fileDate.getFullYear();
                    hour = fileDate.getHours();
                    minute = fileDate.getMinutes();
                }

                form_new.find(":input").each(function(index, input) {
                    input.id = input.id.replace(/__prefix__/g, file_count);
                    input.name = input.name.replace(/__prefix__/g, file_count);
                });
                form_new.find("#id_files-"+file_count+"-file_creation_date").val(year+"-"+month+"-"+day+" "+hour+":"+minute);
                $('#form-files').find("#id_files-"+file_count+"-file_creation_date").val(year+"-"+month+"-"+day+" "+hour+":"+minute);
                AddFileToView(form_new, file);
                form_new.attr('id', '');
                
                form_new.find("label").each(function(index, label) {
                    $(label).attr('for', $(label).attr('for').replace(/__prefix__/g, file_count));
                });

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

                var removeThumbnail = form_new.find('.removeThumbnail')[0];
                removeThumbnail.classList.remove('hidden');
                removeThumbnail.addEventListener('click', function() {
                    $(this.parentNode).remove();
                });

                $('#form-files').append(form_new);
                $('#form-files').append(file_form_template);

                file_count++;       
                $("#id_files-TOTAL_FORMS").val(file_count);

                };

                
                $(inputFile).fileExif(exifCallback);

            /*if(file.lastModifiedDate) {
                // Append file creation date
                var fileDate = new Date(file.lastModifiedDate);
                day = fileDate.getDate();
                month = fileDate.getMonth()+1;
                year = fileDate.getFullYear();
                hour = fileDate.getHours();
                minute = fileDate.getMinutes();

                form_new.find("#id_files-"+file_count+"-file_creation_date").val(year+"-"+month+"-"+day+" "+hour+":"+minute);
            }*/ 

            
        } else {
            AddFileToView(form_new, null);
        }
        
    }

    /************************************************************************************/
    /* Add the submitted file to the view and save it in the session and on the server. */
    /************************************************************************************/
    function imageRemoved() {

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
