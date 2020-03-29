# -*- encoding: utf-8 -*-
{
    "name": "Product - Stock Coverage",
    "version": "9.0.1",
    "category": "Product",
    "description": """
Shows figures in the product form related to stock coverage
There are settings in Inventory/settings to define the calculation range and
the display range.
    """,
    "author": "coop it easy",
    "website": "coopiteasy.be",
    "license": "AGPL-3",
    "depends": ["product", "purchase", "point_of_sale", "stock"],
    "data": ["views/product_template_view.xml", "data/cron.xml"],
}
