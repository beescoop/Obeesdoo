# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "POS - Can Partner Shop",
    "summary": """Display in the POS whether the partner can shop or not.""",
    "author": "Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Point Of Sale",
    "version": "12.0.2.0.2",
    "depends": ["point_of_sale", "shift"],
    "qweb": ["static/src/xml/pos.xml"],
    "data": ["views/assets.xml"],
    "installable": True,
    "license": "AGPL-3",
}
