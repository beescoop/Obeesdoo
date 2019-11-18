odoo.define('beesdoo_shift.barcode_scanner_focus', function (require) {
"use strict";

    var core = require('web.core');

    var FormViewBarcodeHandler = require('barcodes.FormViewBarcodeHandler');

    var BarcodeHandlerUnfocus = FormViewBarcodeHandler.extend({
        _set_quantity_listener: function(event) {
            console.log("TEST");
            this.super();
        },
        // Method is not called when a field is focus.
        on_barcode_scanned: function(barcode) {
             console.log("method called");
            this._super(barcode);
        }
    });
core.form_widget_registry.add('barcode_handler_unfocus', BarcodeHandlerUnfocus);

return BarcodeHandlerUnfocus;
/*
    var Widget = require('web.Widget');
    var BarcodeHandlerUnfocus = Widget.extend({
        events: {
            'click .oe_stat_button': 'function_test',
        }
        function_test: function (){
            console.log("test handler")
        });

    });
    core.form_widget_registry.add('barcode_handler_unfocus', BarcodeHandlerUnfocus);
    return BarcodeHandlerUnfocus;*/
});
