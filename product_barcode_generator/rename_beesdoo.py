# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""This module was previously part of beesdoo_product before it was moved to the
OCA. beesdoo_product is presently an empty module that depends on this module.
When this module is installed, it should convert data from the beesdoo_product
module to be useable by this module.
"""

import logging

_logger = logging.getLogger(__name__)

MODELS_TO_RENAME = {}

XMLIDS_TO_RENAME = [
    (
        "beesdoo_product.seq_ean_product_internal_ref",
        "product_barcode_generator.seq_ean_product_internal_ref",
    ),
    (
        "beesdoo_product.beesdoo_product_barcode_rule",
        "product_barcode_generator.product_barcode_generator_rule",
    ),
]
OLD_MODULE_NAME = "beesdoo_product"
NEW_MODULE_NAME = "product_barcode_generator"


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
    # openupgrade.delete_records_safely_by_xml_id(env, xml_ids,
