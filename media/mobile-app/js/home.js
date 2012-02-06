
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
    var location = null;
    
    var wizard = [
        {
            label: 'Category',
            id:'category',
            load: function(){
                $.mobile.changePage('#category');
            }
            /*save: function($page){
            }*/
        },
        {
            label: 'Address',
            id:'address',
            load: function(){
                $.mobile.changePage('#address');
            }
            /*save: function($page) {
                var address = $page.find('.address-validate').text();
                $('#menu-address .value').html(address);
            }*/
        },
        {
            label: 'Photo',
            id: 'photo',
            load: function(){
                $.mobile.changePage('#photo');
            }
            /*save: function($page) {
                
            }*/
        },
        {
            label: 'Description',
            id:'description',
            load: function(){
                $.mobile.changePage('#description');
            }/*,
            save: function($page) {
                $('#menu-description .value').html($page.find('#id_desc').val());
            }*/
        }
    ];
    var wizardHtml = $('<div id="wizard"></div>');
    for(i in wizard) {
        wizardHtml.append('<span id="step-' + wizard[i].id + '" data-role="button" data-inline="true">' + wizard[i].label + '</span>');
    }

    var index = -1;
    var current = null;
    function nextStep(step, reverse) {
        wizardHtml.children().eq(index).removeClass('current');
        if(current && current.filled) {
            wizardHtml.children().eq(index).addClass('filled');
        } else if(current) {
            wizardHtml.children().eq(index).removeClass('filled');
        }
        

        if(step != null) {
            index = step;
        } else {
            index++;
        }
        
        current = wizard[index];
        if(step == null) {
            while(index in wizard && current.filled) {
                index++;
                current = wizard[index];
            }
        }
        if(current) {
            //wizardHtml.children().eq(index).removeClass('filled');
            wizardHtml.children().eq(index).addClass('current');
            $.mobile.changePage('#'+current.id, {reverse:reverse});
            // current.load();
        } else {
            current = null;
            $('#welcome').hide();
            $('#resume').show();
            $.mobile.changePage('#home');
            return;
        }
    }

    $(document).delegate(".page-step", "pagebeforeshow", function(){
        $(this).find('.ui-content').prepend(wizardHtml);
    });

    wizardHtml.delegate('.filled', "click", function(){
        var target = $(this).parent().children().index(this);
        nextStep(target, target < index);
    });

    $(function(){
        $('.page-step').delegate("[data-rel=back]", "click", function(evt){
            evt.preventDefault();
            evt.stopImmediatePropagation();
            if(index == 0) {
                index--;
                current = null;
                wizardHtml.children().first().removeClass('current');
                $.mobile.changePage('#home', {reverse:true});
                return ;
            }
            nextStep(index - 1, true);
            return ;
            //index--;
            //current.filled = false;
            //current = wizard[index-1];
        });
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
        current.filled = false;
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
            current.filled = true;
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
            //reportData['address'] = address;
            //reportData['location'] = p;
            location = p;
            caption.html(address).removeClass('loader');
            btn.button('enable');
        });
    });

    $(document).delegate('#address', "pageshow", function(evt){
        var address = reportData['address'];
        
        if(!address) {
            var btn = $(this).find('.address-confirm, .address-invalidate').button('disable');
            var caption = $('.address-validate').addClass('loader');

            window.fms.getCurrentPosition(function(p){
                loadAddress(p,function(address){
                    reportData['address'] = address;
                    reportData['location'] = p;

                    caption.html(address).removeClass('loader');
                    btn.button('enable');
                });
            });
        }
    });

    $(document).delegate('#address .address-confirm', "click", function(evt){
        var address = $(this).closest('.ui-content').find('.address-validate').text();
        $('#menu-address .value').html(address);
        
        reportData['address'] = address;
        reportData['location'] = location;
        
        current.filled = true;
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
        
        current.filled = true;
        nextStep();
    });

    $(document).delegate('#description', "pageshow", function(){
        $(this).find('#id_desc').focus();
    });

    function saveDescription(){
        var description = $('#id_desc').val();
        $('#menu-description .value').html(description);
        reportData['description'] = description;

        current.filled = description.length;
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
            console.log('ajax success');
            $.mobile.hidePageLoadingMsg();
            $('#welcome').find('.msg').show().html('Your report has been sent successfully');
            $('#resume').slideUp();
            $('#welcome').slideDown();
            for(var i in wizard) {
                wizard[i].filled = false;
            }
            reportData = {};
            index = -1;
            wizardHtml.children().removeClass('current');
            wizardHtml.children().removeClass('filled');
            //$.mobile.changePage('#home');
            /*setTimeout(function(){
                $('#welcome').find('.msg').slideUp();
            },3000);*/
        }
        
        window.fms.getToken(function(token,backend){
            if(token) {
                reportData.token = token;
                reportData.backend = backend;
                console.log('sending ' + JSON.stringify(reportData));
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
                    $.post(url,reportData,success,'json').error(window.fms.connectionErrorCallback);
                }
            } else {
                $.mobile.changePage('#config',{transition:'fade'});
            }
        });
    };

    function loadAddress(p,cb){
        position = p;
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
