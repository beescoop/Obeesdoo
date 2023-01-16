# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""This module was previously beesdoo_shift_attendance before it was moved to the OCA.
beesdoo_shift_attendance is presently an empty module that depends on this module. When
this module is installed, it should convert all data from the beesdoo_shift_attendance
module to be useable by this module.
"""

import logging

_logger = logging.getLogger(__name__)

MODELS_TO_RENAME = [
    ("beesdoo.shift.sheet", "shift.sheet"),
    ("beesdoo.shift.sheet.added", "shift.sheet.added"),
    ("beesdoo.shift.sheet.expected", "shift.sheet.expected"),
    ("beesdoo.shift.sheet.shift", "shift.sheet.shift"),
    ("beesdoo.shift.sheet.validate", "shift.sheet.validate"),
    (
        "beesdoo.shift.generate_missing_attendance_sheets",
        "shift.generate_missing_attendance_sheets",
    ),
]
CONSTRAINTS_TO_RENAME = {
    "shift_generate_missing_attendance_sheets": [
        (
            "beesdoo_shift_generate_missing_attendance_sheet_create_uid_fkey",
            "shift_generate_missing_attendance_sheets_create_uid_fkey",
        ),
    ],
}
XMLIDS_TO_RENAME = [
    (
        "beesdoo_shift_attendance.beesdoo_shift_partner_1_demo",
        "shift_attendance.shift_partner_1_demo",
    ),
    (
        "beesdoo_shift_attendance.beesdoo_shift_partner_2_demo",
        "shift_attendance.shift_partner_2_demo",
    ),
    (
        "beesdoo_shift_attendance.beesdoo_shift_user_1_demo",
        "shift_attendance.shift_user_1_demo",
    ),
    (
        "beesdoo_shift_attendance.beesdoo_shift_user_1_demo_res_partner",
        "shift_attendance.shift_user_1_demo_res_partner",
    ),
    (
        "beesdoo_shift_attendance.beesdoo_shift_user_2_demo",
        "shift_attendance.shift_user_2_demo",
    ),
    (
        "beesdoo_shift_attendance.beesdoo_shift_user_2_demo_res_partner",
        "shift_attendance.shift_user_2_demo_res_partner",
    ),
]
PARAMETER_KEYS_TO_RENAME = {
    "beesdoo_shift_attendance.card_support": "shift_attendance.card_support",
    "beesdoo_shift_attendance.pre_filled_task_type_id": (
        "shift_attendance.pre_filled_task_type_id"
    ),
    "beesdoo_shift_attendance.attendance_sheet_generation_interval": (
        "shift_attendance.attendance_sheet_generation_interval"
    ),
    "beesdoo_shift_attendance.attendance_sheet_default_shift_state": (
        "shift_attendance.attendance_sheet_default_shift_state"
    ),
}
OLD_MODULE_NAME = "beesdoo_shift_attendance"
NEW_MODULE_NAME = "shift_attendance"


def model_to_table(name):
    return name.replace(".", "_")


def rename_beesdoo(cr):
    cr.execute(
        "SELECT id FROM ir_module_module "
        "WHERE name = %s and state IN ('installed', 'to upgrade')",
        (OLD_MODULE_NAME,),
    )
    if not cr.fetchone():
        return

    from openupgradelib import openupgrade

    _logger.info("renaming models")
    openupgrade.rename_models(cr, MODELS_TO_RENAME)
    tables_to_rename = [
        (model_to_table(old_name), model_to_table(new_name))
        for old_name, new_name in MODELS_TO_RENAME
    ]
    _logger.info("renaming tables")
    openupgrade.rename_tables(cr, tables_to_rename)
    for table_name, constraints in CONSTRAINTS_TO_RENAME.items():
        for old_name, new_name in constraints:
            openupgrade.logged_query(
                cr,
                "alter table {} rename constraint {} to {}".format(
                    table_name, old_name, new_name
                ),
            )

    for origin, new in PARAMETER_KEYS_TO_RENAME.items():
        _logger.info("renaming key {} to {}".format(origin, new))
        openupgrade.logged_query(
            cr,
            """
            UPDATE ir_config_parameter SET key = %s
            WHERE key = %s""",
            (new, origin),
        )

    _logger.info("renaming xmlids")
    openupgrade.rename_xmlids(cr, XMLIDS_TO_RENAME)

    _logger.info(
        "transferring ir_model_data from {} to {}".format(
            OLD_MODULE_NAME, NEW_MODULE_NAME
        )
    )
    # this query comes from openupgrade.update_module_names(), which cannot be
    # used directly here because the module with the old name still exists.
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data SET module = %s
        WHERE module = %s AND name NOT IN
        (SELECT name FROM ir_model_data WHERE module = %s)""",
        (NEW_MODULE_NAME, OLD_MODULE_NAME, NEW_MODULE_NAME),
    )
