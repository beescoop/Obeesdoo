# -*- coding: utf-8 -*-
{
    'name': "Beescoop Shift Management",

    'summary': """
        Volonteer Timetable Management""",

    'description': """

    """,

    'author': "Thibault Francois",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Coop',
    'version': '0.1',

    'depends': ['beesdoo_base'],

    'data': [
        "security/ir.model.access.csv",
        "views/task_template.xml",
        "views/task.xml",
        "views/planning.xml",
        "wizard/instanciate_planning.xml",
        "wizard/batch_template.xml",
    ],
}
