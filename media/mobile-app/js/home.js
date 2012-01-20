
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
                $.mobile.changePage('#resume');
                return;
            }
            current.load();
        } else {
            current = null;
            $.mobile.changePage('#resume');
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
    $(document).delegate('.toolbar .next', "click", function(){nextStep()});
    $(document).delegate('#resume .menuitem', "click", function(){
        nextStep($(this).data('step'));
    });


    $(document).delegate('#photo', "pageinit", function(evt){
        $.mobile.showPageLoadingMsg();
        panel = $(this);
        
        navigator.camera.getPicture(function(fileURI) {
            reportData['photo'] = fileURI;
            var img = $('<img src="'+fileURI+'"/>').height('140px');
            $('#menu-photo').append(img);
            /*.css({
                'background-image': 'url('+fileURI+')',
                'background-size': 'cover'
            });*/
            panel.find('form').append('<img src="'+fileURI+'"/>');
            
            $.mobile.hidePageLoadingMsg();
        },
        function(message) {
            alert('Failed to take photo... ' + message);
        }, { 
            destinationType: Camera.DestinationType.FILE_URI,
            sourceType: (Camera.PictureSourceType.CAMERA),
            targetWidth: 300,
            targetHeight: 300
        });
    });

    $(document).delegate('#address', "pageinit", function(evt){
        window.fms.getCurrentPosition(function(p){
            var address = $('.address-validate').text();
            if(!address) {
                loadAddress(p,function(address){
                    $('.address-validate').text(address);
                });
            }
        });
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

    $(document).delegate('#category li', "click", function(){
        //save
        $(this).addClass('ui-btn-active').siblings().removeClass('ui-btn-active');
        var category = $(this).text();
        reportData['category'] = category;
        $('#menu-category .value').text(category);
        nextStep();
    });

    $(document).delegate('#description', "pageshow", function(){
        $(this).find('#id_desc').focus();
    });

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
                    console.log('<p class="error-msg">' + response.status + '</p>');
                }
            }
        ).error(window.fms.connectionErrorCallback);
    }



}());
