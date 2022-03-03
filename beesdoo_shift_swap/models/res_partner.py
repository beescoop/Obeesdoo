from odoo import _, api, models
from datetime import timedelta



class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.multi
    def coop_swap(self):
        return {
            "name": _("Subscribe Swap Cooperator"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.subscribe.shift.swap",
            "target": "new",
        }

    @api.multi
    def coop_exchange(self):
        return {
            "name": _("Exchange Swap Cooperator"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.subscribe.shift.exchange",
            "target": "new",
        }

    @api.multi
    def send_mail_coop_same_days_same_hour(self, my_tmpl_dated,partner_to):
        template_rec = self.env.ref("beesdoo_shift_swap.email_template_contact_coop", False)
        email_values = {
            "my_tmpl_dated": my_tmpl_dated,
            "worker_id":partner_to
        }
        template_rec.write({'partner_to': partner_to.id})
        template_rec.with_context(email_values).send_mail(self.id, False)
