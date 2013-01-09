$(document).ready(function() {
    var selectCategory = $("#id_report-secondary_category");
    //If not pro

    // var showPrivate = window.location.href.indexOf("/pro/") == -1;

    $('#id_report-category').change(function(evt) {
        // updates entry notes
        var el_id = $('#id_report-category').val();
        if(el_id)
        {
            $("#secondary_container").load("/ajax/categories/" + el_id);

            selectCategory.val("");
            selectCategory.prop('disabled', false);
            selectCategory.find("option:not(:first)").hide();
            selectCategory.find("optgroup").hide();
            for (id in categories[el_id]) {
                selectCategory.find("option[value="+id+"]").show().parent().show();
            }
            selectCategory.find("optgroup").has("option:visible").show();
            console.log(selectCategory.find("optgroup").has("option"));
        }
        else
        {
            selectCategory.val("");
            selectCategory.prop('disabled', true);
        }
    });
    $('#id_report-category').change(); // initialize notes

    $('#id_report-secondary_category').change(function(evt) {
            //Copy is necessary to avoid django validation problem
            var el_id_copy = $('#id_report-secondary_category').val();
            $('#id_report-secondary_category_copy').val(el_id_copy);
        });
    $('#id_report-secondary_category').change();// initialize notes
});
