
describe('Urbis Map', function(){
    var expect = chai.expect;
    describe('Default Layers', function(){
        it('should init', function(){
            var mapView = new MapView();

            expect(mapView).to.have.property('layers');

            mapView.render();
            expect(mapView).to.have.property('map');
            expect(mapView.$el.hasClass('loading')).equal(true);
        });
    });
});
