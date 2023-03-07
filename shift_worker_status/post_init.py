# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

OLD_MODULE_NAME = "beesdoo_worker_status"
NEW_MODULE_NAME = "shift_worker_status"

PARAMS_TO_RENAME = {
    "beesdoo_worker_status.irregular_penalty": "shift_worker_status.irregular_penalty",
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
