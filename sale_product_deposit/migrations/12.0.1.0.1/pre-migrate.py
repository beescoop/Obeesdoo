from openupgradelib import openupgrade

renamed_xml_ids = (
    (
        "beesdoo_product_label.consignes_group_tax",
        "sale_product_deposit.deposit_tax_group",
    ),
)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, renamed_xml_ids)
