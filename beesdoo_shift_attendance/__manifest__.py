# This module is, for now, specific to the BEES coop.
# Therefore, this module depends on `beesdoo_worker_status`.
# If someone needs this module but has another worker_status rules
# this module can be splitted into a generic part, and a specific part
# that implement the worker_status rules.
{
    "name": "BEES coop Shift Attendance Sheet",
    "summary": """
        Volonteer Timetable Management
        Attendance Sheet for BEES coop""",
    "author": "Elouan Le Bars, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "version": "12.0.1.2.0",
    "depends": [
        "eater",
        "member_card",
        "eater_member_card",
        "beesdoo_shift",
        "beesdoo_worker_status",
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
}
