odoo.define('beescoop.pos', function (require) {
    "use strict";
    var module   = require("point_of_sale.screens");
    var Model = require('web.DataModel');
    var set_customer_info = function(el_class, value, prefix) {
        var el = this.$(el_class);
        el.empty();
        if (prefix && value) {
            value = prefix + value
        }
        if (value) {
            el.append(value);
        }
    }

// TODO: will be taken care of in separate 'pos_order_email' module
/*    module.ReceiptScreenWidget = module.ReceiptScreenWidget.include({
        send : function() {
            var self = this;
            var loaded = new $.Deferred();
            var order = this.pos.get_order().name;
            var records = new Model('pos.order').call('send_order', [order], {}, { shadow: false, timeout: 10000});
            records.then(function(result){
                var el = self.$('.message-send')
                el.empty();
                el.append('<h2>' + result + '</h2>');
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
        show: function(){
            this._super();
            var self = this;
            this.$('.message-send').empty();
        },
    })*/

    module.ActionpadWidget = module.ActionpadWidget.include({
        renderElement : function() {
            var self = this;
            var loaded = new $.Deferred();
            this._super();
            if (!this.pos.get_client()) {
                return

            }
            var customer_id = this.pos.get_client().id;
            var res = new Model('res.partner').call('get_eater',
                    [ customer_id ], undefined, { shadow: true, timeout: 1000});
            res.then(function(result) {
                set_customer_info.call(self, '.customer-delegate1', result[0], 'Eater 1: ');
                set_customer_info.call(self, '.customer-delegate2', result[1], 'Eater 2: ');
                set_customer_info.call(self, '.customer-delegate3', result[2], 'Eater 3: ');
            }, function(err) {
                loaded.reject(err);
            });
        },
    });

    module.PaymentScreenWidget.include({
        render_customer_info : function() {
            var self = this;
            var loaded = new $.Deferred();
            if (!this.pos.get_client()) {
                return
            }
            var customer_id = this.pos.get_client().id;
            var res = new Model('res.partner').call('get_eater', [ customer_id ], undefined, { shadow: true, timeout: 1000});
            res.then(function(result) {
                set_customer_info.call(self, '.customer-name', self.pos.get_client().name);
                set_customer_info.call(self, '.customer-delegate1', result[0], 'Eater 1: ');
                set_customer_info.call(self, '.customer-delegate2', result[1], 'Eater 2: ');
                set_customer_info.call(self, '.customer-delegate3', result[2], 'Eater 3: ');
            }, function(err) {
                loaded.reject(err);
            });
        },
        renderElement : function() {
            this._super();
            this.render_customer_info();
        },
        customer_changed : function() {
            this._super();
            this.render_customer_info();
        },
    });
});
