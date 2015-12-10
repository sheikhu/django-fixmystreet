/* jshint expr: true */

var expect = chai.expect;

describe('L.FixMyStreet.Map', function () {
  var $map;  // The DOM element containing the map.
  var map;  // The Leaflet map (`L.FixMyStreet.Map`).
  var ANIMATION_DELAY = 250;  // Delay to wait for the animation to finish.


  beforeEach(function () {
    $map = $('<div id="map" />');
    $map.prependTo($('body'));
    map = new L.FixMyStreet.Map('map');
  });

  afterEach(function () {
    map = null;
    $map.remove();
  });


  describe('Initialization', function () {
    it('should be created', function () {
      expect($map.find('.leaflet-map-pane').length).to.equal(1);
      // Other option: expect($map[0].children.length).to.be.above(0);
      // Other option: expect($map.attr('class').split(/\s+/)).to.contain('leaflet-container');
    });

//     it('constants', function () {
//       // @TODO
//       // @QUESTION: How to set JS var before loading lib?
//       expect(map.options.myLayers['map-street'].settings.options.layers).to.be.equal('urbisFR');
//     });
//
//     it('check options overwrite', function () {
//       // @TODO
//     });

    it('zoom and center', function () {
      expectLatLngEqual(map.getCenter(), L.FixMyStreet.Util.toLatLng(map.options.center));
      expect(map.getZoom()).to.be.equal(map.options.zoom);
    });

    it('check contraints', function () {
      if (map.options.minZoom !== undefined) {
        map.setZoom(map.options.minZoom - 1);
        window.setTimeout(function () {  // Animation => delay
          expect(map.getZoom()).to.be.equal(map.options.minZoom);
        }, ANIMATION_DELAY);
      }
      if (map.options.maxZoom !== undefined) {
        map.setZoom(map.options.maxZoom + 1);
        window.setTimeout(function () {  // Animation => delay
          expect(map.getZoom()).to.be.equal(map.options.maxZoom);
        }, ANIMATION_DELAY);
      }
    });

    it('map layers', function () {
      $.each(map.options.myLayers, function (k, v) {
        expect(v._layer).to.be.instanceOf(L.TileLayer);
        if (v.visible === true) {
          expect(v._layer._map).to.not.be.undefined;
        } else {
          expect(v._layer._map).to.be.undefined;
        }
      });
    });

    it('incidents', function () {
      for (var k in map.options.incidentTypes) {
        expect(map.incidents[k]).to.be.eql([]);
      }
      expect(map._incidentLayer).to.be.instanceOf(L.MarkerClusterGroup);
    });

    it('controls', function () {
      expectSelectorExists('#map .leaflet-control-container .leaflet-top.leaflet-left .leaflet-control-zoom');
      expectSelectorExists('#map .leaflet-control-container .leaflet-top.leaflet-right .leaflet-control-layers');
      expectSelectorExists('#map .leaflet-control-container .leaflet-bottom.leaflet-left .leaflet-control-attribution');
      // @TODO: options.myLayers with opacityControl => opacityControl layer
    });

    it('layers control', function () {
      // @TODO: Verify visibility?
      // Build lists of base layers and overlays from options.
      var baseLayers = [];
      var overlays = [];
      $.each(map.options.myLayers, function (k, v) {
        (map.isOverlayLayer(v) ? overlays : baseLayers).push(map.getLayerTitleForControl(v));
      });

      // Verify base layers elements
      var existingBaseLayers = $('#map .leaflet-control-container .leaflet-top.leaflet-right .leaflet-control-layers-base > label > span');
      if (baseLayers.length <= 1) {  // Less than 2 choices => no elements
        expect(existingBaseLayers.length).to.be.equal(0);
      } else {
        existingBaseLayers.each(function (i) {
          var title = $(this).text().trim();
          var index = baseLayers.indexOf(title);
          expect(index).to.not.be.equal(-1);
          baseLayers.splice(index, 1);
        });
        expect(baseLayers.length).to.be.equal(0);
      }

      // Verify overlays elements
      $('#map .leaflet-control-container .leaflet-top.leaflet-right .leaflet-control-layers-overlays > label > span').each(function (i) {
        var title = $(this).text().trim();
        var index = overlays.indexOf(title);
        expect(index).to.not.be.equal(-1);
        overlays.splice(index, 1);
      });
      expect(overlays.length).to.be.equal(0);
    });
  });


  describe('Incidents', function () {
    var incidentTypes = ['new', 'reported', 'ongoing', 'closed', 'other'];
    // var incidentTypes = ['reported'];

    it('add incident', function () {
      $.each(incidentTypes, function (k, v) {
        expect($('#map .leaflet-marker-pane > .leaflet-marker-icon').length).to.be.equal(0);
        var model = {
          type: v,
        };
        map.addIncident(model);
        expect($('#map .leaflet-marker-pane > .leaflet-marker-icon').length).to.be.equal(1);
        if (v === 'new') {
          map.removeNewIncident();
        } else {
          map.removeAllIncidents();
        }
      });
    });


//     it('load from GeoJSON', function () {
//       // @TODO
//       // @QUESTION: How to use mock objects?
//       // check from URL and by passing directly a GeoJSON object
//     });
//
//     it('remove all incidents', function () {
//       // @TODO
//       // markers removed
//       // map.incidents[*] empty
//     });
//
//     it('remove new incident', function () {
//       // @TODO
//       // marker removed
//       // map.newIncidentMarker === null
//     });
//
//     it('filter by incident type', function () {
//       // @TODO
//       // for each incident type
//         // call toggle
//         // check if markers disappear
//         // ----
//         // call toggle with visibility, true and false
//         // check if markers visible or not
//     });
//
//     it('search results', function () {
//       // @TODO
//       // add one result
//       // add results (bulk)
//         // check markers are created
//         // check panel is displayed
//           // check panel contains results
//       // remove search results
//     });
//
//     it('buttons', function () {
//       // @TODO
//       // added at the right position
//       // LocateOnMap
//         // check click handler
//       // StreetView
//         // check click handler
//       // SizeToggle
//         // check click handler
//     });
//
//     it('filter', function () {
//       // @TODO
//       // added on map, at the right position
//       // content = options.incidentTypes.filtering !== false
//     });
  });
});
