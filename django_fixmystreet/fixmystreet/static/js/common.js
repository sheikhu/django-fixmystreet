$(document).ready(function(){
    $('#select-language').change(function(){
        $(this).closest('form').submit();
    });

    if ($("#leftMenuPanePro .positionable").length) {
        //Update menu entries with coordinates
        var USER_POSITION = new Object();
        if(navigator.geolocation){
            var options = {timeout:60000};
            var mapReference = this.map;
            navigator.geolocation.getCurrentPosition(
                //success
                function(position) {
                    var latitude = POSY = position.coords.latitude;
                    var longitude = POSX = position.coords.longitude;
                    var p = new Proj4js.Point(longitude, latitude);
                    Proj4js.transform(new Proj4js.Proj("EPSG:4326"), new Proj4js.Proj("EPSG:31370"), p);
                    USER_POSITION.x = p.x;
                    USER_POSITION.y = p.y;
                    updateMenuEntries(p.x,p.y);
                },
                function() {},
            options);
        }
    }
});

function updateMenuEntries(x,y) {
    //Update the left menu coordinates
    var currentHref;
    $("#leftMenuPanePro .positionable").each(function(idx,value){
            currentHref = $(value).attr('href');
            $(value).attr('href',currentHref+'?x='+x+'&y='+y);
    });
        //End update menu	
}
