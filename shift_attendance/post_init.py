# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

OLD_MODULE_NAME = "beesdoo_shift_attendance"
NEW_MODULE_NAME = "shift_attendance"

PARAMS_TO_RENAME = {
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


def post_init(cr, registry):
    cr.execute(
        "SELECT id FROM ir_module_module "
        "WHERE name = %s and state IN ('installed', 'to upgrade')",
        (OLD_MODULE_NAME,),
    )
    if not cr.fetchone():
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    for old_key, new_key in PARAMS_TO_RENAME.items():
        try:
            old_value = env["ir.config_parameter"].get_param(old_key)
        except Exception:
            _logger.warning("could not find value for '%s'", old_key)
            continue
        env["ir.config_parameter"].set_param(new_key, old_value)
        # Delete old parameter.
        env["ir.config_parameter"].search([("key", "=", old_key)]).unlink()
