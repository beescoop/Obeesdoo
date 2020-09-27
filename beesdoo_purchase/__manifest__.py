{
    "name": "Bees Purchase",
    "summary": """
        - Adds a 'Responsible' field to purchase orders
        - A filter w.r.t. the mail sellers is placed on the products field of a
        purchase order
        - Allow inverting the Purchase Order Reference on the invoice lines
    """,
    "author": "Beescoop - Cellule IT, " "Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Purchase",
    "version": "12.0.1.2.0",
    "depends": ["base", "purchase", "beesdoo_product"],
    "data": [
        "security/invoice_security.xml",
        "views/purchase_order.xml",
        "views/res_config_settings_view.xml",
        "report/report_purchaseorder.xml",
    ],
    "license": "AGPL-3",
}
