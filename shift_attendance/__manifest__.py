# This module depends on `shift_worker_status`.
# If someone needs this module but has another worker_status rules
# this module can be splitted into a generic part, and a specific part
# that implement the worker_status rules.
{
    "name": "Shift Attendance Sheet",
    "summary": """
        Volunteer Timetable Management""",
    "author": """
        Elouan Le Bars,
        Coop IT Easy SC,
        Odoo Community Association (OCA),
        """,
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "version": "12.0.1.2.0",
    "depends": [
        "eater",
        "member_card",
        "eater_member_card",
        "shift",
        "shift_worker_status",
        "mail",
        "barcodes",
    ],
    "data": [
        "data/system_parameter.xml",
        "data/cron.xml",
        "data/mail_template.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "wizard/validate_attendance_sheet.xml",
        "wizard/generate_missing_attendance_sheets.xml",
        "views/attendance_sheet.xml",
    ],
    "demo": [
        "demo/users.xml",
        "demo/workers.xml",
    ],
    "license": "AGPL-3",
    "pre_init_hook": "rename_beesdoo",
    "post_init_hook": "post_init",
}
