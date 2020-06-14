from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    max_nb_eater_allowed = fields.Integer(
        string="Max number of eater allowed",
        default=-1,
        help=(
            "Maximum number of eater allowed for the owner of the share. "
            "A negative value means no maximum."
        ),
    )
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
    eater = fields.Selection(
        [("eater", "Eater"), ("worker_eater", "Worker and Eater")],
        string="Eater/Worker",
    )
