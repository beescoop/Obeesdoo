# Copyright 2017-2020 Coop IT Easy SC (http://coopiteasy.be)
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shift Portal",
    "summary": """
        Show available shifts for regular and irregular workers on the
        website and let workers manage their shifts with an
        easy web interface.
    """,
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "depends": ["portal", "website", "shift"],
    "assets": {
        "web.assets_backend": ["shift_portal/static/src/js/script.js"],
    },
    "data": [
        "data/res_config_data.xml",
        "views/shift_website_templates.xml",
        "views/my_shift_website_templates.xml",
        "views/res_config_views.xml",
    ],
}
