/** @odoo-module alias=pos_eater.ActionpadWidget **/
// SPDX-FileCopyrightText: 2024 Coop IT Easy SC
//
// SPDX-License-Identifier: AGPL-3.0-or-later

import Registries from "point_of_sale.Registries";
import ActionpadWidget from "point_of_sale.ActionpadWidget";

const EaterActionpadWidget = (ActionpadWidget) =>
    class extends ActionpadWidget {
        get eaterNames() {
            const names = this.props.partner.child_eater_ids.map(
                (id) => this.env.pos.db.get_partner_by_id(id).name
            );
            return names.join(", ");
        }
    };

Registries.Component.extend(ActionpadWidget, EaterActionpadWidget);
export default EaterActionpadWidget;
