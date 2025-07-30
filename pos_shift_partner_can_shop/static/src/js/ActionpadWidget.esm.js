/** @odoo-module */

// SPDX-FileCopyrightText: 2020 Coop IT Easy SC
//
// SPDX-License-Identifier: AGPL-3.0-or-later

import ActionpadWidget from "point_of_sale.ActionpadWidget";
import Registries from "point_of_sale.Registries";
import {_t} from "@web/core/l10n/translation";

const ActionpadWidgetConfirm = () =>
    class extends ActionpadWidget {
        setup() {
            super.setup(...arguments);
        }

        async trigger() {
            const customer_partner = this.env.pos.get_order().get_partner();
            if (
                this.props.actionName.valueOf() === "Payment" &&
                customer_partner &&
                !customer_partner.can_shop
            ) {
                const {confirmed} = await this.showPopup("ConfirmPopup", {
                    title: _t("This customer can not shop."),
                    body: _t(
                        "This member is not up-to-date with his/her shift. \n\n" +
                            "Do you want to proceed to payment?"
                    ),
                });

                if (!confirmed) {
                    return;
                }
            }
            super.trigger(...arguments);
        }
    };

Registries.Component.extend(ActionpadWidget, ActionpadWidgetConfirm);
