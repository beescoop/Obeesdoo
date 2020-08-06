# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Macavrac Base Module",
    "summary": """
    Module with basic customizations for the Macavrac cooperative.
     """,
    "author": "Patricia Daloze, Coop IT Easy SCRLfs",
    "category": "Sales",
    "version": "12.0.1.0.0",
    "depends": ["beesdoo_shift", "beesdoo_website_shift", "contacts"],
    "data": [
        "data/mail_template.xml",
        "views/res_partner.xml",
        "views/shift.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
