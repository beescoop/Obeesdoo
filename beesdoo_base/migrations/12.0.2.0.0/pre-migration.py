import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__ + " 12.0.2.0.0")


renamed_view_xml_ids = (
    (
        "beesdoo_base.beesdoo_partner_form_view",
        "member_card.beesdoo_partner_form_view",
    ),
    (
        "beesdoo_base.view_beesdoo_res_partner_filter",
        "member_card.view_beesdoo_res_partner_filter",
    ),
    (
        "beesdoo_base.MemberCard Wizard",
        "member_card.MemberCard Wizard",
    ),
    (
        "beesdoo_base.printing_membercard_request_wizard",
        "member_card.printing_membercard_request_wizard",
    ),
    (
        "beesdoo_base.membercard_set_as_printed_wizard",
        "member_card.membercard_set_as_printed_wizard",
    ),
    (
        "beesdoo_base.action_membercard_wizard",
        "member_card.action_membercard_wizard",
    ),
    (
        "beesdoo_base.report_beescard_cm",
        "member_card.report_beescard_cm",
    ),
    (
        "beesdoo_base.beesdoo_base_action_request_membercard_printing",
        "member_card.beesdoo_base_action_request_membercard_printing",
    ),
    (
        "beesdoo_base.beesdoo_base_action_set_membercard_as_printed",
        "member_card.beesdoo_base_action_set_membercard_as_printed",
    ),
    (
        "beesdoo_base.action_eater_wizard",
        "eater.action_eater_wizard",
    ),
    (
        "beesdoo_base.Eater Wizard",
        "eater.Eater Wizard",
    ),
)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("renaming view xml ids")
    openupgrade.rename_xmlids(env.cr, renamed_view_xml_ids)
