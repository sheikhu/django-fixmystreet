(function() {
    var file_types = {
        image: ["image/png","image/jpeg"],
        pdf: ["application/pdf"],
        document: ["application/vnd.oasis.opendocument.text","application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
        spreadsheet: ["application/vnd.ms-excel","application/vnd.oasis.opendocument.spreadsheet","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
    };
    var allowed_file_types = [];
    for (var k in file_types) { allowed_file_types = allowed_file_types.concat(file_types[k]); }
    var file_max_size = 10000000; // 10MB
    var file_max_size_total = 20000000; // 20MB
    var file_size_total = 0;
    var file_count = 0;
    var inputfile_count = 0;

    //this is a counter of total files added, including those that were removed. this counter is necessary to properly name elements when adding a new file.
    // Otherwise there were conflicts in names when adding, then removing, then adding files again.
    var total_file_count = 0;


    $(function() {
        /**********************************************************/
        /* Attach a onchange listener to the file input field.    */
        /* This listener will verify the validity of the filesize */
        /**********************************************************/
        $(document.body).delegate(":file", "change", fileSelected);
    });

    function isFileType(type, allowed) {
        return file_types[allowed].indexOf(type) > -1;
    }

/********************************************************************************************/
/* This function used to retrieve the exif data from an image asynchronously                */
/********************************************************************************************/


/********************************************************************************************/
/* This function checks the size of the current selected file in the file form input field. */
/********************************************************************************************/
    function fileSelected(evt) {
        var inputFile = evt.currentTarget;
        var filesContainer = $('<div />').appendTo('#file-form-files');

        if (typeof inputFile.files == 'undefined' || inputFile.files.length === 0) {
            return;
        }

        // WARNING: this code must run in IE and input.filers is not supported by IE9
        var exifCallback = function(file, exifObject) {
            var day;
            var month;
            var year;
            var hour;
            var minute;
            if (exifObject.DateTimeOriginal){
                var datetosplit = exifObject.DateTimeOriginal;
                var splitted = datetosplit.split(/[:,\/ ]/);
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

            var form_new = $($('#file-form-row-tpl').html().replace(/__prefix__/g, total_file_count));
            form_new.find("#id_files-"+total_file_count+"-file_creation_date").val(year+"-"+month+"-"+day+" "+hour+":"+minute);
            form_new.removeClass('required').removeClass('invalid');

            form_new.find("[data-toggle=popover]").remove();
            form_new.find("[data-toggle=popover]")
                .popover({
                    html : true,
                    content: function() { return $(this).next().html(); }
                }).click(function(e) { e.preventDefault(); });

            var removeThumbnail = form_new.find('.removeThumbnail')[0];
            removeThumbnail.addEventListener('click', function() {
                $(this).closest('.row-fluid').parent().remove();
                file_size_total -= file.size;

                file_count--;
                total_file_count--;
                $("#id_files-TOTAL_FORMS").val(file_count);
            });

            AddFileToView(form_new, file);
            filesContainer.append(form_new);

            file_count++;
            total_file_count++;
            $("#id_files-TOTAL_FORMS").val(file_count);
        };


        var fileFailed = false;
        for (var i = 0; i < inputFile.files.length; i++) {
            var file = inputFile.files[i];

            if (!file) {
                AddFileToView(form_new, null);
                continue;
            }

            // validation of the file
            if(allowed_file_types.indexOf(file.type)==-1 ){
                $('#file-type-error').modal();
                continue;
            }
            if(file.size === 0) {
                alert(gettext('Filesize must be greater than 0'));
                continue;
            }
            if(file.size > file_max_size) {
                $('#file-too-large-error').modal();
                fileFailed = true;
                continue;
            }

            // Add this file size to the total of current selected files
            file_size_total += file.size;
            if(file_size_total > file_max_size_total) {
                // Total is too much, decrease this file size from the current total
                file_size_total -= file.size;
                $('#file-total-too-large-error').modal();
                fileFailed = true;
                continue;
            }

            $.fileExif(file, exifCallback);
        }

        if (fileFailed) {
            return;
        }

        var oldInput = $(inputFile).remove();
        var newInput = oldInput.clone();
        oldInput.attr({id: null, name: 'files-files-'+inputfile_count}).removeClass();
        filesContainer.attr('id', 'files-group-'+inputfile_count).append(oldInput);
        $('#file-form-btn-add-container .input-file-button2').append(newInput);
        inputfile_count++;
    }

    /************************************************************************************/
    /* Add the submitted file to the view and save it in the session and on the server. */
    /************************************************************************************/
    function AddFileToView(elem, file){
        //Determine the type of the submited file
        var type = (file && file.type) || null;
        //Structured Data of the file to add
        //var title = elem.find(":file").val();
        //if (title === ""){
        //    title = file.name;
        //}

        var thumbnails = "";
        var imgContainer = elem.find(".thumb");
        var img = $('<img />');
        imgContainer.append(img);
        if (isFileType(type, 'pdf')){
            thumbnails = "/static/images/icon-pdf.png";
        } else if (isFileType(type, 'document')){
            thumbnails = "/static/images/icon-word.jpg";
        } else if (isFileType(type, 'spreadsheet')){
            thumbnails = "/static/images/icon-excel.png";
        } else {
            thumbnails = "/static/images/icon-generic.png";
        }

        if (typeof window.FileReader != 'undefined' && isFileType(type, 'image')) {
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

    // Override validateForm from common.js
    var oldValidateForm = validateForm;

    validateForm = function(form) {
        var isValid = false;
        var $this = $(this);

        // Validation of comment and photo
        var hasComment, hasPhoto = false;
        if ($('#id_comment-text').val()) {
            hasComment = true;
        }
        if (total_file_count) {
            hasPhoto = true;
        }

        if (hasComment || hasPhoto) {
            isValid = true;
        }

        $this.find('[data-one-click]').prop('disabled', isValid && $('#coordonnees').is(':visible'));

        var commentArea = $('#id_comment-text');
        var fileUploadBtn = $('#file-form-btn-add-container > label.input-file-button');

        if (!isValid) {
            fileUploadBtn.addClass('invalid');
            commentArea.addClass('invalid');
        } else {
            fileUploadBtn.removeClass('invalid');
            commentArea.removeClass('invalid');
        }

        isValid = oldValidateForm(form) && isValid;

        return isValid;

    }
})(validateForm);


