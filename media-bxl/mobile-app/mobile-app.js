

$(document).bind("ready", function(){
    var $map = $('#map-bxl');
    //var rootUrl = 'http://localhost:8000';
    var rootUrl = 'http://fixmystreet.irisnetlab.be';
    var mediaUrl = rootUrl + '/media/';


    if(navigator.geolocation && navigator.geolocation.getCurrentPosition)
    {
        navigator.geolocation.getCurrentPosition(function(position)
        {
            var source = new Proj4js.Proj("EPSG:4326");
            var dest   = new Proj4js.Proj("EPSG:31370");
            var p      = new Proj4js.Point(position.coords.longitude, position.coords.latitude);
            
            Proj4js.transform(source, dest, p);
            
            $('#create-report').attr('href',rootUrl + '/mobile/reports/new?lon='+p.x+'&lat='+p.y+'&address=arts');

            $map.fmsMap({
                apiRootUrl: rootUrl + "/api/",
                origin:{x:p.x,y:p.y},
                markerStyle:{
                    externalGraphic: mediaUrl + "images/marker.png",
                    graphicXOffset:-32/2,
                    graphicYOffset:-32,
                    graphicHeight:32,
                    graphicWidth:32
                },
                fixedMarkerStyle:{
                    externalGraphic: mediaUrl + "images/marker-fixed.png"
                },
                pendingMarkerStyle:{
                    externalGraphic: mediaUrl + "images/marker-pending.png"
                }
            });

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
                $map.fmsMap('addDraggableMarker', p.x, p.y);
            });
        },
        function(){
            alert('Your device do not support geo localisation..');
            $map.fmsMap({
                apiRootUrl: rootUrl + "/api/",
                markerStyle:{
                    externalGraphic: mediaUrl + "images/marker.png",
                    graphicXOffset:-32/2,
                    graphicYOffset:-32,
                    graphicHeight:32,
                    graphicWidth:32
                }
            });
        });
    }

    $map.bind('markermoved',function(evt,p){
        $('#create-report').attr('href',rootUrl + '/mobile/reports/new?lon='+p.x+'&lat='+p.y+'&address=arts');
    });

    // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    $map.bind('reportselected',function(evt, point, report){
        $.get(rootUrl + '/mobile/reports/' + report.id,function(response){
            var $panel = $(response);
            var id = $panel[0].id;
            $('#jqt').append($panel);
            console.log($panel);
            $panel.hide();
            jQT.goTo('#' + id);//, 'slide');
        });
    });

    $(document.body).delegate('#id_category', 'change', function(event){
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

    $(document).delegate(".new_report", "pageinit", function(){
        var $form = $(this).find('form');
        
        $('#id_category').change();// initialize notes
        
        $form.find('.error-msg').remove();
        $form.find(':submit').attr('disabled','disabled');
        $('#id_address').addClass('loading');

        $map.fmsMap('getSelectedAddress', function(response){					
            $form.removeClass('loading');
            $form.find(':submit').removeAttr('disabled');
            
            if(response.status == 'success')
            {
                $('#id_postalcode').val(response.result.address.street.postCode);
                $('#id_address').val(response.result.address.street.name + ', ' + response.result.address.number);
            }
            else
            {
                $form.removeClass('loading');
                $('#id_address').after('<p class="error-msg">' + response.status + '</p>');
            }
        });
        
        //$form.find('#id_photo').closest('p').hide();
        
        function setPhotoPath(fileURI)
        {
            alert(fileURI);
            $form.find('#id_photo').val(fileURI);
            $form.find('#photo_preview').attr('src',fileURI).fadeIn();
        }
        
        if(navigator.camera && navigator.camera.getPicture)
        {
            //alert('Open the camera...');
            navigator.camera.getPicture(setPhotoPath, function(message)
            {
                alert('Failed to take photo... ' + message);
            },{ 
                quality: 50/*, 
                destinationType: Camera.DestinationType.FILE_URI*/
            }); 
        }
        else
        {
            alert('navigator.camera.getPicture not available');
        }
    });


    var $searchTerm = $('#search');
    var $searchWard = $('#search-ward');
    var $searchForm = $('#search-form');
    var $proposal = $('#proposal');

    $('#show-search').click(function(evt){
        evt.preventDefault();
        $(this).hide();
        $searchForm.show();
    });

    $searchForm.submit(function(event)
    {
        event.preventDefault();
        
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
                        window.location.assign(resToHref(response.result[0]));
                    }
                    else
                    {
                        $searchTerm.removeClass('loading');
                        $proposal.empty();
                        for(var i in response.result)
                        {
                            var loc = response.result[i];
                            var street = loc.address.street;
                            $street = $('<li>' + street.name + ' (' + street.postCode + ')</li>')
                                .data('loc',loc)
                                .click(function()
                                {
                                    var loc = $(this).data('loc');
                                    $map.fmsMap('setCenter',loc.point.x, loc.point.y);
                                    
                                    $searchForm.hide();
                                    $('#show-search').show();
                                });
                            $proposal.append($street);
                        }
                        $proposal.slideDown();
                    }
                    // window.location.assign('/reports/new?lon=' + response.result.point.x + '&lat=' + response.result.point.y);
                }
                else
                {
                    $searchTerm.removeClass('loading');
                    if(response.status == "noresult" || response.status == "success")
                    {
                        $proposal.html('<p class="error-msg">No corresponding address has been found</p>').slideDown();
                    }
                    else
                    {
                        $proposal.html('<p class="error-msg">' + response.status + '</p>').slideDown();
                    }
                }
            },
            error:function(){
                $searchTerm.removeClass('loading');
        
                $proposal.html('<p class="error-msg">Unexpected error.</p>');
            }
        });
    });
    /*
    if(navigator.camera && navigator.camera.getPicture);
        navigator.camera.getPicture(function(){
        });
    }
    */
});

/* proj4js config */
Proj4js.defs["EPSG:31370"]="+proj=lcc +lat_1=51.16666723333334 +lat_2=49.83333389999999 +lat_0=90 +lon_0=4.367486666666666 +x_0=150000.013 +y_0=5400088.438 +ellps=intl +towgs84=-99.1,53.3,-112.5,0.419,-0.83,1.885,-1.0 +units=m +no_defs";
