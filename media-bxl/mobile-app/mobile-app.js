(function(){
    $(document).bind("mobileinit", function(){
        //$.mobile.allowCrossDomainPages = true;
        //$.mobile.page.prototype.options.addBackBtn = true;
        $.mobile.ajaxEnabled = false;
    });


    var rootUrl = 'http://fixmystreet.irisnet.be';
    var rootUrl = 'http://fixmystreet.irisnetlab.be';
    // var rootUrl = 'http://192.168.103.27:8000';
    // var rootUrl = 'http://localhost:8000';

    var mediaUrl = rootUrl + '/media/';


    function goBackPage(evt){
        evt.preventDefault();
        evt.stopImmediatePropagation();

        var $current = $.mobile.activePage;
        var $page = $current.prev().first();

		if($current.data('ajaxLoaded')){
	        $page.one('pageshow', function(evt,data){
	            data.prevPage.remove();
	        });
        }
        $.mobile.changePage($page,{reverse:true});
        $.mobile.activePage = $page;
    };
    
    $(document).bind("backbutton", goBackPage);
    
    $(document).delegate("[data-rel=back]", "click", goBackPage);

    function loadFmsPage(url){
        $.mobile.showPageLoadingMsg();
        
        $.get(url, function(content){
            var $page = $(content);
            $.mobile.activePage.after($page);
            $page.page();
            
            $.mobile.hidePageLoadingMsg();
            $.mobile.changePage($page);

            $page.data('url',url);
            $page.data('ajaxLoaded',true);
        }).error(connectionErrorCallback);
    }

    $(document).delegate("form", "submit", function(evt){
        evt.preventDefault();
        evt.stopPropagation();

        $.mobile.showPageLoadingMsg();

        var $form = $(this);
        var $current = $form.closest('[data-role=page]');

        var url = $form.attr('action') || $current.data('url');
        if(!$form.attr('action')){
            $form.attr('action', url);
        }
        
        $form.ajaxSubmit(function(content){
            var $page = $(content).page();

            $current.find('[data-role=content]').remove();
            var newContent = $page.find('[data-role=content]');
            newContent.addClass('ui-content');
            $current.append(newContent);
            $current.trigger( "create" );
            $(document.body).animate({scrollTop:0}, 'fast');
            
            
            $.mobile.hidePageLoadingMsg();

            $current.data('url',url);
            $current.trigger( "pageinit" );
        }).error(connectionErrorCallback);
    });
    
    function connectionErrorCallback(){
        alert('Connection problem, please check your internet connection and relanch this app.');
        navigator.app.exitApp();
    }

    $(document).delegate('#home', "pageinit", function(){
        $page = $(this);
        var $map = $page.find('#map-bxl');

        function initMap(p){
            $map.fmsMap({
                apiRootUrl: rootUrl + "/api/",
                origin:{x:p.x,y:p.y},
                showControl:false,
                markerStyle:{
                    externalGraphic: "images/marker.png",
                    graphicXOffset:-32/2,
                    graphicYOffset:-32,
                    graphicHeight:32,
                    graphicWidth:32
                },
                fixedMarkerStyle:{
                    externalGraphic: "images/marker-fixed.png"
                },
                pendingMarkerStyle:{
                    externalGraphic: "images/marker-pending.png"
                }
            });
            
            loadReports(p,function(){
                $map.fmsMap('addDraggableMarker', p.x, p.y);
                $('#create-report').removeClass('ui-disabled').data('position',p);
                $('#content-disabled').remove();
            });
            
            $map.one('markerdrag click movestart zoomend',function(evt,point){
                $('#instructable').fadeOut();
            });
        }
        
        function loadReports(p,callback){
            $.getJSON(rootUrl + '/api/reports/',{lon:p.x,lat:p.y},function(response){
                if(response.status != 'success')
                {
                    // do something
                    console.log('error');
                    return ;
                }

                for(var i in response.results)
                {
                    var report = response.results[i];
                    $map.fmsMap('addReport',report);
                }
                if(callback){
                    callback();
                }
            }).error(connectionErrorCallback);
        }

        function noGeoLoc(){
            var defaultLoc = {x:148853.101438753, y:170695.57753253728};
            alert('Your device do not support geo localisation..');
            initMap(defaultLoc);
        }


        if(navigator.geolocation && navigator.geolocation.getCurrentPosition)
        {
            navigator.geolocation.getCurrentPosition(function(position)
            {
                var source = new Proj4js.Proj("EPSG:4326");
                var dest   = new Proj4js.Proj("EPSG:31370");
                var p      = new Proj4js.Point(position.coords.longitude, position.coords.latitude);
                
                Proj4js.transform(source, dest, p);
                initMap(p);
            }, noGeoLoc);
        }
        else
        {
            noGeoLoc();
        }

        $map.bind('markermoved',function(evt,p){
            $('#create-report').attr('href',rootUrl + '/mobile/reports/new?lon=' + p.x + '&lat=' + p.y + '&address=arts');
            $('#create-report').data('position',p);
        });

        $map.bind('reportselected',function(evt, point, report){
            loadFmsPage(rootUrl + '/mobile/reports/' + report.id);
        });
        
        $page.find('#create-report').click(function(evt){
            evt.preventDefault();
            evt.stopPropagation();

            var p = $(this).data('position');
            if(!p){return;}
            loadFmsPage(rootUrl + '/mobile/reports/new?lon=' + p.x + '&lat=' + p.y);
        });

        $page.find('#zoom-in,#zoom-out').click(function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            if(this.id=="zoom-in"){
                $map.fmsMap('zoomIn');
            }else{
                $map.fmsMap('zoomOut');
            }
        });
        $page.find('#locate').click(function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            $map.fmsMap('center');
        });


        var $searchTerm = $page.find('#search');
        var $searchWard = $page.find('#search-ward');
        var $searchForm = $page.find('#search-form');
        var $proposal   = $page.find('#proposal');

        //$page.find('#show-search').click(function(evt){
            //evt.preventDefault();
            //$(this).hide();
            //$searchForm.show();
        //});


		$searchTerm.change(function(){
			if(!$searchTerm.val()){
				$proposal.slideUp();
			}
		});
		
        $searchForm.submit(function(event)
        {
            event.preventDefault();
            event.stopPropagation();
            
            $proposal.slideUp();
            $searchTerm.addClass('loading');
            
            $.ajax({
                url:rootUrl + '/api/search/',
                type:'POST',
                contentType:'text/json',
                dataType:'json',
                data:JSON.stringify({
                    "language": "fr",
                    "address": {
                        "street": {
                            "name": $searchTerm.val(),
                            "postcode": $searchWard.val() || ''
                        },
                        "number": ""
                    }
                }),
                success:function(response){
                    if(response.status == 'success' && response.result.length > 0)
                    {
                        if(response.result.length == 1)
                        {
                            var loc = response.result[i];
                            $map.fmsMap('setCenter',loc.point.x, loc.point.y);
                            
                            //$searchForm.hide();
                            //$('#show-search').show();
                            $proposal.slideUp();
                        }
                        else
                        {
                            $searchTerm.removeClass('loading');
                            $proposal.empty();
                            for(var i in response.result)
                            {
                                var loc = response.result[i];
                                var street = loc.address.street;
                                $street = $('<li><a href="#">' + street.name + ' (' + street.postCode + ')</a></li>')
                                    .data('loc',loc)
                                    .click(function()
                                    {
                                        var loc = $(this).data('loc');
                                        //console.log(loc);
                                        $map.fmsMap('setCenter',loc.point.x, loc.point.y);
                                        $('#create-report').addClass('ui-disabled').data('position',loc.point);
                                        
                                        loadReports(loc.point,function(){
                                            $('#create-report').removeClass('ui-disabled');
                                        });

                                        //$searchForm.hide();
                                        //$('#show-search').show();
                                        $proposal.slideUp();
                                    });
                                $proposal.append($street);
                            }
                            $proposal.slideDown().listview('refresh');
                        }
                    }
                    else
                    {
                        $searchTerm.removeClass('loading');
                        if(response.status == "noresult" || response.status == "success")
                        {
                            $proposal.html('<li class="error-msg">No corresponding address has been found</li>').slideDown().listview('refresh');
                        }
                        else
                        {
                            $proposal.html('<li class="error-msg">' + response.status + ' ' + response.msg + '</li>').slideDown().listview('refresh');
                        }
                    }
                },
                error:function(){
                    $searchTerm.removeClass('loading');
            
                    $proposal.html('<p class="error-msg">Unexpected error.</p>');
                }
            });
        });
    });

    $(document).delegate("#new_report", "pageinit", function(){
        var $form = $(this).find('form');
        
        $(this).find('#id_category').change(function(event){
            // updates entry notes
            var el_id = $('#id_category').val();
            if(el_id)
            {
                $("#secondary_container").load(rootUrl + "/ajax/categories/"+el_id);
            }
            else
            {
                $("#secondary_container").html('');
            }
        });

        $(this).find('#id_category').change();// initialize notes
        
        $form.find('.error-msg').remove();
        $form.find(':submit').attr('disabled','disabled');
        $form.find('#id_address').addClass('loading');

        $('#map-bxl').fmsMap('getSelectedAddress', function(response){					
            $form.removeClass('loading');
            $form.find(':submit').removeAttr('disabled');
            
            if(response.status == 'success')
            {
                $form.find('#id_postalcode').val(response.result.address.street.postCode);
                $form.find('#id_address').val(response.result.address.street.name + ', ' + response.result.address.number);
            }
            else
            {
                $form.removeClass('loading');
                $form.find('#id_address').after('<p class="error-msg">' + response.status + '</p>');
            }
        });
        
        function setPhotoPath(fileURI)
        {
            $form.find('#id_photo').val(fileURI);
            $form.find('#photo_preview').attr('src',fileURI).fadeIn();
            $('.select_photo').css({'margin-right':'105px'});
        }
        
        $form.find('#id_photo').change(function(){
            var file = this.files[0];
            if(file){
                var $img = $form.find('#photo_preview');
                console.log('change',file);
                $img[0].file = file;
                
                var reader = new FileReader();  
                reader.onload = function(e) {
                    $img.prop('src', e.target.result);
                    $img.fadeIn();
                    $('.select_photo').css({'margin-right':'105px'});
                };
                reader.readAsDataURL(file);
            }
        });
        
        if(navigator.camera && navigator.camera.getPicture)
        {
            $('.select_photo').click(function(evt){
                evt.preventDefault();
                
                navigator.camera.getPicture(setPhotoPath, function(message)
                {
                    alert('Failed to take photo... ' + message);
                },{ 
                    quality: 50, 
                    destinationType: Camera.DestinationType.FILE_URI,
                    sourceType: (this.id=="take_photo"?Camera.PictureSourceType.CAMERA:Camera.PictureSourceType.PHOTOLIBRARY)
                });
            });
        }
        else
        {
            $('.select_photo').addClass('ui-disabled');
            $('#id_photo').show();
        }
    });
}());

/* proj4js config */
Proj4js.defs["EPSG:31370"]="+proj=lcc +lat_1=51.16666723333334 +lat_2=49.83333389999999 +lat_0=90 +lon_0=4.367486666666666 +x_0=150000.013 +y_0=5400088.438 +ellps=intl +towgs84=-99.1,53.3,-112.5,0.419,-0.83,1.885,-1.0 +units=m +no_defs";
