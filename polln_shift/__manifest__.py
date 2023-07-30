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
        "cooperator_worker",
        "cooperator_eater",
        "cooperator_info_session",
        "eater_parent_barcode",
        "cooperator_info_session",
        "cooperator",
    ],
    "data": [
        # "data/mail_template.xml",
        "views/res_partner.xml",
        "views/shift.xml",
        "views/product.xml",
        "report/label.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
