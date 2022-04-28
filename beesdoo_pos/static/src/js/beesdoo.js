odoo.define("beesdoo_pos.screens", function (require) {
    "use strict";
    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");

    models.load_fields("res.partner", "is_company");

    var set_customer_info = function (parent_class, value) {
        var parent = this.$(parent_class);
        var info_div = document.createElement("div");
        info_div.textContent = value;
        if (value) {
            parent.append(info_div);
        }
    };

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
                    result.forEach((client_name) =>
                        set_customer_info.call(
                            self,
                            ".customer-information-pay",
                            client_name
                        )
                    );
                    loaded.resolve();
                })
                .fail(function (type, error) {
                    loaded.reject(error);
                });
            return loaded;
        },
    });

    screens.PaymentScreenWidget.include({
        render_customer_info: function () {
            var self = this;
            var loaded = new $.Deferred();
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
                    set_customer_info.call(self, ".customer-name", client.name);
                    result.forEach((client_name) =>
                        set_customer_info.call(self, ".customer-delegates", client_name)
                    );
                    loaded.resolve();
                })
                .fail(function (type, error) {
                    loaded.reject(err);
                });
            return loaded;
        },

        auto_invoice: function () {
            var self = this;
            var customer = this.pos.get_client();
            var order = this.pos.get_order();
            if (customer && customer.is_company && !order.is_to_invoice()) {
                self.click_invoice();
            }
            if (!customer && order.is_to_invoice()) {
                self.click_invoice();
            }
        },

        renderElement: function () {
            this._super();
            this.render_customer_info();
        },

        customer_changed: function () {
            this._super();
            if (this.pos.config.module_account) {
                this.auto_invoice();
            }
            this.render_customer_info();
        },
    });
});
