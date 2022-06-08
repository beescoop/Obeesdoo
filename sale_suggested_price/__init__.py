from . import models
from . import wizard

from odoo import api, SUPERUSER_ID
from openupgradelib import openupgrade


renamed_view_xml_ids = (
    (
        "beesdoo_product.beesdoo_product_category_form",
        "sale_suggested_price.product_category_form_view",
    ),
    (
        "beesdoo_product.product_template_edit_price_tree_view",
        "sale_suggested_price.product_template_edit_price_tree_view",
    ),
    (
        "beesdoo_product.beesdoo_product_category_list",
        "sale_suggested_price.product_category_list_view",
    ),
    (
        "beesdoo_product.beesdoo_product_supplierinfo_tree_view",
        "sale_suggested_price.product_supplierinfo_tree_view",
    ),
    (
        "beesdoo_product.product_template_edit_price_tree_view",
        "sale_suggested_price.product_template_edit_price_tree_view",
    ),
    (
        "beesdoo_product.beesdoo_product_res_parter_form",
        "sale_suggested_price.view_partner_form",
    ),
    (
        "beesdoo_product.res_config_settings_view_form",
        "sale_suggested_price.res_config_settings_view_form",
    ),
)


def rename_xml_ids(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)
