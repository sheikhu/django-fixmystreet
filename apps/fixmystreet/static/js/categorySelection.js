$(document).ready(function() {
    var selectCategory = $("#id_report-secondary_category");
    var selectCopy = selectCategory.clone();

    var containerSubCategory = document.querySelector("#report-sub_category");
    var selectSubCategory = document.querySelector("#id_report-sub_category");
    //If not pro
     // var showPrivate = window.location.href.indexOf("/pro/") != -1;

    $('#id_report-category').change(function(evt) {
        // updates entry notes
        var el_id = $('#id_report-category').val();

        if(el_id) {
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

        containerSubCategory.hidden = true;
        selectSubCategory.innerHTML = "";
    });
    $('#id_report-category').change(); // initialize notes

    $('#id_report-secondary_category').change(function(evt) {
            //Copy is necessary to avoid django validation problem
            var el_id_copy = $('#id_report-secondary_category').val();
            $('#id_report-secondary_category_copy').val(el_id_copy);

            // Manage sub_categories
            var el_id = $('#id_report-category').val();

            var sub_categories = categories[el_id][el_id_copy].sub_categories;
            var sub_categories_html = "";

            for (var idx in sub_categories) {
                var sub_category = sub_categories[idx];

                sub_categories_html += '<li><label for="id_report-sub_category_' + sub_category.id + '">';
                sub_categories_html += '<input id="id_report-sub_category_' + sub_category.id + '" name="report-sub_category" value="' + sub_category.id + '" type="radio">' + sub_category.label;
                sub_categories_html += '</label></li>';
            }
            selectSubCategory.innerHTML = sub_categories_html;

            if (sub_categories_html) {
                containerSubCategory.hidden = false;
            } else {
                containerSubCategory.hidden = true;
            }
        });

    $('#id_report-secondary_category').change();// initialize notes
});
