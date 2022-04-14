odoo.define("beesdoo_website_shift_swap.shift_table", function (require) {
    "use strict";
    $(document).ready(function () {
        // Documentation: https://datatables.net/, https://momentjs.com/
        $.fn.dataTable.moment("dddd DD MMM, YYYY");
        $(".interactive").DataTable({
            columnDefs: [{orderable: false, targets: "non_orderable"}],
        });
    });
});
