
$(document).delegate('#home', "pageinit", function(){
    
    if(navigator.camera && navigator.camera.getPicture)
    {
        $('#menu-photo').click(function(evt) {
            var $this = $(this);
            evt.preventDefault();
            $.mobile.showPageLoadingMsg();
            
            navigator.camera.getPicture(function(fileURI) {
                console.log(fileURI);
                $this.css({
                    'background-image': 'url('+fileURI+')',
                    'background-size': 'cover'
                });
                console.log($this);
                
                $.mobile.hidePageLoadingMsg();
            },
            function(message) {
                alert('Failed to take photo... ' + message);
            }, { 
                destinationType: Camera.DestinationType.FILE_URI,
                sourceType: (this.id=="take_photo"?Camera.PictureSourceType.CAMERA:Camera.PictureSourceType.PHOTOLIBRARY),
                targetWidth: 300,
                targetHeight: 300
            });
        });
    }
    else
    {
        $('#menu-photo').addClass('ui-disabled');
    }
    window.fms.getCurrentPosition(function(p){
        loadAddress(p);
    });
});

function loadAddress(p){
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
                console.log(response.result.address.street.postCode);
                console.log(address);
                $('#menu-address').html(address).buttonMarkup();
            }
            else
            {
                console.log('<p class="error-msg">' + response.status + '</p>');
            }
        }
    ).error(window.fms.connectionErrorCallback);
}



$(document).delegate('#description', "pageinit", function(){
    $(this).find('form').submit(function(evt){
        evt.preventDefault();
        //save
        history.back();
    });
});

$(document).delegate('#description', "pageshow", function(){
    $(this).find('#id_desc').focus();
});

$(document).delegate('#description .confirm', "click", function(){
    //save
    history.back();
});



$(document).delegate('#category', "pageinit", function(){
    $(this).find('.confirm').hide();
});

$(document).delegate('#category .confirm', "click", function(){
    var selected = $(this).closest('.panel').find(':radio:checked');
    $('#menu-category').html(selected.next().text()).buttonMarkup();
    //save
    history.back();
});

$(document).delegate('#category :radio', "change", function(){
    $(this).closest('.panel').find('.confirm').fadeIn();
    $(this).closest('form').find(':checked').next().addClass('ui-btn-active');
    $(this).closest('form').find(':radio:not(:checked)').next().addClass('ui-radio-off').removeClass('ui-radio-on ui-btn-active').find('.ui-icon').addClass('ui-icon-radio-off').removeClass('ui-icon-radio-on');
});


