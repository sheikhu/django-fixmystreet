/* jshint expr: true */

var expect = chai.expect;

describe('L.FixMyStreet.Map', function () {
  var $map;  // The DOM element containing the map.
  var map;  // The Leaflet map (`L.FixMyStreet.Map`).

  beforeEach(function () {
    $map = $('<div id="map" />');
    $map.prependTo($('body'));
    map = new L.FixMyStreet.Map('map');
  });

  afterEach(function () {
    map = null;
    $map.remove();
  });

  describe('???', function () {
    it('should be created', function () {
      // expect($map[0].children.length).to.be.above(0);
      // expect($map.attr('class').split(/\s+/)).to.contain('leaflet-container');
      expect($map.find('.leaflet-map-pane').length).to.equal(1);
    });

    it('constants', function () {
      // @QUESTION: How to set JS var before loading lib?
      expect(map.options.myLayers['map-street'].settings.options.layers).to.be.equal('urbisFR');
    });

    it('check options overwrite', function () {
    });

    it('should be initialized according to options', function () {
      // options.center == map.getCenter()
      // options.zoom == map.getZoom()
      // options.myLayers => layers
      // options.myLayers with opacityControl => opacityControl layer
      // options.incidentTypes => MarkerClusterGroup layers
      // layerControl added on map
      // layerControl contains myLayers + base/overlay
    });

    it('check contraints', function () {
      // options.minZoom: map.setZoom(options.minZoom - 1) => map.getZoom() == options.minZoom
      // options.maxZoom: map.setZoom(options.maxZoom + 1) => map.getZoom() == options.maxZoom
      // options.maxBounds: ??? panTo outside?
      // options. == map.
    });

    it('add incident', function () {
      // for each incident type
        // added in map.incidents[type]
        // added on map
      // for new incident
        // map center & zoom
    });

    it('load from GeoJSON', function () {
      // @QUESTION: How to use mock objects?
      // check from URL and by passing directly a GeoJSON object
    });

    it('remove all incidents', function () {
      // markers removed
      // map.incidents[*] empty
    });

    it('remove new incident', function () {
      // marker removed
      // map.newIncidentMarker === null
    });

    it('filter by incident type', function () {
      // for each incident type
        // call toggle
        // check if markers disappear
        // ----
        // call toggle with visibility, true and false
        // check if markers visible or not
    });

    it('search results', function () {
      // add one result
      // add results (bulk)
        // check markers are created
        // check panel is displayed
          // check panel contains results
      // remove search results
    });

    it('buttons', function () {
      // added at the right position
      // LocateOnMap
        // check click handler
      // StreetView
        // check click handler
      // SizeToggle
        // check click handler
    });

    it('filter', function () {
      // added on map, at the right position
      // content = options.incidentTypes.filtering !== false
    });

    it('', function () {
    });

    it('', function () {
    });

    it('', function () {
    });

    it('', function () {
    });
  });
});
