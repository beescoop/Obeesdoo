odoo.define("beesdoo_website_shift.script", function (require) {
    "use strict";
    $(document).ready(function () {
        // Hide help panel by default for small screens
        if ($(window).width() < 992) {
            $("#collapseHelp").removeClass("show");
        }

        // Translatable terms
        var core = require("web.core");
        var _t = core._t;

        // Change help button if help is hidden
        if (!$("#collapseHelp").hasClass("show")) {
            $("#toggle_help_button").text(_t("Show"));
        }

        // Toggle help panel
        $("#collapseHelp").on("hidden.bs.collapse", function () {
            $("#toggle_help_button").text(_t("Show"));
        });

        $("#collapseHelp").on("shown.bs.collapse", function () {
            $("#toggle_help_button").text(_t("Hide"));
        });

        $(".multi-collapse").on("hidden.bs.collapse", function () {
            $("#toggle_shifts_button").text(_t("Show next shifts"));
        });

        $(".multi-collapse").on("shown.bs.collapse", function () {
            $("#toggle_shifts_button").text(_t("Reduce"));
        });

        // Move modals to body to avoid unwanted behaviour due to parent elements position
        $(".modal").appendTo("body");
    });
});
