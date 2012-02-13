
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
    var location = null, postalcode = null;
    
    var wizard = [
        {
            label: 'Photo',
            id: 'photo',
            icon:'photo.png'
        },
        {
            label: 'Category',
            id:'category',
            icon:'category.png'
        },
        {
            label: 'Address',
            id:'address',
            icon:'map.png'
        },
        {
            label: 'Description',
            id:'description',
            icon:'description.png'
        }
    ];
    var wizardHtml = $('<div id="wizard"></div>');
    for(i in wizard) {
        wizardHtml.append('<span id="step-' + wizard[i].id + '" data-role="button" data-inline="true"><img src="images/' + wizard[i].icon + '"/></span>');
    }

    var index = -1;
    var current = null;
    function nextStep(step, reverse) {
        wizardHtml.children().eq(index).removeClass('current');
        //if(current && current.filled) {
            //wizardHtml.children().eq(index).addClass('filled');
        //}
        if(current && current.valid) {
            wizardHtml.children().eq(index).addClass('valid');
        } else {
            wizardHtml.children().eq(index).removeClass('valid');
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
            // wizardHtml.children().eq(index).removeClass('filled');
            wizardHtml.children().eq(index).addClass('current');
            wizardHtml.children().eq(index).addClass('filled');
            $.mobile.changePage('#'+current.id, {reverse:reverse});
            // current.load();
        } else {
            current = null;
            $('#welcome').hide();
            $('#resume').show();
            $.mobile.changePage('#home');
        }
    }

    $(document).delegate(".page-step", "pagebeforeshow", function(){
        $(this).find('.ui-content').prepend(wizardHtml);
    });

    wizardHtml.delegate('.filled:not(.current)', "click", function(){
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

    $(document).delegate('#photo #skip', "click", function(evt){
        reportData['photo'] = null;
        $('#menu-photo').find('img.ui-li-icon').prop('src','images/photo.png');
        $('#menu-photo .value').html('Empty').addClass('error-msg');
        current.filled = true;
        current.valid = false;
        nextStep();
    });
    $(document).delegate('#photo #capture', "click", function(evt){
        getPhoto(Camera.PictureSourceType.CAMERA);
    });
    $(document).delegate('#photo #select', "click", function(evt){
        getPhoto(Camera.PictureSourceType.PHOTOLIBRARY);
    });
    function getPhoto(source){
        $.mobile.showPageLoadingMsg();
        
        navigator.camera.getPicture(function(fileURI) {
            reportData['photo'] = fileURI;
            $('#photo #preview').html('<img src="'+fileURI+'"/>');
            $('#menu-photo .value').html(source === Camera.PictureSourceType.CAMERA?'Photo from camera':'Photo from Library').removeClass('error-msg');
            $('#menu-photo img.ui-li-icon').prop('src',fileURI);
            
            $.mobile.hidePageLoadingMsg();
            current.filled = true;
            current.valid = true;
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

        
        loadAddress(p,function(address, postalcode){
            //reportData['address'] = address;
            //reportData['location'] = p;
            location = p;
            postalcode = postalcode;
            caption.html(address).removeClass('loader');
            btn.button('enable');
        });
    });

    function initAddressPage(evt){
        var address = reportData['address'];
        
        if(!address && window.fms.isOnline()) {
            var btn = $(this).find('.address-confirm, .address-invalidate').button('disable');
            var caption = $('.address-validate').addClass('loader').removeClass('error-msg');

            window.fms.getCurrentPosition(function(p){
                loadAddress(p, function(address, postalcode) {
                    reportData['address'] = address;
                    reportData['postalcode'] = postalcode;
                    reportData['x'] = p.x;
                    reportData['y'] = p.y;

                    caption.html(address).removeClass('loader');
                    btn.button('enable');
                });
            });
        } else {
            if(!window.fms.isOnline()) {
                $('.address-validate').html('Your are offline').addClass('error-msg');
                $(this).find('.address-confirm, .address-invalidate').button('disable');
            }
        }
    }
    $(document).delegate('#address', "pageshow", initAddressPage);
    $(document).bind("online", initAddressPage);

    $(document).delegate('#address .address-confirm', "click", function(evt){
        var address = $(this).closest('.ui-content').find('.address-validate').text();
        $('#menu-address .value').html(address);
        
        reportData['address'] = address;
        reportData['postalcode'] = postalcode;
        reportData['x'] = location.x;
        reportData['y'] = location.y;
        
        current.filled = true;
        current.valid = true;
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
        current.valid = true;
        nextStep();
    });

    $(document).delegate('#description', "pageshow", function(){
        $(this).find('#id_desc').focus();
    });

    

    $(document).delegate('#description .buttons button', "click", function saveDescription(){
        var description = $('#id_desc').val();
        $('#menu-description .value').html(description);
        if(!description.length) {
            $('#menu-description .value').html('<span class="error-msg">Empty</span>');
        }
        reportData['description'] = description;

        current.filled = true;
        current.valid = description.length;
        nextStep();
    });
    //$(document).delegate('#description #id_desc', "blur", saveDescription);

    $(document).delegate('#resume .submit', "click", function(evt){
        evt.preventDefault();
        evt.stopPropagation();
        submitReport();
    });
    
    $(document).delegate('.help', "click", function(){
        var $this = $(this),
            tips = $this.closest('.ui-page').find('.tips');

        if($this.data('fms-tips')) {
            $this.data('fms-tips',false);
            tips.slideUp();
        } else {
            $this.data('fms-tips',true);
            tips.slideDown();
        }
    });

    function submitReport() {
        console.log(reportData);

        $.mobile.showPageLoadingMsg();

        var url = window.fms.rootUrl + '/api/report/new/';

        var success = function(content){
            console.log('ajax success');
            $.mobile.hidePageLoadingMsg();
            $('#welcome').find('.msg').show().html('Your report has been saved successfully. See you soon for a new report !');
            $('#resume').slideUp();
            $('#welcome').slideDown();
            for(var i in wizard) {
                wizard[i].filled = false;
            }
            reportData = {};
            index = -1;

            // clear all data in process
            wizardHtml.children().removeClass('current');
            wizardHtml.children().removeClass('filled');
            wizardHtml.children().removeClass('valid');

            $('#category').find('li.ui-btn-active').removeClass('ui-btn-active');

            $('#address .address-validate').html('');

            $('#photo #preview img').remove();
            $('#menu-photo img.ui-li-icon').prop('src','images/photo.png');
            $('#menu-photo .value').html('').removeClass('error-msg');

            $('#id_desc').val('');
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
