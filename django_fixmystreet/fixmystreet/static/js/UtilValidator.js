//Create new object.
UtilValidator = new Object();
//Logging purposes
UtilValidator.TAG = "UtilValidator.JS: ";

UtilValidator.REGEXP_EMAIL = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
UtilValidator.REGEXP_PHONE = /^[0-9]+$/;

/**
 * validateEmail validates the given potential email using regexp
 */
UtilValidator.validateEmail = function(emailValue) {			
    if( !UtilValidator.REGEXP_EMAIL.test( emailValue ) ) {
        return false;
    } else {
        return true;
    }
}

/**
 * validatePhone validates the given phonenumber (Only numbers are accepted)
 */
UtilValidator.validatePhone = function(phoeValue) {			
    if( !UtilValidator.REGEXP_PHONE.test( phoeValue ) ) {
        return false;
    } else {
        return true;
    }
}