# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""This module was previously beesdoo_worker_status before it was moved to the OCA.
beesdoo_worker_status is presently an empty module that depends on this module. When
this module is installed, it should convert all data from the beesdoo_worker_status
module to be useable by this module.
"""

import logging

_logger = logging.getLogger(__name__)

MODELS_TO_RENAME = {}
XMLIDS_TO_RENAME = [
    (
        "beesdoo_worker_status.beesdoo_shift_task_template_1_demo",
        "shift.shift_task_template_1_demo",
    ),
    (
        "beesdoo_worker_status.beesdoo_shift_task_template_2_demo",
        "shift.shift_task_template_2_demo",
    ),
    (
        "beesdoo_worker_status.beesdoo_shift_task_template_3_demo",
        "shift.shift_task_template_3_demo",
    ),
]
PARAMETER_KEYS_TO_RENAME = {
    "beesdoo_worker_status.irregular_penalty": (
        "shift_worker_status.irregular_penalty"
    ),
}
OLD_MODULE_NAME = "beesdoo_worker_status"
NEW_MODULE_NAME = "shift_worker_status"


def model_to_table(name):
    return name.replace(".", "_")


def rename_beesdoo(cr):
    cr.execute(
        "SELECT id FROM ir_module_module "
        "WHERE name=%s and state IN ('installed', 'to upgrade')",
        (OLD_MODULE_NAME,),
    )
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
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data SET module = %s
        WHERE module = %s AND name NOT IN
        (SELECT name FROM ir_model_data WHERE module = %s)""",
        (NEW_MODULE_NAME, OLD_MODULE_NAME, NEW_MODULE_NAME),
    )
