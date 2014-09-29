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
