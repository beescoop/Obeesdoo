# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Polln Shift Module",
    "summary": """
    Module with basic customizations for the Polln cooperative.
     """,
    "author": "Patricia Daloze, Thibault Francois, Coop IT Easy SC",
    "category": "Sales",
    "website": "https://github.com/beescoop/Obeesdoo",
    "version": "12.0.2.0.1",
    "depends": [
        "shift",
        "beesdoo_website_shift",
        "contacts",
        "beesdoo_easy_my_coop",
    ],
    "data": [
        # "data/mail_template.xml",
        "views/res_partner.xml",
        "views/shift.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
