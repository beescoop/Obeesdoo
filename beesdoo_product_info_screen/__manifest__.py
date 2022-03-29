# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Information Screen",
    "version": "12.0.0.0.1",
    "category": "Product",
    "summary": "Adds a read-only screen to display product information",
    "author": "Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "license": "AGPL-3",
    "depends": ["beesdoo_product"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rules.xml",
        "views/product.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
