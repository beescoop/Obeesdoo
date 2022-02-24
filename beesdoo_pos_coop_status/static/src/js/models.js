odoo.define("beesdoo_pos_coop_status.models", function(require) {
    "use strict";
    var models = require("point_of_sale.models");
    models.load_fields("res.partner", ["can_shop", "state"]);
});
