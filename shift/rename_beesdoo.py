# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""This module was previously beesdoo_shift before it was moved to the OCA.
beesdoo_shift is presently an empty module that depends on this module. When
this module is installed, it should convert all data from the beesdoo_shift
module to be useable by this module.
"""

import logging

_logger = logging.getLogger(__name__)

MODELS_TO_RENAME = {
    "beesddoo.shift.assign_super_coop": "shift.assign_super_coop",
    "beesddoo.shift.generate_planning": "shift.generate_planning",
    "beesddoo.shift.generate_shift_template.line": "shift.generate_shift_template.line",
    "beesddoo.shift.generate_shift_template": "shift.generate_shift_template",
    "beesdoo.shift.action_mixin": "shift.action_mixin",
    "beesdoo.shift.daynumber": "shift.daynumber",
    "beesdoo.shift.extension": "shift.extension",
    "beesdoo.shift.holiday": "shift.holiday",
    "beesdoo.shift.journal": "shift.journal",
    "beesdoo.shift.planning": "shift.planning",
    "beesdoo.shift.shift": "shift.shift",
    "beesdoo.shift.subscribe": "shift.subscribe",
    "beesdoo.shift.template": "shift.template",
    "beesdoo.shift.temporary_exemption": "shift.temporary_exemption",
    "beesdoo.shift.type": "shift.type",
}
XMLIDS_TO_RENAME = [
    ("beesdoo_shift.beesdoo_shift_daynumber_1_demo", "shift.shift_daynumber_1_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_2_demo", "shift.shift_daynumber_2_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_3_demo", "shift.shift_daynumber_3_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_4_demo", "shift.shift_daynumber_4_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_5_demo", "shift.shift_daynumber_5_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_6_demo", "shift.shift_daynumber_6_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_7_demo", "shift.shift_daynumber_7_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_1_demo", "shift.shift_task_type_1_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_2_demo", "shift.shift_task_type_2_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_3_demo", "shift.shift_task_type_3_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_4_demo", "shift.shift_task_type_4_demo"),
    ("beesdoo_shift.beesdoo_shift_planning_1_demo", "shift.shift_planning_1_demo"),
]
OLD_MODULE_NAME = "beesdoo_shift"
NEW_MODULE_NAME = "shift"


def model_to_table(name):
    return name.replace(".", "_")


def rename_beesdoo(cr):
    cr.execute(
        "SELECT id FROM ir_module_module "
        "WHERE name=%s and state IN ('installed', 'to upgrade')", (OLD_MODULE_NAME,))
    if not cr.fetchone():
        return

    from openupgradelib import openupgrade

    for origin, new in MODELS_TO_RENAME.items():
        table_origin = model_to_table(origin)
        table_new = model_to_table(new)
        if openupgrade.table_exists(cr, table_origin) and not openupgrade.table_exists(
            cr, table_new
        ):
            _logger.info("renaming table {} to {}".format(table_origin, table_new))
            openupgrade.rename_tables(cr, [(table_origin, table_new)])

        _logger.info("renaming model {} to {}".format(origin, new))
        openupgrade.rename_models(cr, [(origin, new)])

    _logger.info("renaming xmlids")
    openupgrade.rename_xmlids(cr, XMLIDS_TO_RENAME)

    _logger.info(
        "transferring ir_model_data from {} to {}".format(
            OLD_MODULE_NAME, NEW_MODULE_NAME
        )
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data SET module = %s
        WHERE module = %s AND name NOT IN
        (SELECT name FROM ir_model_data WHERE module = %s)""",
        (NEW_MODULE_NAME, OLD_MODULE_NAME, NEW_MODULE_NAME),
    )
