(function(){

    module("fb-connect"); // access this test case by running index.html?filter=fb-connect

    test("date time parsing", function() {
        expect(3);
        var expected = new Date('Wed Mar 07 2012 15:28:46 GMT+0100 (CET)').toString();

        equal(window.fms.parseIsoDate('Wed Mar 07 2012 15:28:46 GMT+0100').toString(), expected, "parse standard JavaScript format");
        equal(window.fms.parseIsoDate('2012-03-07T15:28:46 +0100').toString(), expected, "parse iso format");
        // equal(window.fms.parseIsoDate('2012-03-07T14:28:46').toString(), expected, "parse iso format without timezone, UCT > -1 hour"); // not an expected case, FB give a tizoned date
        equal(window.fms.parseIsoDate('2012-03-07 15:28:46').toString(), expected, "parse classic local date time format");
    });

    var me = null;
    FB.login = function mock(callback) {
        setTimeout(function() {
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
        if(path == "/me") {
            setTimeout(function() {
                callback(me);
            },10);
        }
    };

    test("connection", function() {
        $('#qunit-fixture').append(
        '<div class="ui-content">\
            <div id="loggedout">\
                <p>To create a report you have to login</p>\
                <p><a id="login-fb"><span>Login with Facebook</span></a></p>\
            </div>\
            <div id="loggedin">\
                <p>You are logged as:</p>\
                <p><a id="back-report" data-role="button" data-transition="fade" href="#home">Ok</a></p>\
                <p style="margin-top:45px;"><button id="disconnect" data-theme="e">Log off</button></p>\
            </div>\
        </div>');
        
        expect(3);
        
        equal($('#loggedin').css('display'),'none','we are logged out');
        equal($('#loggedout').css('display'),'block','we are logged out');
        $('#login-fb').click(); // mock above do the trick
    });

}());
