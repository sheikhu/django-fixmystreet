
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



$(this).find('form').submit(function(evt){
    evt.preventDefault();
    var panel = $(this).closest('.panel');
    panel.trigger('save');
});

$(document).delegate('.toolbar .next', "click", function(){
    var panel = $(this).closest('.panel');
    panel.trigger('save');
    
    var item = $('#home #menu-'+panel.attr('id'));
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





$(document).delegate('#description', "pageshow", function(){
    $(this).find('#id_desc').focus();
});

$(document).delegate('#description', "save", function(){
    console.log($(this).find('#id_desc').val());
    $('#menu-description .value').html($(this).find('#id_desc').val().substr(0,20));
});

$(document).delegate('#category', "save", function(){
    var selected = $(this).closest('.panel').find(':radio:checked');
    $('#menu-category .value').html(selected.next().text());
});

$(document).delegate('#category :radio', "change", function(){
    $(this).closest('form').find(':checked').next().addClass('ui-btn-active');
    $(this).closest('form').find(':radio:not(:checked)').next()
            .addClass('ui-radio-off')
            .removeClass('ui-radio-on ui-btn-active')
            .find('.ui-icon')
            .addClass('ui-icon-radio-off')
            .removeClass('ui-icon-radio-on');
});


