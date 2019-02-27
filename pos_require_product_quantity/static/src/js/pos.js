/*
  Copyright 2019 Coop IT Easy SCRLfs
  	    Robin Keunen <robin@coopiteasy.be>
  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/

odoo.define(

'pos_require_product_quantity.pos_require_product_quantity',
function (require) {
"use strict";

var core = require('web.core');
var models = require('point_of_sale.models');
var screens = require("point_of_sale.screens");

var _t = core._t;
var orderline_prototype = models.Orderline.prototype;

models.Orderline = models.Orderline.extend({
    initialize: function (attr, options) {
        orderline_prototype.initialize.call(this, attr, options);

        var unit = this.get_unit();
        if (unit) {
            if (unit.category_id[1] === 'Unit') {
                this.set_quantity(1);
            } else {
                this.set_quantity(0);
            }
        }
    }
});

screens.ActionpadWidget = screens.ActionpadWidget.include({
    renderElement: function () {
        var self = this;
        this._super();

        this.$('.pay').click(function(){

            if (self.pos.config.require_product_quantity) {

                var orderlines = self.pos.get_order().orderlines;
                var qty_unset_list = [];

                for(var i = 0; i < orderlines.length; i++) {
                    var line = orderlines.models[i];
                    if (line.quantity === 0) {
                        qty_unset_list.push(line);
                    }
                }
                if (qty_unset_list.length > 0) {
                    self.gui.back();
                    var body = _t('No quantity set for products:');
                    for (var i = 0; i < qty_unset_list.length; i++) {
                        body = body + '  - ' + qty_unset_list[i].product.display_name;
                    }
                    self.gui.show_popup(
                        'alert',
                        {
                            'title': _t('Missing quantities'),
                            'body': body,
                        });
                }
            }
        });
    }
})

});
