# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Augustin Borsu
#   - Elise Dupont
#   - Thibault François
#   - Jean-Marc François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Beesdoo Inventory",
    "summary": "Emptied.\nleftover: Restrict selectable products to those"
    " sold as main supplier by the picking partner.",
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Inventory",
    "version": "12.0.3.1.0",
    "depends": [
        "stock",
        "product_main_supplier",
        "stock_picking_responsible",
        "stock_move_line_auto_fill",
        "stock_picking_product_link",
    ],
    "data": ["views/stock.xml"],
    "installable": True,
    "license": "AGPL-3",
}
