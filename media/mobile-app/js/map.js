(function(){
    var $map, initialized, newPoint;

    
    $(document).delegate('#map', "pageinit", function(){
        $page = $(this);
        $map = $page.find('#map-bxl');

        window.fms.getCurrentPosition(initMap)

        $map.bind('markermoved',function(evt,p){
            newPoint = p;
        });

        $map.bind('reportselected',function(evt, point, report){
            $.mobile.changePage(window.fms.rootUrl + '/mobile/reports/' + report.id);
        });
        
        $page.find('.confirm').click(function(evt){
            evt.preventDefault();
            evt.stopPropagation();

            if(newPoint){
                /* set location */
                loadAddress(newPoint);
            }
            history.back();
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
                url:window.fms.rootUrl + '/api/search/',
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


    function initMap(p){
        console.log('init map data');
        if(initialized){
            console.log('map already initialized, reset map content');
            $map.fmsMap('reset');
        }else{
            initialized = true;
            console.log('first map init');
            $map = $('#map-bxl');
            localRootFolder = window.location.href.substr(0,window.location.href.lastIndexOf('/') + 1);
            $map.fmsMap({
                apiRootUrl: window.fms.rootUrl + "/api/",
                origin:{x:p.x,y:p.y},
                showControl:false,
                markerStyle:{
                    externalGraphic: localRootFolder + "images/marker.png",
                    graphicXOffset:-44/2,
                    graphicYOffset:-77,
                    graphicHeight:77,
                    graphicWidth:44
                },
                fixedMarkerStyle:{
                    externalGraphic: localRootFolder + "images/marker-fixed.png"
                },
                pendingMarkerStyle:{
                    externalGraphic: localRootFolder + "images/marker-pending.png"
                }
            });
        }

        loadReports(p,function(){
            $map.fmsMap('addDraggableMarker', p.x, p.y);
            $('#create-report').removeClass('ui-disabled').data('position',p);
            $('#content-disabled').remove();
        });
        
        $('#instructable').fadeIn();
        $map.one('markerdrag click movestart zoomend',function(evt,point){
            $('#instructable').fadeOut();
        });
    }

    function loadReports(p,callback){
        $.getJSON(window.fms.rootUrl + '/api/reports/',{x:p.x,y:p.y},function(response){//, timestamp:(new Date()).toString() to disable cache
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
        }).error(window.fms.connectionErrorCallback);
    }
}());
