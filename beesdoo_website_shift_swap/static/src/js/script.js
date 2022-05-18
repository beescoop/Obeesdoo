odoo.define("beesdoo_website_shift_swap.shift_table", function (require) {
    "use strict";
    $(document).ready(function () {
        // Interactive html tables
        // Documentation: https://datatables.net/, https://momentjs.com/
        $.fn.dataTable.moment("dddd DD MMM, YYYY");
        var table = $(".interactive").DataTable({
            columnDefs: [{orderable: false, targets: "non_orderable"}],
        });
        // Add hidden checkboxes to the form data and add at least one condition
        $("#select_available_shifts_form").on("submit", function (e) {
            if (table.$('input[type="checkbox"]').filter(":checked").length < 1) {
                alert("Please select at least one shift");
                return false;
            }
            var $form = $(this);
            table.$('input[type="checkbox"]').each(function () {
                if (!$.contains(document, this)) {
                    if (this.checked) {
                        $form.append(
                            $("<input>")
                                .attr("type", "hidden")
                                .attr("name", this.name)
                                .val(this.value)
                        );
                    }
                }
            });
        });
        // Popovers
        $('[data-toggle="popover"]').popover();
    });
});
