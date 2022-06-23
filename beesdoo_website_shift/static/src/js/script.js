odoo.define("beesdoo_website_shift.script", function (require) {
    "use strict";
    $(document).ready(function () {
        // Hide help panel by default for small screens
        if ($(window).width() < 992) {
            $("#collapseHelp").removeClass("show");
        }

        // Change help button if help is hidden
        if (!$("#collapseHelp").hasClass("show")) {
            $("#toggle_help_button").text("Show");
        }

        // Toggle help panel
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
