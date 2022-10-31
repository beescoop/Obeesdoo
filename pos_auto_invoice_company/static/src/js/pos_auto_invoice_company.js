odoo.define("pos_auto_invoice_company.screens", function (require) {
    "use strict";
    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");

    models.load_fields("res.partner", "is_company");

    // Should this be put in a separate module ?
    // Note a pos_auto_invoice module already exists in addons,
    // but it doesn't do the same thing
    screens.PaymentScreenWidget.include({
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

        customer_changed: function () {
            this._super();
            if (this.pos.config.module_account) {
                this.auto_invoice();
            }
        },
    });
});
