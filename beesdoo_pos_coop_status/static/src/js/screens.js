/*
 Copyright (C) 2020-Today Coop IT Easy SCRLfs
 @author: Robin Keunen <robin@coopiteasy.be>
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define("beesdoo_pos_coop_status.screens", function(require) {
    "use strict";

    var screens = require("point_of_sale.screens");

    screens.ActionpadWidget.include({
        renderElement: function() {
            // Get click handler to wrap it w/ our code
            var self = this;
            this._super();
            var button_pay_click_handler = $._data(this.$el.find(".pay")[0], "events")
                .click[0].handler;
            var button_pay = this.$(".pay");
            button_pay.off("click");

            // Wrap click handler
            button_pay.click(function() {
                var client = self.pos.get_client();
                if (client && client.can_shop) {
                    button_pay_click_handler();
                } else if (client && !client.can_shop) {
                    self.gui.show_popup("confirm", {
                        title: _t("This cooperator cannot shop."),
                        body: _t(
                            "This cooperator is not up-to-date with his/her shift. \n\n" +
                                "Do you want to proceed to payment?"
                        ),
                        confirm: function() {
                            button_pay_click_handler();
                        },
                    });
                } else {
                    self.gui.show_popup("confirm", {
                        title: _t("No customer set."),
                        body: _t(
                            "You did no select a customer. Do you want to proceed to payment?"
                        ),
                        confirm: function() {
                            button_pay_click_handler();
                        },
                    });
                }
            });
        },
    });
});
