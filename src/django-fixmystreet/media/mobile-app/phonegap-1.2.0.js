/**
 * Phongap emulator file
 * Emulate phonegap behavior in a browser
 * fi: getPicture return a random picture
 */
(function($){
    console.log('This is a phonegap emulator, do NOT put it on a mobile')

    if(!navigator){
        window.navigator = {};
    }

    if(!navigator.device){
        navigator.device = {plateform:'emulator'};
    }
    if(!window.device){
        window.device = navigator.device;
    }
    if(!navigator.camera){
        navigator.camera = {};
    }
    if(!navigator.camera.getPicture){
        samples = [
            'http://www.atomicpetals.com/wp-content/themes/default/custom/rotator/home-4.jpg',
            'http://blogs.ubc.ca/CourseBlogSample01/wp-content/themes/thesis/rotator/sample-1.jpg',
            'http://docs.gimp.org/en/images/filters/examples/color-taj-sample-colorize.jpg'
        ];
        navigator.camera.getPicture = function(callback){
            callback(samples[Math.floor(Math.random()*samples.length)]);
        }
        
        
        window.Camera = {}
        Camera.DestinationType = {
            DATA_URL : 0,                // Return image as base64 encoded string
            FILE_URI : 1                 // Return image file URI
        };
        
        Camera.PictureSourceType = {
            PHOTOLIBRARY : 0,
            CAMERA : 1,
            SAVEDPHOTOALBUM : 2
        };
        
        Camera.EncodingType = {
            JPEG : 0,               // Return JPEG encoded image
            PNG : 1                 // Return PNG encoded image
        };
        
        Camera.MediaType = { 
            PICTURE: 0,             // allow selection of still pictures only. DEFAULT. Will return format specified via DestinationType
            VIDEO: 1,               // allow selection of video only, WILL ALWAYS RETURN FILE_URI
            ALLMEDIA : 2            // allow selection from all media types
        };
    }
    
    if($)
    {
        $(function(){
            var keyboard = $('<img src="images/keyboard.jpg"/>').css({
                'width': '100%',
                'position': 'fixed',
                'bottom': 0,
                'z-index':2000
            }).hide();
            $(document.body).append(keyboard);
            $(document).delegate('input[type="text"],textarea', 'focus', function(){
                keyboard.slideDown();
            });
            $(document).delegate('input[type="text"],textarea', 'blur', function(){
                keyboard.hide();
            });
        });
    }
}(jQuery));
