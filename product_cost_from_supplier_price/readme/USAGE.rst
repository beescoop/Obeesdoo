To enable this feature, the costing method (``property_cost_method``) of the product's category should be set to "Standard Price (From Main Supplier's Price)" (``standard_from_main_supplier_price``).

As the supplier's price is defined per product (``product.template``) and not per variant (``product.product``), if a product has multiple variants, the cost is not updated.
