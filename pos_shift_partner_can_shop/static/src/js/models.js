odoo.define("pos_shift_partner_can_shop.models", function (require) {
    "use strict";
    var models = require("point_of_sale.models");
    models.load_fields("res.partner", ["can_shop", "state"]);
});
