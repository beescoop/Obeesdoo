/** @odoo-module */

// SPDX-FileCopyrightText: 2025 Coop IT Easy SC
//
// SPDX-License-Identifier: AGPL-3.0-or-later

import PaymentScreen from "point_of_sale.PaymentScreen";
import Registries from "point_of_sale.Registries";
import {onWillStart} from "@odoo/owl";

const ExtendedPaymentScreen = (OriginalPaymentScreen) =>
    class extends OriginalPaymentScreen {
        setup() {
            super.setup(...arguments);
            onWillStart(() => {
                this.auto_invoice();
            });
        }
        async selectPartner() {
            await super.selectPartner(...arguments);
            this.auto_invoice();
        }
        auto_invoice() {
            var order = this.currentOrder;
            var partner = order.get_partner();
            order.set_to_invoice(partner && partner.is_company);
        }
    };

Registries.Component.extend(PaymentScreen, ExtendedPaymentScreen);
