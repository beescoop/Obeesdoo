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
)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming view xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)

    _logger.info("renaming group xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_group_xml_ids)

    module_ids = env["ir.module.module"].search(
        [("name", "=", "account_invoice_negative_total"), ("state", "=", "uninstalled")]
    )
    if module_ids:
        module_ids.button_install()
