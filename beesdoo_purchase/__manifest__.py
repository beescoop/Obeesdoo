{
    "name": "Bees Purchase",
    "summary": """
        Enhancements related to Purchase module :
        field, filter, PO reference, product's purchase and/or selling price
    """,
    "author": "Beescoop - Cellule IT, " "Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Purchase",
    "version": "12.0.1.3.0",
    "depends": ["base", "purchase", "beesdoo_product"],
    "data": [
        "security/invoice_security.xml",
        "views/purchase_order.xml",
        "views/res_config_settings_view.xml",
        "report/report_purchaseorder.xml",
    ],
    "license": "AGPL-3",
}
