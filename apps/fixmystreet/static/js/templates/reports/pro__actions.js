

function setThirdPartyResponsibility(boolVal) {
    //hiddenThirdPartyResponsibility is used in updates.py : change_flag_and_add_comment
    showAddCommentDialog("hiddenThirdPartyResponsibility", boolVal, TRAD_SWITCH_THIRD_PARTY_RESPONSIBILITY_PLACEHOLDER, TRAD_THIRD_PARTY_RESPONSIBILITY_MESSAGE);
}

function setPrivateProperty(boolVal) {
    //hiddenPrivateProperty is used in updates.py : change_flag_and_add_comment
    showAddCommentDialog("hiddenPrivateProperty", boolVal, TRAD_SWITCH_PRIVATE_PROPERTY_PLACEHOLDER, TRAD_PRIVATE_PROPERTY_MESSAGE);
}

function showAddCommentDialog(name, boolVal, placeholder, message){
    $("#dialogAddComment").find(".control-group").removeClass("required");
    $("#hiddenAddComment").attr("name", name );
    $("#hiddenAddComment").attr("value", boolVal);
    if(placeholder != undefined){
        $("#dialogAddComment").find("#id_text").attr("placeholder", placeholder);
    }
    if(boolVal){
        message=message.replace('{0}', ('<span class="pAddCommentYes">' + gettext('yes') + '</span>'));
    }
    else{
        message=message.replace('{0}', ('<span class="pAddCommentNo">' + gettext('no') + '</span>'));
    }
    $("#divAddCommentMessage p").html(message);
    $("#fieldsetAddComment").coolfieldset({collapsed:true, speed:"fast"});

    //set proper icon (up or down)
    checkIconAddComment();
    $("#fieldsetAddComment legend").on("click", function(){
        checkIconAddComment();
    });

    //show modal
    $("#divAddComment").modal();
}

function checkIconAddComment(){
    console.log("test");
    if($("#iconAddComment").attr("class") && $("#iconAddComment").attr("class").indexOf("icon-chevron-down") > -1){
        $("#iconAddComment").removeClass("icon-chevron-down");
        $("#iconAddComment").addClass("icon-chevron-up");
    }
    else{
        $("#iconAddComment").removeClass("icon-chevron-up");
        $("#iconAddComment").addClass("icon-chevron-down");
    }
}

function setPrivate() {
    var r2=confirm(TRAD_SET_PRIVATE);
    if (r2==true){
        window.location = SWITCH_VISIBILITY_URL + '?visibility=true';
    }
}

function setPublic() {
    window.location = SWITCH_VISIBILITY_URL + '?visibility=false';
}

function confirmTransfer(url, manId) {
    $('#modalTransfer form').attr('action', url);
    $('#modalTransfer form input[name="man_id"]').val(manId);
    $('#modalTransfer').modal()
}

function confirmAssign(argUrl) {
    var r=confirm(gettext('Are you sure you want to change the contractor/applicant?'));
    if (r==true){
        window.location = argUrl
    }
}

function cancelCategoryUpdate() {
    //Close modal Window
    $('#modalCategory').modal('hide');
}

function sortAndAppendSecCat(data) {
    // Sort sec_cat
    var sortedSecCat = data.sort(function(a,b) {
        var aSecCat = a["s_c_n_"+LANGUAGE_CODE] + a["n_"+LANGUAGE_CODE];
        var bSecCat = b["s_c_n_"+LANGUAGE_CODE] + b["n_"+LANGUAGE_CODE];

        return aSecCat == bSecCat ? 0 : aSecCat < bSecCat ? -1 : 1;
    });

    // Create select with optgroups
    var currentOptGroup = null;
    for(var i = 0; i<sortedSecCat.length;++i) {
        if (sortedSecCat[i]["s_c_n_"+LANGUAGE_CODE] != currentOptGroup) {
            // Close previous optgroup if not the first
            if (currentOptGroup) {
                $("#sec_cat_select").append('</optgroup>');
            }
            // Add new optgroup
            $("#sec_cat_select").append('<optgroup label="' + sortedSecCat[i]["s_c_n_"+LANGUAGE_CODE] + '">');

            currentOptGroup = sortedSecCat[i]["s_c_n_"+LANGUAGE_CODE];
        }

        // options
        var option = "<option value='"+sortedSecCat[i].id+"'>" + sortedSecCat[i]["n_"+LANGUAGE_CODE] + "</option>";
        $("#sec_cat_select").append(option);
    }
    // Close previous optgroup if exists
    if (currentOptGroup) {
        $("#sec_cat_select").append('</optgroup>');
    }

    $("#sec_cat_select").prepend("<option value='0'>" + TRAD_SELECT_CATEGORY + "</option>");

    $("#sec_cat_select").val(REPORT_SEC_CAT_ID);
}

function validateCategories() {
    var valid = true;
    var form =  $('#update_cat_form');
    form.find('#main_cat_select, #sec_cat_select').each(function(ind, field) {
        var value = true;
        var field = $(field);
        if(field.val() == 0){
            valid = false;
            field.addClass('invalid');
        }else {
            field.removeClass('invalid');
        }
    });

    if(!valid) {
        form.find('.invalid select').first().focus();
        form.find('.required-error-msg').fadeIn();
        form.addClass('required-invalid');
    }
    return valid;
}

function close(){
    var r=confirm(TRAD_CLOSE_REPORT);
    if (r==true){
        window.location = CLOSE_REPORT_URL;
    }
}

function cancelPriorityUpdate(){
    //Restore original values
    $("#id_probability").val(REPORT_GRAVITY);
    $("#id_gravity").val(REPORT_PROBABILITY);
    //Close modal Window
    $('#modalPriority').modal('hide');
}

function persistPriorityUpdate(){
    var a = parseInt($("#id_probability").val());
    var b = parseInt($("#id_gravity").val());

    window.location = UPDATE_PRIORITY_URL +"?gravity="+a+"&probability="+b
}

function planned(){
    var date_planned = document.getElementById('date_planned').value;

    if (date_planned) {
        var url = PLANNED_URL + "?date_planned=" + date_planned;
        window.location = url;
    }
}