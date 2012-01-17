
$(document).delegate('#home', "pageinit", function(){
    
    if(!navigator.camera || !navigator.camera.getPicture)
    {
        $('#menu-photo').addClass('ui-disabled');
    }
    window.fms.getCurrentPosition(function(p){
        loadAddress(p);
    });
});

$(document).delegate('#photo', "pageinit", function(evt){
    $.mobile.showPageLoadingMsg();
    panel = $(this);
    
    navigator.camera.getPicture(function(fileURI) {
        $('#menu-photo').addClass('filled').empty();
        $('#menu-photo').css({
            'background-image': 'url('+fileURI+')',
            'background-size': 'cover'
        });
        panel.find('form').append('<img src="'+fileURI+'"/>');
        
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
                $('#menu-address').addClass('filled').find('.value').html(address);
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

$(document).delegate('.toolbar .next', "click", function(){
    //save
    var itemId = $(this).closest('.panel').attr('id');
    var item = $('#home #menu-'+itemId);
    item.addClass('filled');
    var menu = $('#home .menu-button');
    var target = menu.filter(':gt('+menu.index(item)+'):not(.filled)').first();
    console.log(target);
    if(!target.length){
        $.mobile.changePage('#home');
        $('#home button').button('enable');	
    }else{
        $.mobile.changePage(target.attr('href'));
    }
});




$(document).delegate('#category', "pageinit", function(){
    //$(this).find('.confirm').hide();
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


