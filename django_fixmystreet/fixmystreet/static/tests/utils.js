/* jshint expr: true */

function asyncExpect (done, fct) {
  // Usage:
  // $.get('http://...', {data: 'value'}, function (data, textStatus, jqXHR) {
  //   asyncExpect(done, function () {
  //     expect(...);
  //     done();
  //   });
  // );

  try {
    fct();
    done();
  } catch (error) {
    done(error);
  }
}

function expectUrlWorks (url, done) {
  $.get(url, {}, function (data, textStatus, jqXHR) {
    asyncExpect(done, function () {
      expect(jqXHR.status).to.be.equal(200);
      expect(data).to.not.be.empty;
      done();
    });
  });
}

function expectLatLngEqual (value, refValue, delta) {
  expect(value).to.be.instanceOf(L.LatLng);
  if (delta === undefined || delta === 0) {
    expect(value.lat).to.be.equal(refValue.lat);
    expect(value.lng).to.be.equal(refValue.lng);
  } else {
    expect(value.lat).to.be.closeTo(refValue.lat, delta);
    expect(value.lng).to.be.closeTo(refValue.lng, delta);
  }
}

function expectPointEqual (value, refValue, delta) {
  expect(value).to.be.instanceOf(L.Point);
  if (delta === undefined || delta === 0) {
    expect(value.x).to.be.equal(refValue.x);
    expect(value.y).to.be.equal(refValue.y);
  } else {
    expect(value.x).to.be.closeTo(refValue.x, delta);
    expect(value.y).to.be.closeTo(refValue.y, delta);
  }
}

function expectSelectorExists (selector) {
  expect($(selector).length).to.not.be.equal(0);
}
