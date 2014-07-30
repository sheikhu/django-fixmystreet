/* jshint expr: true */

var expect = chai.expect;
describe('Search Address Page', function () {
    describe('Message View', function () {
        var message;

        beforeEach(function () {
            message = new fms.MessageView({
                el: $('<div> </div>')
            });
            message.render().$el.appendTo('body');
        });

        afterEach(function () {
            message.remove();
        });

        it('should init without error', function () {
            expect(message).to.have.property('$el');
        });

        it('should be empty when cleared', function () {
            expect(message.$el.find('p').length).to.equal(0);

            message.show('test');
            expect(message.$el.find('p').length).to.equal(1);

            message.clear();
            expect(message.$el.find('p').length).to.equal(0);

            message.show('test');
            expect(message.$el.find('p').length).to.equal(1);
        });

        it('should show message with css class', function () {
            message.show('test');
            expect(message.$el.find('.text-error').length).to.equal(0);

            message.clear();
            message.error('test');
            expect(message.$el.find('.text-error').length).to.equal(1);
        });
    });

    describe('Address Proposal View', function () {
        var addressProposal, addessFixtures = [
            {"language":"fr","address":{"street":{"name":"Avenue Capart","postCode":"1090","municipality":"Jette","id":"749"},"number":""},"point":{"x":146637.084634569,"y":175061.451139995}},
            {"language":"fr","address":{"street":{"name":"Avenue de Laeken","postCode":"1090","municipality":"Jette","id":"2756"},"number":""},"point":{"x":146819.390083262,"y":173428.145026864}},
            {"language":"fr","address":{"street":{"name":"Avenue des Muses","postCode":"1180","municipality":"Uccle","id":"3476"},"number":""},"point":{"x":149498.762522229,"y":162913.383760823}},
            {"language":"fr","address":{"street":{"name":"Avenue de Jette","postCode":"1090","municipality":"Jette","id":"2628"},"number":""},"point":{"x":146881.532577937,"y":173414.37252241}},
            {"language":"fr","address":{"street":{"name":"Avenue Wolvendael","postCode":"1180","municipality":"Uccle","id":"5413"},"number":""},"point":{"x":148181.710664958,"y":165322.414564594}},
            {"language":"fr","address":{"street":{"name":"Avenue des Abeilles","postCode":"1050","municipality":"Ixelles","id":"16"},"number":""},"point":{"x":151374.070284113,"y":165954.223214778}},
            {"language":"fr","address":{"street":{"name":"Avenue de l'Agneau","postCode":"1180","municipality":"Uccle","id":"47"},"number":""},"point":{"x":148386.317966909,"y":163006.854217643}},
            {"language":"fr","address":{"street":{"name":"Avenue de l'Aiglon","postCode":"1180","municipality":"Uccle","id":"56"},"number":""},"point":{"x":149575.956870891,"y":163696.117865531}},
            {"language":"fr","address":{"street":{"name":"Avenue Albert","postCode":"1180","municipality":"Uccle","id":"66"},"number":""},"point":{"x":148498.134297517,"y":167108.427855707}},
            {"language":"fr","address":{"street":{"name":"Avenue des Alisiers","postCode":"1180","municipality":"Uccle","id":"84"},"number":""},"point":{"x":147831.199437604,"y":162799.376468544}}
        ];

        beforeEach(function () {
            addressProposal = new fms.AddressProposalView({
                el: $('<div> </div>')
            });
            addressProposal.render().$el.appendTo('body');
        });

        afterEach(function () {
            addressProposal.remove();
        });

        it('should init without error', function () {
            expect(addressProposal).to.have.property('$el');
        });

        xit('should show addresses', function () {
            addressProposal.open(addessFixtures);
            expect(addressProposal.render().$el.is(':visible')).to.be.true;
        });

        xit('should show markers on map', function () {
        });

        xit('should paginate', function () {
        });

        xit('should paginate markers on map', function () {
        });

        xit('should close', function () {
        });
    });
});
