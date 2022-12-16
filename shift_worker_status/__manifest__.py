# Copyright 2020 Coop IT Easy SCRL fs
#   Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "BEES coop Worker Status manager",
    "summary": """
        Worker status management specific to beescoop.""",
    "author": "Thibault Francois, Elouan Le Bars, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "version": "12.0.1.1.0",
    "depends": ["beesdoo_shift"],
    "data": [
        "data/beesdoo_worker_status_data.xml",
        "views/res_config_settings_view.xml",
    ],
    "demo": ["demo/tasks.xml"],
    "license": "AGPL-3",
}
