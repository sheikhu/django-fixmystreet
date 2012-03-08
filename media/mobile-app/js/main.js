(function() {
    $(document).bind("mobileinit", function() {
        //$.mobile.page.prototype.options.addBackBtn = true;
        $.mobile.pushStateEnable = false;
    });

    if(!window.fms) {
        window.fms = {};
    }

    window.fms.rootUrl = 'http://fixmystreet.irisnet.be';
    window.fms.rootUrl = 'http://dev.fixmystreet.irisnetlab.be';
    if(window.location.protocol == 'http:') {
        window.fms.rootUrl = window.location.protocol + '//' + window.location.host;
    }

    window.fms.mediaUrl = window.fms.rootUrl + '/media/';
    window.fms.serviceGisUrl = 'http://service.gis.irisnetlab.be';

    if(window.Phonegap && window.Notification) {
        window.alert = function(message) {
            return Notification.prototype.alert.apply(this, [message, function(){}, 'Fix My Street Brussels', 'OK']);
        }
    }

    if(!window.console) {
        window.console = {};
    }
    if(!console.log) {
        console.log = $.noop;
    }

    $(document).bind("backbutton", function(){ history.back(); });
    $(document).delegate("[data-rel=back]", "click", function(){ history.back(); });

    $(document).delegate(".ui-page", "pageinit", function(){
        if($(this).find('.ui-footer').length){
            $(this).find('.ui-content').addClass('ui-content-footered');
        }
    });

    window.fms.isOnline = function(dateTimeStr) {
        if(!window.Connection || !navigator.network || !navigator.network.connection) {
            return true;
        }
        return navigator.network.connection.type !== Connection.NONE;
    }

    window.fms.connectionErrorCallback = function(xhr, textStatus, errorThrown)
    {
        console.log('connection error: ' + textStatus + ' ' + errorThrown + ' ' + xhr.responseText);
        alert('Connection failed.');
        $.mobile.hidePageLoadingMsg();
    }

    window.fms.getCurrentPosition = function(callback)
    {
        function locationErrorCallback(error)
        {
            console.log('localisation error: ' + JSON.stringify(error));
            alert('Your device do not support geo localisation or the localisation has failed.');
            var defaultLoc = {x:148853.101438753, y:170695.57753253728};
            callback(defaultLoc);
            $.mobile.hidePageLoadingMsg();
        }

        $.mobile.showPageLoadingMsg();
        console.log('atempt to locate');
        if(navigator.geolocation && navigator.geolocation.getCurrentPosition)
        {
            navigator.geolocation.getCurrentPosition(function(position){
                $.mobile.hidePageLoadingMsg();
                var source = new Proj4js.Proj("EPSG:4326");
                var dest   = new Proj4js.Proj("EPSG:31370");
                var p      = new Proj4js.Point(position.coords.longitude, position.coords.latitude);
                  
                Proj4js.transform(source, dest, p);
                callback(p);
                $.mobile.hidePageLoadingMsg();
            },locationErrorCallback);
        }
        else
        {
            locationErrorCallback();
        }
    }
}());



/* proj4js config */
Proj4js.defs["EPSG:31370"]="+proj=lcc +lat_1=51.16666723333334 +lat_2=49.83333389999999 +lat_0=90 +lon_0=4.367486666666666 +x_0=150000.013 +y_0=5400088.438 +ellps=intl +towgs84=-99.1,53.3,-112.5,0.419,-0.83,1.885,-1.0 +units=m +no_defs";
