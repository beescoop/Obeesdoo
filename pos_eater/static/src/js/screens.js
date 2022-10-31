odoo.define("pos_eater.screens", function (require) {
    "use strict";
    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");

    models.load_fields("res.partner", "is_company");

    screens.ActionpadWidget.include({
        renderElement: function () {
            var self = this;
            var loaded = new $.Deferred();
            this._super();
            var client = this.pos.get_client();
            if (!client) {
                return;
            }
            this._rpc(
                {
                    model: "res.partner",
                    method: "get_eater",
                    args: [client.id],
                },
                {
                    shadow: true,
                },
                {
                    timeout: 1000,
                }
            )
                .then(function (result) {
                    var eaters = result.join("<br />");
                    self.$(".customer-information-pay").html(eaters);
                    loaded.resolve();
                })
                .fail(function (type, error) {
                    loaded.reject(error);
                });
            return loaded;
        },
    });
});
