from . import models
from . import wizard

from odoo import api, SUPERUSER_ID
from openupgradelib import openupgrade


renamed_view_xml_ids = (
    (
        "beesdoo_product.purchase_product_edit_price",
        "sale_adapt_price_wizard.purchase_product_edit_price",
    ),
    (
        "beesdoo_product.menu_purchase_edit_price",
        "sale_adapt_price_wizard.menu_purchase_edit_price",
    ),
    (
        "beesdoo_product.sale_product_edit_price",
        "sale_adapt_price_wizard.sale_product_edit_price",
    ),
    (
        "beesdoo_product.menu_sale_edit_price",
        "sale_adapt_price_wizard.menu_sale_edit_price",
    ),
    (
        "beesdoo_product.purchase_product_edit_price",
        "sale_adapt_price_wizard.purchase_product_edit_price",
    ),
    (
        "beesdoo_product.purchase_product_edit_price",
        "sale_adapt_price_wizard.purchase_product_edit_price",
    ),
    (
        "beesdoo_product.product_template_edit_price_tree_view",
        "sale_adapt_price_wizard.product_template_edit_price_tree_view",
    ),
    (
        "beesdoo_product.adapt_sales_price_wizard",
        "sale_adapt_price_wizard.adapt_sales_price_wizard",
    ),
)


def rename_xml_ids(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)
