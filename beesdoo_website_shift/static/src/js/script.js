odoo.define("beesdoo_website_shift.script", function (require) {
    "use strict";
    $(document).ready(function () {
        $("#collapseHelp").on("hidden.bs.collapse", function () {
            $("#toggle_help_button").text("Show");
        });

        $("#collapseHelp").on("shown.bs.collapse", function () {
            $("#toggle_help_button").text("Hide");
        });

        $(".multi-collapse").on("hidden.bs.collapse", function () {
            $("#toggle_shifts_button").text("Show next shifts");
        });

        $(".multi-collapse").on("shown.bs.collapse", function () {
            $("#toggle_shifts_button").text("Reduce");
        });
    });
});
