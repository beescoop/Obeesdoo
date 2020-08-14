from openupgradelib import openupgrade


xmlid_renames = [
    # data/cron.xml
    ('beesdoo_shift.ir_cron_check_non_validated_sheet',
     'beesdoo_shift_attendance.ir_cron_check_non_validated_sheet'),
    # data/email_template.xml
    ('beesdoo_shift.email_template_non_validated_sheet',
     'beesdoo_shift_attendance.email_template_non_validated_sheet'),
    ('beesdoo_shift.email_template_non_attendance',
     'beesdoo_shift_attendance.email_template_non_attendance'),
    # data/system_parameter.xml
    ('beesdoo_shift.card_support',
     'beesdoo_shift_attendance.card_support'),
    ('beesdoo_shift.attendance_sheet_generation_interval',
     'beesdoo_shift_attendance.attendance_sheet_generation_interval'),
    # security/group.xml
    ('beesdoo_shift.group_shift_attendance_sheet',
     'beesdoo_shift_attendance.group_shift_attendance_sheet'),
    ('beesdoo_shift.group_shift_attendance_sheet_validation',
     'beesdoo_shift_attendance.group_shift_attendance_sheet_validation'),
]


_config_param_renames = [
    ('beesdoo_shift.default_task_type_id',
     'beesdoo_shift_attendance.pre_filled_task_type_id'),
]


def rename_config_parameters(cr, keys_spec):
    for (old, new) in keys_spec:
        query = ("UPDATE ir_config_parameter SET key = %s "
                 "WHERE key = %s")
        openupgrade.logged_query(cr, query, (new, old))


def fix_shift_status(cr):
    """
    The 'draft' status for the shift (a task) does not exist in 12.0. So
    shift in this state will be moved to the 'cancel' state.
    """
    query = (
        "UPDATE beesdoo_shift_shift SET state = 'cancel' "
        "WHERE state = 'draft'"
    )
    openupgrade.logged_query(cr, query)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlid_renames)
    rename_config_parameters(cr, _config_param_renames)
    fix_shift_status(cr)
