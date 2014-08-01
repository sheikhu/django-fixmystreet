
describe('Urbis Map', function(){
    var expect = chai.expect;
    describe('Default Layers', function(){
        it('should init', function(){
            var $mapEl = $('<div id="map"> </div>');
            var map = new L.FixMyStreet.Map($mapEl[0]);

            expect(L.FixMyStreet.Map).to.have.property('namedLayersSettings');
        });
    });
});
