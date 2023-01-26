{
    "name": "Bees Purchase",
    "summary": """
        Enhancements related to Purchase module :
        field, filter, PO reference, product's purchase and/or selling price
    """,
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Purchase",
    "version": "12.0.1.4.0",
    "depends": [
        "purchase",
        # beesdoo_purchase was (almost entirely) split into the subsequent modules.
        "purchase_order_responsible",
        "account_invoice_line_custom_reference",
        "purchase_order_main_supplier",
    ],
    "data": [
        "views/purchase_order.xml",
    ],
    "license": "AGPL-3",
}
