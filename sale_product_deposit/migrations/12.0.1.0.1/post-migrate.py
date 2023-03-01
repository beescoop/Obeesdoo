from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    product_templates = env["product.template"].search([])
    for product in product_templates:
        product._compute_total()
