(function() {

	$(document).bind('initapp', function() {
        if(window.PG) {
            FB.init({
                appId: "263584440367959",
                nativeInterface: PG.FB,
                cookie: true
            });
        } else {
            console.log('fail to init fb sdk with native interface');
            FB.init({ 
                appId: "263584440367959"
            });
        }
        var expires = window.localStorage.getItem('fms_fb_access_token_expires');
        if (expires && new Date(expires) > new Date()) {
            console.log('token not expired, try to init config');
            $(function() {
                $(document).trigger('connected');
            });
        }
	});

    /**
     * Sometimes FB give a date in the format 2012-01-01T00:00:00 +0100
     * Some browser does not parse this format nativelly, need to parse manualy in this case
     */
    window.fms.parseIsoDate = function(dateTimeStr) {
        var datetime = new Date(dateTimeStr);
        if(!isNaN(datetime.getTime())) {
            return datetime;
        }
        var p = (/(\d{4})-(\d{2})-(\d{2})(?: |T)(\d{2}):(\d{2}):(\d{2})(?: \+(\d{4})?)/).exec(dateTimeStr);
		if(p && p.length > 6){
            // new Date() return a date in correct timezone (UCT + 1h), no need to fix timezone
	        return new Date(p[1], p[2]-1, p[3], p[4], p[5], p[6]);
		} else {
	        return null;
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

        $('#config').removeClass('logged');
        //$('#login-status').html('To create a report you have to login');
        //$('#login-fb').closest('p').show();
        //$('#disconnect').closest('p').hide();
        //$('#back-report').closest('p').hide();
    });
    
    $(document).bind('connected', function() {
        $.mobile.showPageLoadingMsg();
        FB.api('/me', function(response) {
            console.log('get my info ' + JSON.stringify(response));
            if(!response.error) {
                $('#config').addClass('logged');
                $('#login-name').html(response.name);
                $('#login-email').html(response.email);
                //$('#login-fb').closest('p').hide();
                //$('#disconnect').closest('p').show();
                //$('#back-report').closest('p').show();
            }
            $.mobile.hidePageLoadingMsg();
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
}());
