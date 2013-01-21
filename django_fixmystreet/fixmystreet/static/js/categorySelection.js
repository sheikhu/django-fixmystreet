$(document).ready(function() {
    var selectCategory = $("#id_report-secondary_category");
    var selectCopy = selectCategory.clone();
    //If not pro
     // var showPrivate = window.location.href.indexOf("/pro/") != -1;

    $('#id_report-category').change(function(evt) {
        // updates entry notes
        var el_id = $('#id_report-category').val();
        if(el_id)
        {
            $("#secondary_container").load("/ajax/categories/" + el_id);
            selectCategory.prop('disabled', false);
            selectCategory.html(selectCopy.html());
            selectCategory.find("option:not(:first)").hide();
            selectCategory.find("optgroup").hide();
            for (id in categories[el_id]) {
                selectCategory.find("option[value="+id+"]").show().parent().show();
            }
            selectCategory.find("optgroup").has("option:visible").show();
            $.each($("#id_report-secondary_category option").filter(function() { return $(this).css("display") == "none" }),function(idx,value){
                $(value).remove();
            });
            $.each(selectCategory.find("optgroup"),function(idx,value){
                if($(value).children().length ==0){
                    $(value).remove();
                }
            });
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