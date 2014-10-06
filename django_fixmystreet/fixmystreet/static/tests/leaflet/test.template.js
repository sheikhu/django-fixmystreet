/* jshint expr: true */

var expect = chai.expect;


describe('L.FixMyStreet.Template', function () {
  L.FixMyStreet.Template.options = {
    templates: {
      base:
        '<div class="base">' +
          '<h1>{_heading_}</h1>' +
          '<div class="partial">{_partial_}</div>' +
        '</div>',
      _heading_:
        gettext('Test #<% this.number %>'),
      _partial_:
        '<div class="partial-inner">' +
          '<% if (this.valueTrue) { %>' +
            '<div><% this.contentIfTrue %></div>' +
          '<% } else { %>' +
            '<div><% this.contentIfFalse %></div>' +
          '<% } %>' +
          '<div><% (this.valueFalse ? \'true\' : \'false\') %></div>' +
        '</div>' +
        '<ul>' +
          '<% for (var i in this.items) { %>' +
            '<li>' +
              '<% this.items[i].num %>: <% this.items[i].name %>' +
            '</li>' +
          '<% } %>' +
        '</ul>',
    },
  };
  var TEMPLATE_DATA = {
    number: 123,
    valueTrue: true,
    valueFalse: false,
    contentIfTrue: 'The test evaluated to "true".',
    contentIfFalse: 'The test evaluated to "false".',
    items: [
      {num: 1, name: 'First result'},
      {num: 'B', name: 'Second result'},
      {num: 'C', name: 'Third result'},
    ],
  };
  var TEMPLATE_RENDERED =
    '<div class="base">' +
      '<h1>Test #123</h1>' +
      '<div class="partial">' +
        '<div class="partial-inner">' +
          '<div>The test evaluated to "true".</div>' +
          '<div>false</div>' +
        '</div>' +
        '<ul>' +
          '<li>1: First result</li>' +
          '<li>B: Second result</li>' +
          '<li>C: Third result</li>' +
        '</ul>' +
      '</div>' +
    '</div>';


  it('should render correctly', function (done) {
    L.FixMyStreet.Template._render(TEMPLATE_DATA, function (error, html) {
      asyncExpect(done, function () {
        expect(html).to.be.equal(TEMPLATE_RENDERED);
      });
    });
  });
});
