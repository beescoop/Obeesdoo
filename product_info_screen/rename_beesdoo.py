# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""This module was previously beesdoo_product_info_screen before it was moved to
the OCA. beesdoo_product_info_screen is presently an empty module that depends
on this module. When this module is installed, it should convert all data from
the beesdoo_product_info_screen module to be useable by this module.
"""

import logging

_logger = logging.getLogger(__name__)

OLD_MODULE_NAME = "beesdoo_product_info_screen"
NEW_MODULE_NAME = "product_info_screen"


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
