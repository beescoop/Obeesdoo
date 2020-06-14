{
    "name": "Bees Purchase",
    "summary": """
        Extends Purchase module. 
        """,
    "description": """
        Extends Purchase module: 
        - Adds a 'Responsible' field to purchase orders:
        This is a user who will follow up the order. This users replaces 
        the creator in the order's mail messages followers list, and in the 
        create_uid ORM field. His user's contact info is printed on 
        purchases orders as 'Referent'.
        - A filter w.r.t. the mail sellers is placed on the products field of a 
        purchase order.  
    """,
    "author": "Beescoop - Cellule IT, " "Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Purchase",
    "version": "12.0.1.1.0",
    "depends": ["base", "purchase", "beesdoo_product"],
    "data": ["views/purchase_order.xml", "report/report_purchaseorder.xml",],
}
