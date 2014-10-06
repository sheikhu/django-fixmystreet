/* jshint expr: true */

var expect = chai.expect;

describe('L.FixMyStreet.UrbisLayersSettings', function () {
  describe('???', function () {
    $.each(L.FixMyStreet.UrbisLayersSettings, function (k, v) {
      it('URL for "' + k + '" should return data', function (done) {
        var url = v.url +
                  '?SERVICE=' + encodeURIComponent(v.type.toUpperCase()) +
                  '&REQUEST=GetMap' +
                  '&VERSION=1.1.1' +
                  '&LAYERS=' + encodeURIComponent(v.options.layers) +
                  '&FORMAT=' + encodeURIComponent(v.options.format) +
                  (v.options.styles === undefined ? '' : '&STYLES=' + encodeURIComponent(v.options.styles)) +
                  (v.options.filter === undefined ? '' : '&FILTER=' + encodeURIComponent(v.options.filter)) +
                  '&TRANSPARENT=' + (v.options.transparent ? 'true' : 'false') +
                  '&SRS=' + encodeURIComponent(v.options.crs === undefined ? 'EPSG:3857' : v.options.crs.code) +
                  '&HEIGHT=256&WIDTH=256' +
                  '&BBOX=481859.0263097511,6594375.304218728,484305.01121487666,6596821.289123851';
        expectUrlWorks(url, done);
      });
    });
  });
});
