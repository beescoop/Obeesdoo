from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api


def rename_xml_ids(cr):
    renamed_view_xml_ids = (
        (
            "beesdoo_base.beesdoo_partner_form_view",
            "member_card.res_partner_view_form",
        ),
        (
            "beesdoo_base.view_beesdoo_res_partner_filter",
            "member_card.res_partner_view_filter",
        ),
        (
            "beesdoo_base.MemberCard Wizard",
            "member_card.membercard_new_wizard_view_form",
        ),
        (
            "beesdoo_base.printing_membercard_request_wizard",
            "member_card.membercard_requestprinting_wizard_view_form",
        ),
        (
            "beesdoo_base.membercard_set_as_printed_wizard",
            "member_card.membercard_set_as_printed_wizard_view_form",
        ),
        (
            "beesdoo_base.action_membercard_wizard",
            "member_card.membercard_wizard_action",
        ),
        (
            "beesdoo_base.report_beescard_cm",
            "member_card.membercard_report_action",
        ),
        (
            "beesdoo_base.beesdoo_base_action_request_membercard_printing",
            "member_card.member_card_requestprinting_wizard_action",
        ),
        (
            "beesdoo_base.beesdoo_base_action_set_membercard_as_printed",
            "member_card.member_card_set_as_printed_wizard_action",
        ),
    )

    env = api.Environment(cr, SUPERUSER_ID, {})
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)
