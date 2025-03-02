odoo.define("beescoop.pos.ticket", function(require) {
    "use strict";
    console.log("loading pos ticket");
    var module = require("point_of_sale.screens");
    var rpc = require("web.rpc");

    module.ReceiptScreenWidget = module.ReceiptScreenWidget.include({
        send: function() {
            var self = this;
            var loaded = new $.Deferred();
            var order = this.pos.get_order().name;
            rpc.query(
                {
                    model: "pos.order",
                    method: "send_order",
                    args: [order],
                    kwargs: {},
                },
                {
                    timeout: 10000,
                    shadow: false,
                }
            )
                .then(function(message) {
                    var el = self.$(".message-send");
                    el.empty();
                    el.append("<h2>" + message + "</h2>");
                })
                .fail(function(type, error) {
                    var el = self.$(".message-send");
                    el.empty();
                    el.append("<h2>" + "Could not send ticket" + "</h2>");
                });
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$(".button.send").click(function() {
                if (!self._locked) {
                    self.send();
                }
            });
        },
        show: function() {
            this._super();
            var self = this;
            this.$(".message-send").empty();
        },
    });
});
