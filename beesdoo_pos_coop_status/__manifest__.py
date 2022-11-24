# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "BEES coop Point of sale - Cooperator Status",
    "summary": """Emptied.""",
    "author": "Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Point Of Sale",
    "version": "12.0.2.0.0",
    "depends": ["beesdoo_pos", "beesdoo_shift", "pos_shift_partner_can_shop"],
    "qweb": ["static/src/xml/pos.xml"],
    "data": ["views/assets.xml"],
    "installable": True,
    "license": "AGPL-3",
}
