import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.2.0.0")


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

modules_to_install = [
    "sale_suggested_price",
    "product_main_suplier",
]


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming view xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)

    for module in modules_to_install:
        module_ids = env["ir.module.module"].search(
            [("name", "=", module), ("state", "=", "uninstalled")]
        )
        if module_ids:
            module_ids.button_install()
