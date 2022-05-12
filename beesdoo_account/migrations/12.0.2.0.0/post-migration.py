import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.2.0.0")

renamed_group_xml_ids = (
    (
        "beesdoo_account.group_validate_invoice_negative_total_amount",
        "account_invoice_negative_total.group_validate_invoice_negative_total_amount",
    ),
)


renamed_view_xml_ids = (
    (
        "beesdoo_account.res_config_settings_view_form",
        "account_invoice_negative_total.res_config_settings_view_form",
    ),
    (
        "beesdoo_account.account_invoice_form_view",
        "account_invoice_date_required.account_invoice_form_view",
    ),
    (
        "beesdoo_account.account_invoice_form_view",
        "account_invoice_date_required.account_invoice_form_view",
    ),
)

modules_to_install = ["account_invoice_negative_total", "account_invoice_date_required"]


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming view xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)

    _logger.info("renaming group xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_group_xml_ids)

    for module in modules_to_install:
        module_ids = env["ir.module.module"].search(
            [("name", "=", module), ("state", "=", "uninstalled")]
        )
        if module_ids:
            module_ids.button_install()
