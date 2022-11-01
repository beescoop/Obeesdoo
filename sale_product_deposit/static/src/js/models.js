odoo.define("beesdoo_product.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");

    var _super_PosModel = models.PosModel.prototype;

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var product_model = _.find(this.models, function (model) {
                return model.model === "product.product";
            });
            product_model.fields.push("total_with_vat");

            // Inheritance
            return _super_PosModel.initialize.call(this, session, attributes);
        },
    });
});
