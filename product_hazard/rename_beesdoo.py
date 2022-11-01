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
    "beesdoo.product.hazard": "product.hazard",
}

XMLIDS_TO_RENAME = [
    ("beesdoo_product.fds_required", "product_hazard.fds_required"),
    ("beesdoo_product.fds_not_required", "product_hazard.fds_not_required"),
    ("beesdoo_product.fds_present", "product_hazard.fds_present"),
    ("beesdoo_product.hazard_none", "product_hazard.hazard_none"),
    ("beesdoo_product.hazard_acid", "product_hazard.hazard_acid"),
    ("beesdoo_product.hazard_base", "product_hazard.hazard_base"),
    ("beesdoo_product.hazard_other", "product_hazard.hazard_other"),
]
OLD_MODULE_NAME = "beesdoo_product"
NEW_MODULE_NAME = "beesdoo_product_label"


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
        UPDATE ir_model_data SET module = 'product_hazard'
        WHERE module = 'beesdoo_product' AND
        name LIKE 'model_product_hazard%'""",
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data SET module = 'product_hazard'
        WHERE module = 'beesdoo_product' AND
        name LIKE 'field_product_hazard%'""",
    )
