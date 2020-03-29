from odoo import models, fields


class ProductTemplate(models.Model):

    inherit = 'product.template'

    can_shop = fields.Boolean(string="Is share?")
