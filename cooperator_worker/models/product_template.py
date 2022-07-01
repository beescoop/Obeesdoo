from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_working = fields.Boolean(
        string="Allow owner to work?",
        help=(
            "Owner of this type of share are allowed to participate to the "
            "shift system."
        ),
    )
    allow_shopping = fields.Boolean(
        string="Allow owner to shop?",
        help="Owner of this type of share are allowed to shop.",
    )
