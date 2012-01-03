(function(){
    $(document).delegate("#new_report", "pagereload", function(){
        var $form = $(this).find('form');
        
        window.fms.getCurrentPosition(function(p){
            $.post(
                window.fms.rootUrl + '/api/locate/',
                '{\
                    "language": "en",\
                    "point":{x:' + p.x + ',y:' + p.y + '}\
                }',
                function(response)
                {
                    $form.removeClass('loading');
                    $form.find(':submit').removeAttr('disabled');
                    $form.find(':submit').removeClass('ui-disabled');
                    
                    if(response.status == 'success')
                    {
                        $form.find('#id_postalcode').val(response.result.address.street.postCode);
                        $form.find('#id_address').val(response.result.address.street.name + ', ' + response.result.address.number);
                    }
                    else
                    {
                        $form.find('#id_address').after('<p class="error-msg">' + response.status + '</p>');
                    }
                }
            ).error(window.fms.connectionErrorCallback);
        });
    });

    $(document).delegate("#new_report", "pageinit", function() {
        var $form = $(this).find('form');
        
        if(window.localStorage){
            /* auto fill the form */
            var author = window.localStorage.getItem("author");
            var email = window.localStorage.getItem("email");
            var phone = window.localStorage.getItem("phone");
            $('#id_author').val(author);
            $('#id_email').val(email);
            $('#id_phone').val(phone);
            console.log('autofill',author,email,phone);
            $form.submit(function(){
                author = $('#id_author').val();
                email = $('#id_email').val();
                phone = $('#id_phone').val();
                window.localStorage.setItem("author",author);
                window.localStorage.setItem("email",email);
                window.localStorage.setItem("phone",phone);
                console.log('values saved',author,email,phone);
            });
        }
                
        $form.find('.error-msg').remove();
        $form.find(':submit').attr('disabled','disabled');
        $form.find(':submit').addClass('ui-disabled');
        $form.find('#id_address').addClass('loading');

        
        $('#locate').click(function(evt){
            $mapPanel = $('#map');
            $.mobile.changePage($mapPanel,{transition:'flip'});
            $mapPanel.trigger('pagereload');
        });
        
        function setPhotoPath(fileURI)
        {
            $form.find('#id_photo').data('uri',fileURI);
            $form.find('#id_photo').val(fileURI);
            $form.find('#photo_preview').attr('src',fileURI).fadeIn();
                         
            $('.select_photo').css({'margin-right':'110px'});
            $.mobile.hidePageLoadingMsg();
        }
        
        if(navigator.camera && navigator.camera.getPicture)
        {
            $('.select_photo').click(function(evt){
                evt.preventDefault();
                $.mobile.showPageLoadingMsg();
                
                navigator.camera.getPicture(setPhotoPath, function(message)
                {
                    alert('Failed to take photo... ' + message);
                },{ 
                    destinationType: Camera.DestinationType.FILE_URI,
                    sourceType: (this.id=="take_photo"?Camera.PictureSourceType.CAMERA:Camera.PictureSourceType.PHOTOLIBRARY),
                    targetWidth: 300,
                    targetHeight: 300
                });
            });
        }
        else
        {
            $('.select_photo').addClass('ui-disabled');
        }
    });
}());
