(function(){
    $(document).bind("mobileinit", function() {
        //$.mobile.page.prototype.options.addBackBtn = true;
        $.mobile.pushStateEnable = false;
    });

    if(!window.fms) {
        window.fms = {};
    }

    window.fms.rootUrl = 'http://fixmystreet.irisnet.be';
    window.fms.rootUrl = 'http://dev.fixmystreet.irisnetlab.be';
    if(window.location.protocol == 'http:'){
        window.fms.rootUrl = window.location.protocol + '//' + window.location.host;
    }

    window.fms.mediaUrl = window.fms.rootUrl + '/media/';
    
    var DEBUG = true;

    if(window.Notification) {
        window.alert = function(message) {
            return Notification.prototype.alert.apply(this, [message, function(){}, 'Fix My Street Brussels', 'OK']);
        }
    }

    if(!window.console) {
        window.console = {};
    }
    if(!console.log || !DEBUG) {
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
        return (!window.Connection && !navigator.network) || navigator.network.connection.type !== Connection.NONE;
    }


	$(document).bind('initapp', function() {
        if(window.PG) {
            FB.init({ 
                appId: "263584440367959",
                nativeInterface: PG.FB,
                oauth: true
            });
        } else {
            console.log('fail to init fb sdk with native interface');
            FB.init({ 
                appId: "263584440367959"
            });
        }
        var expires = window.localStorage.getItem('fms_fb_access_token_expires');
        if (expires && new Date(expires) > new Date()) {
            $(function(){
                $(document).trigger('connected');
            });
        }
	});

    window.fms.parseIsoDate = function(dateTimeStr) {
        var p = (/(\d{4})-(\d{2})-(\d{2})(?: |T)(\d{2}):(\d{2}):(\d{2}) \+(\d{4})/).exec(dateTimeStr);
		if(p && p.length > 6){
	        return new Date(p[1], p[2]-1, p[3], p[4], p[5], p[6]);
		} else {
	        return new Date(dateTimeStr);
		}
    }
 
	$(document).delegate('#login-fb', 'click', function() {
		FB.login(function(response) {
            if (response.session) {
                window.fms.login(response.session.access_token, window.fms.parseIsoDate(response.session.expires));
            }
        }, { perms: "email" });
	});
    $(document).delegate('#disconnect', 'click', function() {
        window.localStorage.removeItem('fms_fb_access_token');
        window.localStorage.removeItem('fms_fb_access_token_expires');
        FB.logout();

        $('#login-status').html('To create a report you have to login');
        $('#login-fb').closest('p').show();
        $('#disconnect').closest('p').hide();
        $('#back-report').closest('p').hide();
    });
    
    $(document).bind('connected',function(){
        FB.api('/me', function(response) {
            console.log(response);
            if(!response.error) {
                $('#login-status').html('You are connected as');
                $('#login-status').append('<p><strong>' + response.name + '</strong></p>');
                $('#login-status').append('<p><strong>' + response.email + '</strong></p>');
                $('#login-fb').closest('p').hide();
                $('#disconnect').closest('p').show();
                $('#back-report').closest('p').show();
            }
        });
    });
 
 	window.fms.login = function(token, expires) {
        console.log('login success with token ' + token + ' expire ' + expires);
        window.localStorage.setItem('fms_fb_access_token', token);
        window.localStorage.setItem('fms_fb_access_token_expires', expires);
        $(document).trigger('connected');
	}
    
 	window.fms.getToken = function(cb){
        console.log('try to get token');
        var token = window.localStorage.getItem('fms_fb_access_token');
        var expires = new Date(window.localStorage.getItem('fms_fb_access_token_expires'));
        console.log('token ' + token + ' expire on ' + expires);
        if (token && expires > new Date()) {
            console.log('token retrived');
            cb(token,'facebook');
         } else {
            if(!token) {
                console.log('token not found');
            } else {
                console.log('token expired');
            }
            cb();
            window.localStorage.removeItem('fms_fb_access_token');
            window.localStorage.removeItem('fms_fb_access_token_expires');
        }
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
