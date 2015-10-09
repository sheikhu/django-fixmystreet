

function setThirdPartyResponsibility(boolVal) {
    if(boolVal){ //asking to switch the incident cause to a third party
        var r2=confirm(gettext(TRAD_THIRD_PARTY_TRUE));
    }
    else{ //source of incident is not a third party
        var r2=confirm(gettext(TRAD_THIRD_PARTY_FALSE));
    }
    if (r2==true){
        window.location = THIRD_PARTY_RESPONSIBILITY_URL + '?thirdPartyResponsibility=' + boolVal;
    }
}

function setPrivateProperty(boolVal) {
    if(boolVal){ //asking to switch the incident cause to a third party
        var r2=confirm(gettext(TRAD_PRIVATE_PROPERTY_TRUE));
    }
    else{ //source of incident is not a third party
        var r2=confirm(gettext(TRAD_PRIVATE_PROPERTY_FALSE));
    }
    if (r2==true){
        window.location = PRIVATE_PROPERTY_URL + '?privateProperty=' + boolVal;
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