
(function() {
    $(document).bind('initapp', function() {
        
        if(!navigator.camera || !navigator.camera.getPicture)
        {
            $('#menu-photo').addClass('ui-disabled');
        }
        /*
        window.fms.getCurrentPosition(function(p){
            loadAddress(p);
        });
        */
    });
    
    var reportData = {};
    
    var wizard = [
        {
            label: 'Category',
            load: function(){
                $.mobile.changePage('#category');
            },
            save: function($page){
            }
        },
        {
            label: 'Address',
            load: function(){
                $.mobile.changePage('#address');
            },
            save: function($page) {
                var address = $page.find('.address-validate').text();
                $('#menu-address .value').html(address);
            }
        },
        {
            label: 'Photo',
            load: function(){
                $.mobile.changePage('#photo');
            },
            save: function($page) {
                
            }
        },
        {
            label: 'Description',
            load: function(){
                $.mobile.changePage('#description');
            },
            save: function($page) {
                $('#menu-description .value').html($page.find('#id_desc').val());
            }
        }
    ]


    var index = 0;
    var current = null;
    function nextStep(step) {
        if(current) {
            current.save($.mobile.activePage);
            current.filled = true;
        }


        if(step != null) {
            index = step;
        }

        
        current = wizard[index];
        if(current) {
            if(current.filled && step == null) {
                current = null;
                $('#welcome').hide();
                $('#resume').show();
                $.mobile.changePage('#home');
                return;
            }
            current.load();
        } else {
            current = null;
            $('#welcome').hide();
            $('#resume').show();
            $.mobile.changePage('#home');
            return;
        }

        index++;
    }

    $(document).delegate("[data-rel=back]", "click", function(){
        index--;
        current.filled = false;
        current = wizard[index-1];
    });

    $(document).delegate('#start', "click", function(){nextStep()});
    $(document).delegate('#resume .menuitem', "click", function(){
        nextStep($(this).data('step'));
    });

    $(document).delegate('#photo #capture', "click", function(evt){
        getPhoto(Camera.PictureSourceType.CAMERA);
    });
    $(document).delegate('#photo #select', "click", function(evt){
        getPhoto(Camera.PictureSourceType.LIBRARY);
    });
    $(document).delegate('#photo #skip', "click", function(evt){
        reportData['photo'] = null;
        $('#photo #preview').empty();
        $('#menu-photo').find('img').remove();
        nextStep();
    });
    function getPhoto(source){
        $.mobile.showPageLoadingMsg();
        
        navigator.camera.getPicture(function(fileURI) {
            reportData['photo'] = fileURI;
            $('#photo #preview').html('<img src="'+fileURI+'"/>');
            $('#menu-photo').find('img').remove();
            $('#menu-photo').append('<img src="'+fileURI+'"/>');

            /*var img = $('<img src="'+fileURI+'"/>').height('140px');*/
            /*.css({
                'background-image': 'url('+fileURI+')',
                'background-size': 'cover'
            });*/
            
            $.mobile.hidePageLoadingMsg();
            nextStep();
        },
        function(message) {
            alert('Failed to take photo... ' + message);
        }, { 
            destinationType: Camera.DestinationType.FILE_URI,
            sourceType: source,
            targetWidth: 300,
            targetHeight: 300
        });
    }

    $(document).bind("locationchange", function(evt,p){
        var btn = $(this).find('.address-confirm, .address-invalidate').button('disable');
        var caption = $('.address-validate').html('').addClass('loader');

        loadAddress(p,function(address){
            reportData['address'] = address;
            caption.html(address).removeClass('loader');
            btn.button('enable');
        });
    });

    $(document).delegate('#address', "pageinit", function(evt){
        var address = reportData['address'];
        
        if(!address) {
            var btn = $(this).find('.address-confirm, .address-invalidate').button('disable');
            var caption = $('.address-validate').addClass('loader');

            window.fms.getCurrentPosition(function(p){
                loadAddress(p,function(address){
                    reportData['address'] = address;
                    caption.html(address).removeClass('loader');
                    btn.button('enable');
                });
            });
        }
    });

    $(document).delegate('#address .address-confirm', "click", function(evt){
        nextStep();
    });

    $(document).delegate('#address .address-invalidate', "click", function(evt){
        $.mobile.changePage('#map',{transition:'flip'});
    });
    $(document).delegate('#map .confirm', "click", function(evt){
        $.mobile.changePage('#address',{transition:'flip'});
    });

    $(document).delegate('#category li:not([data-role=list-divider])', "click", function(){
        $(this).addClass('ui-btn-active').siblings().removeClass('ui-btn-active');
        var category = $(this).text();
        reportData['category'] = $(this).data('value');
        $('#menu-category .value').text(category);
        nextStep();
    });

    $(document).delegate('#description', "pageshow", function(){
        $(this).find('#id_desc').focus();
    });

    function saveDescription(){
        var description = $('#id_desc').val();
        $('#menu-description .value').html(description);
        reportData['description'] = description;
        nextStep();
    }
    $(document).delegate('#description .buttons button', "click", saveDescription);
    //$(document).delegate('#description #id_desc', "blur", saveDescription);

    $(document).delegate('#resume .submit', "click", function(evt){
        evt.preventDefault();
        evt.stopPropagation();
        submitReport();
    });
    function submitReport() {
        console.log(reportData);

        $.mobile.showPageLoadingMsg();

        var url = window.fms.rootUrl + '/api/report/new/';

        var success = function(content){
            $.mobile.hidePageLoadingMsg();
            $('#welcome').find('.msg').show().html('Your report has been sent successfully');
            $('#resume').slideUp();
            $('#welcome').slideDown();
            //$.mobile.changePage('#home');
            setTimeout(function(){
                $('#welcome').find('.msg').slideUp();
            },3000);
        }
        
        window.fms.getToken(function(token,backend){
            if(token) {
                console.log('sending ' + JSON.stringify(reportData))
                reportData.token = token;
                reportData.backend = backend;
                if(reportData.photo) 
                {
                    var imageURI = reportData.photo;
                    var options = new FileUploadOptions();
                    options.fileKey = 'photo';
                    options.fileName = imageURI.substr(imageURI.lastIndexOf('/') + 1);
                    options.mimeType = "image/jpeg";
                    var params = reportData;
                    delete params.photo;
                    
                    var ft = new FileTransfer();
                    
                    ft.upload(imageURI, url, function(r){success(r.response);}, window.fms.connectionErrorCallback, options);
                } else {
                    $.post(url,reportData,success).error(window.fms.connectionErrorCallback);
                }
            } else {
                $.mobile.changePage('#config',{transition:'fade'});
            }
        });
    };

    function loadAddress(p,cb){
        $.post(
            window.fms.rootUrl + '/api/locate/',
            '{\
                "language": "en",\
                "point":{x:' + p.x + ',y:' + p.y + '}\
            }',
            function(response)
            {
                if(response.status == 'success')
                {
                    var address = response.result.address.street.name + ', ' + response.result.address.number;
                    cb(address);
                }
                else
                {
                    cb('<span class="error-msg">' + response.status + '</span>');
                }
            }
        ).error(window.fms.connectionErrorCallback);
    }



}());
