# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "Beescoop Point of sale - Cooperator Status",
    "summary": """POS Support for cooperator status.""",
    "author": "Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Point Of Sale",
    "version": "12.0.1.0.0",
    "depends": ["beesdoo_pos", "beesdoo_shift"],
    "qweb": ["static/src/xml/pos.xml"],
    "data": ["views/assets.xml"],
    "installable": True,
    "license": "AGPL-3",
}
