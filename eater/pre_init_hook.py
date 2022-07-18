from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


def rename_xml_ids(cr):

    renamed_view_xml_ids = (
        (
            "beesdoo_base.action_eater_wizard",
            "eater.eater_new_wizard_action",
        ),
        (
            "beesdoo_base.Eater Wizard",
            "eater.new_eater_wizard_action",
        ),
        (
            "beesdoo_base.beesdoo_partner_form_view",
            "eater.res_partner_form_view",
        ),
    )
    env = api.Environment(cr, SUPERUSER_ID, {})
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)
