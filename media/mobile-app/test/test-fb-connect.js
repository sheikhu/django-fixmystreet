module("fb-connect"); // access this test case by running index.html?filtre=fb-connect

test("date time parsing", function() {
    create_frame('../index.html',function(window) {
        expect(3);
        var fms = window.fms;
        var expected = new Date('Wed Mar 07 2012 15:28:46 GMT+0100 (CET)').toString();

        equal(fms.parseIsoDate('Wed Mar 07 2012 15:28:46 GMT+0100').toString(), expected, "parse standard JavaScript format");
        equal(fms.parseIsoDate('2012-03-07T15:28:46 +0100').toString(), expected, "parse iso format");
        // equal(fms.parseIsoDate('2012-03-07T14:28:46').toString(), expected, "parse iso format without timezone, UCT > -1 hour"); // not an expected case, FB give a tizoned date
        equal(fms.parseIsoDate('2012-03-07 15:28:46').toString(), expected, "parse classic local date time format");
    });
});

test("connection", function() {
    create_frame('../index.html',function(window) {

        var $ = window.jQuery;
        var document = window.document;
        var FB = window.FB;
        expect(7);
        
        equal($('#loggedin').css('display'),'none','we are logged out');
        equal($('#loggedout').css('display'),'block','we are logged out');
        stop(2);

        mockify(FB, function() {
            equal($('#loggedin').css('display'),'block','we are logged in');
            equal($('#loggedout').css('display'),'none','we are logged in');
        });
        $(document).bind('connected',function() {
            ok(true, 'connected event fired');
        });
        $('#login-fb').click(); // mock below do the trick
    });
});





function create_frame(path, callback) {
    var content = $('<iframe />');
    content.prop('src', path);
    content.prop('width',320);
    content.prop('height',480);
    content.prop('frameborder',0);
    $('#qunit-fixture').append(content);

    stop();
    // wait iframe ready
    content.load(function() {
        start();
        console.log(content[0].contentWindow);
        callback(content[0].contentWindow);
    });
}

function mockify(FB, end_cb) {
    var me = null;
    FB.login = function mock(callback) {
        setTimeout(function() {
            ok(true, 'login() called'); start();
            me = {
                name:'test',
                email:'test@fixmystreet.irisnet.be'
            };
            callback({
                session:{
                    access_token:'token',
                    expires:'2012-03-07T15:28:46 +0100'
                }
            });
        },100);
    };

    FB.api = function mock(path, callback) {
        if(path == '/me') {
            setTimeout(function() {
                ok(true, 'api(/me) called'); start();
                callback(me);
                end_cb();
            },10);
        }
    };
}


