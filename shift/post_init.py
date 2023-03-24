# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

OLD_MODULE_NAME = "beesdoo_shift"
NEW_MODULE_NAME = "shift"

PARAMS_TO_RENAME = {
    "alert_delay": "shift.alert_delay",
    "default_grace_delay": "shift.default_grace_delay",
    "default_extension_delay": "shift.default_extension_delay",
    "always_update": "shift.always_update",
    "last_planning_seq": "shift.last_planning_seq",
    "next_planning_date": "shift.next_planning_date",
    "irregular_unsubscribe": "shift.irregular_unsubscribe",
    "regular_counter_to_unsubscribe": "shift.regular_counter_to_unsubscribe",
    "min_percentage_presence": "shift.min_percentage_presence",
    "regular_next_shift_limit": "shift.regular_next_shift_limit",
    "min_hours_to_unsubscribe": "shift.min_hours_to_unsubscribe",
    "max_shift_per_day": "shift.max_shift_per_day",
    "max_shift_per_month": "shift.max_shift_per_month",
    "shift_period": "shift.shift_period",
}


def post_init(cr, registry):
    cr.execute(
        "SELECT id FROM ir_module_module "
        "WHERE name = %s and state IN ('installed', 'to upgrade')",
        (OLD_MODULE_NAME,),
    )
    if not cr.fetchone():
        return

    # After shift is installed, a lot of parameters (with prefix 'shift.') are
    # created fresh. If we didn't rename the keys of the parameters (e.g.
    # 'alert_delay' was never renamed to 'shift.alert_delay'), the values of
    # those parameters would be reset to the default values at init time (i.e.
    # after the init hook).
    #
    # Furthermore, the XMLIDs of all parameters have been changed. If they
    # stayed the same, the parameters would be overridden at init time as well,
    # even though the names of the keys have changed.
    #
    # The idea here is to take the old parameters that haven't yet been pruned,
    # put their values in the newly created parameters, then prune the old
    # parameters.
    env = api.Environment(cr, SUPERUSER_ID, {})
    for old_key, new_key in PARAMS_TO_RENAME.items():
        old_param = env["ir.config_parameter"].search([("key", "=", old_key)])
        if old_param:
            _logger.info("renaming %s to %s", old_key, new_key)
            env["ir.config_parameter"].set_param(new_key, old_param.value)
            old_param.unlink()
