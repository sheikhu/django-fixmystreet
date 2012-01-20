(function(){
    $(document).bind("mobileinit", function() {
        $.support.cors = true;
        $.mobile.allowCrossDomainPages = true;
        //$.mobile.page.prototype.options.addBackBtn = true;
        $.mobile.ajaxEnabled = false;
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

    window.alert = function(message){
        return Notification.prototype.alert.apply(this, [message, function(){}, 'Fix My Street Brussels', 'OK']);
    }

    if(!window.console) {
        window.console = {};
    }
    if(!console.log || !DEBUG) {
        console.log = $.noop;
    }

    $(document).bind("backbutton", function(){ history.back(); });
    $(document).delegate("[data-rel=back]", "click", function(){ history.back(); });



	$(document).bind('initapp', function() {
		FB.init({ 
				appId: "263584440367959", 
				nativeInterface: PG.FB,
				oauth: true
		});
		FB.getSession(function(response) {
            console.log(JSON.stringify(response))
            if (response.session) {
                loggedIn(response.session.access_token);
            }
		});
	});

	$(document).delegate('#login-fb', 'click', function() {
		FB.login(function(response) {
            if (response.session) {
                loggedIn(response.session.access_token);
            }
        }, { perms: "email" });
	});
	
 	function loggedIn(token){
		//alert('logged in');
        console.log('login success with token ' + token);
        $.get(
	        window.fms.rootUrl + '/api/report/create/', 
        	{'access_token':token,'backend':'facebook'},
            function(response){
            	console.log(response.user);
              $('#config .content').append(response.user);
            }
        ).error(function(response){
            console.log(response);
    	});
	}



/*
    $(document).delegate("form", "submit", function(evt){
        evt.preventDefault();
        evt.stopPropagation();

        var $form = $(this);
        var valid = true;
        
        $('.required input, .required select').each(function(ind,input){
            if(!$(input).val()){
                valid = false;
                $(input).addClass('mandatory');
            }else{
                $(input).removeClass('mandatory');
            }
        });
        
        if(!valid){
            $form.find('.mandatory').first().focus();
            
            return;
        }
        
        $.mobile.showPageLoadingMsg();
          
        var $current = $form.closest('[data-role=page]');
          
        var url = window.fms.rootUrl + $form.attr('action');

        var success = function(content){
            var $page = $(content).page();
            
            // TODO: do not change content, change panel instead
            $current.find('[data-role=content]').remove();
            var newContent = $page.find('[data-role=content]');
            newContent.addClass('ui-content');
            $current.append(newContent);
            $current.trigger( "create" );
            $(document.body).animate({scrollTop:0}, 'fast');
              
            $.mobile.hidePageLoadingMsg();

            $current.trigger( "pageinit" );
        }
              
        $file = $form.find('input[type=file]');
        if($file.length && $file.data('uri')) 
        {
            var imageURI = $file.data('uri');
            var options = new FileUploadOptions();
            options.fileKey = $file.attr('name');
            options.fileName = imageURI.substr(imageURI.lastIndexOf('/') + 1);
            options.mimeType = "image/jpeg";
            var params = {};
            var array = $form.serializeArray();
            for(i in array){
                params[array[i].name] = array[i].value;
            }
            options.params = params;
            
            var ft = new FileTransfer();
              
            ft.upload(imageURI, url, function(r){success(r.response);}, connectionErrorCallback, options);
        } else {
            $.post(url,$form.serialize(),success)
                    .error(connectionErrorCallback);
        }
    });
*/

    window.fms.getCurrentPosition = function(callback)
    {
        var locationErrorCallback = function(error)
        {
            console.log('localisation error: ' + error);
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
