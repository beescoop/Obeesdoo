from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # create_uid must mirror the supervisor_id value.
    # create_uid is a magic field that belongs to the ORM that is not
    # editable via a form.
    create_uid = fields.Many2one(
        comodel_name="res.users", compute="_compute_create_uid"
    )
    supervisor_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.user,
    )

    @api.depends("supervisor_id")
    def _compute_create_uid(self):
        for rec in self:
            if rec.supervisor_id:
                rec.create_uid = rec.supervisor_id

    @api.multi
    def write(self, vals):
        if "supervisor_id" in vals:
            new_partner = (
                self.env["res.users"]
                .browse(vals["supervisor_id"])
                .partner_id.id
            )
            for rec in self:
                rec.message_unsubscribe(
                    partner_ids=rec.supervisor_id.partner_id.ids
                )
                rec.message_subscribe(
                    partner_ids=[new_partner], subtype_ids=[]
                )
        return super(PurchaseOrder, self).write(vals)
