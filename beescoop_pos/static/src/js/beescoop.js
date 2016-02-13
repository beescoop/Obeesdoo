odoo.define('beescoop.pos', function (require) {
    "use strict";
    var module   = require("point_of_sale.screens");
    var Model = require('web.DataModel');

    module.ReceiptScreenWidget = module.ReceiptScreenWidget.include({
        send : function() {
            var order = this.pos.get_order().name;
            var records = new Model('pos.order').call('send_order', [order], {});
            records.then(function(result){
                console.log(result)
            },function(err){
                loaded.reject(err);
            });
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.button.send').click(function(){
                if (!self._locked) {
                    self.send();
                }
            });
        },
    })
});