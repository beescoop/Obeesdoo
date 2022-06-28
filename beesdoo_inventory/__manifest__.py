# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Augustin Borsu
#   - Elise Dupont
#   - Thibault François
#   - Jean-Marc François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Beesdoo Inventory",
    "summary": "Restrict selectable products to those"
    " sold as main supplier by the picking partner.",
    "author": "Beescoop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Inventory",
    "version": "12.0.2.0.1",
    "depends": [
        "stock",
        "beesdoo_product",  # for field main_seller_id
        "stock_picking_responsible",
        "stock_picking_copy_quantity",
    ],
    "data": ["views/stock.xml"],
    "installable": True,
    "license": "AGPL-3",
}
