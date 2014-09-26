/* jshint expr: true */

var expect = chai.expect;

function async(done, fct) {
  try {
    fct();
    done();
  } catch (error) {
    done(error);
  }
}


describe('L.FixMyStreet.Util', function () {
  var LATLNG = new L.LatLng(50.8460974, 4.3694384000000355);
  var POINT = new L.Point(LATLNG.lng, LATLNG.lat);
  var POINT_31370 = {x: 150048.32, y: 170632.53};  // Computed from LATLNG on http://epsg.io/31370/map
  var ADDRESS = {
    street: 'Avenue des Arts',
    number: '21',
    postalCode: '1000',
    city: 'Brussels',
    latlng: LATLNG,
  };
  var URBIS_ADDRESS_FROM_LATLNG_RESULT = {
    adNc: '10005006  21',
    address: {
      number: '21',
      street: {
        id: '5583',
        name: 'Avenue des Arts',
        postCode: '1000',
      },
    },
    addresspointid: '2108357',
    geocodematchcode: 1,
    point: {
      x: 4.369348321556435,
      y: 50.84611094405465,
    },
    streetaxisid: '11026560',
    streetsectionid: '11026504',
  };


  var _expectOriginalLatLng = function (result, delta) {
    expect(result).to.be.instanceOf(L.LatLng);
    if (delta === undefined || delta === 0) {
      expect(result.lat).to.be.equal(LATLNG.lat);
      expect(result.lng).to.be.equal(LATLNG.lng);
    } else {
      expect(result.lat).to.be.closeTo(LATLNG.lat, delta);
      expect(result.lng).to.be.closeTo(LATLNG.lng, delta);
    }
  };

  var _expectOriginalPoint = function (result, delta) {
    expect(result).to.be.instanceOf(L.Point);
    if (delta === undefined || delta === 0) {
      expect(result.x).to.be.equal(POINT.x);
      expect(result.y).to.be.equal(POINT.y);
    } else {
      expect(result.x).to.be.closeTo(POINT.x, delta);
      expect(result.y).to.be.closeTo(POINT.y, delta);
    }
  };

  var _expectOriginalPoint31370 = function (result, delta) {
    expect(result).to.be.instanceOf(L.Point);
    if (delta === undefined || delta === 0) {
      expect(result.x).to.be.equal(POINT_31370.x);
      expect(result.y).to.be.equal(POINT_31370.y);
    } else {
      expect(result.x).to.be.closeTo(POINT_31370.x, delta);
      expect(result.y).to.be.closeTo(POINT_31370.y, delta);
    }
  };

  var _expectOriginalAddress = function (result) {
    expect(result.street.toLowerCase()).to.be.equal(ADDRESS.street.toLowerCase());
    expect(result.number.toLowerCase()).to.be.equal(ADDRESS.number.toLowerCase());
    expect(result.postalCode.toLowerCase()).to.be.equal(ADDRESS.postalCode.toLowerCase());
    expect(result.city.toLowerCase()).to.be.equal(ADDRESS.city.toLowerCase());
    expect(result.latlng.lat).to.be.closeTo(ADDRESS.latlng.lat, 0.0001);
    expect(result.latlng.lng).to.be.closeTo(ADDRESS.latlng.lng, 0.0001);
  };


  it('should initialize correclty', function () {
    expect(LATLNG).to.be.instanceOf(L.LatLng);
    expect(POINT).to.be.instanceOf(L.Point);
  });


  describe('_initProj4js', function () {
    it('should convert correctly', function () {
      expect(L.FixMyStreet.Util.PROJ4JS_4326).to.be.undefined;
      expect(L.FixMyStreet.Util.PROJ4JS_31370).to.be.undefined;

      L.FixMyStreet.Util._initProj4js();
      expect(L.FixMyStreet.Util.PROJ4JS_4326).to.be.instanceOf(Proj4js.Proj);
      expect(L.FixMyStreet.Util.PROJ4JS_31370).to.be.instanceOf(Proj4js.Proj);
    });
  });


  describe('toLatLng', function () {
    var _expectLatLng = function (value) {
      var result = L.FixMyStreet.Util.toLatLng(value);
      _expectOriginalLatLng(result);
    };

    var _expectException = function (value) {
      var fn = function () {
        L.FixMyStreet.Util.toLatLng(value);
      };
      expect(fn).to.throw(TypeError);
    };

    it('should accept undefined and null', function () {
      expect(L.FixMyStreet.Util.toLatLng(undefined)).to.be.undefined;
      expect(L.FixMyStreet.Util.toLatLng(null)).to.be.null;
    });

    it('should accept a L.LatLng', function () {
      var result = L.FixMyStreet.Util.toLatLng(LATLNG);
      expect(result).to.be.instanceOf(L.LatLng);
      expect(result).to.be.equal(LATLNG);
    });

    it('should accept a L.Point', function () {
      _expectLatLng(POINT);
    });

    it('should accept a string "Lat,Lng"', function () {
      var str = LATLNG.lat + ',' + LATLNG.lng;
      expect(str).to.be.a('string');
      _expectLatLng(str);
    });

    it('should accept a string "Lat, Lng"', function () {
      var str = LATLNG.lat + ', ' + LATLNG.lng;
      expect(str).to.be.a('string');
      _expectLatLng(str);
    });

    it('should accept a LatLng dictionary {lat: Lat, lng: Lng}', function () {
      var obj = {lat: LATLNG.lat, lng: LATLNG.lng};
      _expectLatLng(obj);
    });

    it('should accept a LatLng array [Lat, Lng]', function () {
      var obj = [LATLNG.lat, LATLNG.lng];
      _expectLatLng(obj);
    });

    it('should accept a Point dictionary {x: X, y: Y}', function () {
      var obj = {x: POINT.x, y: POINT.y};
      _expectLatLng(obj);
    });

    it('should throw an Error otherwise', function () {
      _expectException('non-valid, value');
      _expectException('non-valid-value');

      _expectException({lat: 'non-valid-value', lng: 123});
      _expectException({lat: 'non-valid-value', key: 123});

      _expectException(['non-valid-value', 123.45]);

      _expectException({x: 'non-valid-value', y: 123});
      _expectException({x: 'non-valid-value', key: 123});
    });
  });


  describe('toPoint', function () {
    var _expectPoint = function (value) {
      var result = L.FixMyStreet.Util.toPoint(value);
      _expectOriginalPoint(result);
    };

    var _expectException = function (value) {
      var fn = function () {
        L.FixMyStreet.Util.toPoint(value);
      };
      expect(fn).to.throw(TypeError);
    };

    it('should accept undefined and null', function () {
      expect(L.FixMyStreet.Util.toPoint(undefined)).to.be.undefined;
      expect(L.FixMyStreet.Util.toPoint(null)).to.be.null;
    });

    it('should accept a L.Point', function () {
      var result = L.FixMyStreet.Util.toPoint(POINT);
      expect(result).to.be.instanceOf(L.Point);
      expect(result).to.be.equal(POINT);
    });

    it('should accept a L.LatLng', function () {
      _expectPoint(LATLNG);
    });

    it('should accept a string "X,Y"', function () {
      var str = POINT.x + ', ' + POINT.y;
      expect(str).to.be.a('string');
      _expectPoint(str);
    });

    it('should accept a Point dictionary {x: X, y: Y}', function () {
      var obj = {x: POINT.x, y: POINT.y};
      _expectPoint(obj);
    });

    it('should accept a Point array [X, Y]', function () {
      var obj = [POINT.x, POINT.y];
      _expectPoint(obj);
    });

    it('should accept a LatLng dictionary {lat: Lat, lng: Lng}', function () {
      var obj = {lat: LATLNG.lat, lng: LATLNG.lng};
      _expectPoint(obj);
    });

    it('should throw an Error otherwise', function () {
      _expectException('non-valid, value');
      _expectException('non-valid-value');

      _expectException({x: 'non-valid-value', y: 123});
      _expectException({x: 'non-valid-value', key: 123});

      _expectException(['non-valid-value', 123.45]);

      _expectException({lat: 'non-valid-value', lng: 123});
      _expectException({lat: 'non-valid-value', key: 123});
    });
  });


  describe('fromUrbisCoords', function () {
    it('should convert correctly', function () {
      var result = L.FixMyStreet.Util.fromUrbisCoords(POINT_31370);
      _expectOriginalPoint(result, 0.0000008);  // Min: 0.00000065
    });
  });


  describe('toUrbisCoords', function () {
    it('should convert correctly', function () {
      var result = L.FixMyStreet.Util.toUrbisCoords(POINT);
      _expectOriginalPoint31370(result, 0.08);  // Min: 0.065
    });
  });


  describe('urbisCoordsToLatLng', function () {
    it('should convert correctly', function () {
      var result = L.FixMyStreet.Util.urbisCoordsToLatLng(POINT_31370);
      _expectOriginalLatLng(result, 0.0000008);  // Min: 0.00000065
    });
  });


  describe('getAddressFromLatLng', function () {
    it('should convert correctly', function (done) {
      L.FixMyStreet.Util.getAddressFromLatLng(LATLNG, function (result) {
        async(done, function () {
          _expectOriginalAddress(result);
        // }, function (response) {
        //   done(response);
        });
      });
    });
  });


  describe('urbisResultToAddress', function () {
    it('should convert correctly', function () {
      var result = L.FixMyStreet.Util.urbisResultToAddress(URBIS_ADDRESS_FROM_LATLNG_RESULT);
      _expectOriginalAddress(result);
    });
  });


  describe('getStreetViewUrl', function () {
    // @TODO
  });


  describe('_toProj4jsPoint', function () {
    it('should convert correctly', function () {
      var result = L.FixMyStreet.Util._toProj4jsPoint(POINT);
      expect(result).to.be.instanceOf(Proj4js.Point);
      expect(result.x).to.be.equal(POINT.x);
      expect(result.y).to.be.equal(POINT.y);
    });
  });
});
