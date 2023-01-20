# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""This module was previously beesdoo_shift before it was moved to the OCA.
beesdoo_shift is presently an empty module that depends on this module. When
this module is installed, it should convert all data from the beesdoo_shift
module to be useable by this module.
"""

import logging

_logger = logging.getLogger(__name__)

MODELS_TO_RENAME = [
    ("beesddoo.shift.assign_super_coop", "shift.assign_super_coop"),
    ("beesddoo.shift.generate_planning", "shift.generate_planning"),
    (
        "beesddoo.shift.generate_shift_template.line",
        "shift.generate_shift_template.line",
    ),
    ("beesddoo.shift.generate_shift_template", "shift.generate_shift_template"),
    ("beesdoo.shift.action_mixin", "shift.action_mixin"),
    ("beesdoo.shift.daynumber", "shift.daynumber"),
    ("beesdoo.shift.extension", "shift.extension"),
    ("beesdoo.shift.holiday", "shift.holiday"),
    ("beesdoo.shift.journal", "shift.journal"),
    ("beesdoo.shift.planning", "shift.planning"),
    ("beesdoo.shift.shift", "shift.shift"),
    ("beesdoo.shift.subscribe", "shift.subscribe"),
    ("beesdoo.shift.template", "shift.template"),
    ("beesdoo.shift.temporary_exemption", "shift.temporary_exemption"),
    ("beesdoo.shift.type", "shift.type"),
]
# not generated dynamically from MODELS_TO_RENAME for 2 reasons:
# 1. beesdoo.shift.action_mixin has no table (because it's a mixin).
# 2. many2many tables must be added anyway.
TABLES_TO_RENAME = [
    ("beesddoo_shift_assign_super_coop", "shift_assign_super_coop"),
    ("beesddoo_shift_generate_planning", "shift_generate_planning"),
    (
        "beesddoo_shift_generate_shift_template_line",
        "shift_generate_shift_template_line",
    ),
    ("beesddoo_shift_generate_shift_template", "shift_generate_shift_template"),
    ("beesdoo_shift_daynumber", "shift_daynumber"),
    ("beesdoo_shift_extension", "shift_extension"),
    ("beesdoo_shift_holiday", "shift_holiday"),
    ("beesdoo_shift_journal", "shift_journal"),
    ("beesdoo_shift_planning", "shift_planning"),
    ("beesdoo_shift_shift", "shift_shift"),
    ("beesdoo_shift_subscribe", "shift_subscribe"),
    ("beesdoo_shift_template", "shift_template"),
    ("beesdoo_shift_temporary_exemption", "shift_temporary_exemption"),
    ("beesdoo_shift_type", "shift_type"),
    # many2many tables
    (
        "beesddoo_shift_assign_super_coop_beesdoo_shift_shift_rel",
        "shift_assign_super_coop_shift_shift_rel",
    ),
    (
        "beesdoo_shift_template_res_partner_rel",
        "res_partner_shift_template_rel",
    ),
    (
        "beesdoo_shift_journal_cooperative_status_rel",
        "cooperative_status_shift_journal_rel",
    ),
]
COLUMNS_TO_RENAME = {
    "shift_assign_super_coop_shift_shift_rel": [
        ("beesddoo_shift_assign_super_coop_id", "shift_assign_super_coop_id"),
        ("beesdoo_shift_shift_id", "shift_shift_id"),
    ],
    "res_partner_shift_template_rel": [
        ("beesdoo_shift_template_id", "shift_template_id")
    ],
    "cooperative_status_shift_journal_rel": [
        ("beesdoo_shift_journal_id", "shift_journal_id")
    ],
}
# constraints and indexes are normally correctly renamed by the openupgrade
# functions, but these fail for identifiers that have been truncated to the
# maximum length (63 characters). they are thus manually renamed here. note
# that these are cosmetic changes, not doing them would not prevent the module
# from working correctly.
CONSTRAINTS_TO_RENAME = {
    "cooperative_status_shift_journal_rel": [
        (
            "beesdoo_shift_journal_coopera_beesdoo_shift_journal_id_coop_key",
            "cooperative_status_shift_jour_shift_journal_id_cooperative__key",
        ),
        (
            "beesdoo_shift_journal_cooperative_beesdoo_shift_journal_id_fkey",
            "cooperative_status_shift_journal_rel_shift_journal_id_fkey",
        ),
        (
            "beesdoo_shift_journal_cooperative_st_cooperative_status_id_fkey",
            "cooperative_status_shift_journal_rel_cooperative_status_id_fkey",
        ),
    ],
    "res_partner_shift_template_rel": [
        (
            "beesdoo_shift_template_res_pa_beesdoo_shift_template_id_res_key",
            "res_partner_shift_template_re_shift_template_id_res_partner_key",
        ),
        (
            "beesdoo_shift_template_res_partn_beesdoo_shift_template_id_fkey",
            "res_partner_shift_template_rel_shift_template_id_fkey",
        ),
    ],
    "shift_assign_super_coop_shift_shift_rel": [
        (
            "beesddoo_shift_assign_super_c_beesddoo_shift_assign_super_c_key",
            "shift_assign_super_coop_shift_shift_assign_super_coop_id_sh_key",
        ),
        (
            "beesddoo_shift_assign_super_c_beesddoo_shift_assign_super__fkey",
            "shift_assign_super_coop_shift_s_shift_assign_super_coop_id_fkey",
        ),
        (
            "beesddoo_shift_assign_super_coop_be_beesdoo_shift_shift_id_fkey",
            "shift_assign_super_coop_shift_shift_rel_shift_shift_id_fkey",
        ),
    ],
    "shift_temporary_exemption": [
        (
            "beesdoo_shift_temporary_exempti_temporary_exempt_reason_id_fkey",
            "shift_temporary_exemption_temporary_exempt_reason_id_fkey",
        ),
    ],
}
INDEXES_TO_RENAME = [
    (
        "beesddoo_shift_assign_super_c_beesddoo_shift_assign_super_c_idx",
        "shift_assign_super_coop_shift_sh_shift_assign_super_coop_id_idx",
    ),
    (
        "beesddoo_shift_assign_super_coop_bee_beesdoo_shift_shift_id_idx",
        "shift_assign_super_coop_shift_shift_rel_shift_shift_id_idx",
    ),
    (
        "beesdoo_shift_journal_cooperative__beesdoo_shift_journal_id_idx",
        "cooperative_status_shift_journal_rel_shift_journal_id_idx",
    ),
    (
        "beesdoo_shift_journal_cooperative_sta_cooperative_status_id_idx",
        "cooperative_status_shift_journal_rel_cooperative_status_id_idx",
    ),
    (
        "beesdoo_shift_template_res_partne_beesdoo_shift_template_id_idx",
        "res_partner_shift_template_rel_shift_template_id_idx",
    ),
]
XMLIDS_TO_RENAME = [
    ("beesdoo_shift.beesdoo_shift_daynumber_1_demo", "shift.shift_daynumber_1_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_2_demo", "shift.shift_daynumber_2_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_3_demo", "shift.shift_daynumber_3_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_4_demo", "shift.shift_daynumber_4_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_5_demo", "shift.shift_daynumber_5_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_6_demo", "shift.shift_daynumber_6_demo"),
    ("beesdoo_shift.beesdoo_shift_daynumber_7_demo", "shift.shift_daynumber_7_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_1_demo", "shift.shift_task_type_1_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_2_demo", "shift.shift_task_type_2_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_3_demo", "shift.shift_task_type_3_demo"),
    ("beesdoo_shift.beesdoo_shift_task_type_4_demo", "shift.shift_task_type_4_demo"),
    ("beesdoo_shift.beesdoo_shift_planning_1_demo", "shift.shift_planning_1_demo"),
]
OLD_MODULE_NAME = "beesdoo_shift"
NEW_MODULE_NAME = "shift"


def rename_beesdoo(cr):
    cr.execute(
        "SELECT id FROM ir_module_module "
        "WHERE name = %s and state IN ('installed', 'to upgrade')",
        (OLD_MODULE_NAME,),
    )
    if not cr.fetchone():
        return

    from openupgradelib import openupgrade

    _logger.info("renaming models")
    openupgrade.rename_models(cr, MODELS_TO_RENAME)
    _logger.info("renaming tables")
    openupgrade.rename_tables(cr, TABLES_TO_RENAME)
    _logger.info("renaming columns")
    openupgrade.rename_columns(cr, COLUMNS_TO_RENAME)
    _logger.info("renaming constraints")
    for table_name, constraints in CONSTRAINTS_TO_RENAME.items():
        for old_name, new_name in constraints:
            openupgrade.logged_query(
                cr,
                "alter table {} rename constraint {} to {}".format(
                    table_name, old_name, new_name
                ),
            )
    _logger.info("renaming indexes")
    for old_name, new_name in INDEXES_TO_RENAME:
        openupgrade.logged_query(
            cr, "alter index {} rename to {}".format(old_name, new_name)
        )
    _logger.info("renaming xmlids")
    openupgrade.rename_xmlids(cr, XMLIDS_TO_RENAME)

    _logger.info(
        "transferring ir_model_data from {} to {}".format(
            OLD_MODULE_NAME, NEW_MODULE_NAME
        )
    )
    # this query comes from openupgrade.update_module_names(), which cannot be
    # used directly here because the module with the old name still exists.
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data SET module = %s
        WHERE module = %s AND name NOT IN
        (SELECT name FROM ir_model_data WHERE module = %s)""",
        (NEW_MODULE_NAME, OLD_MODULE_NAME, NEW_MODULE_NAME),
    )
