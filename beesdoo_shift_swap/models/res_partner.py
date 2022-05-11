from odoo import _, api, models


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
    def coop_offer_solidarity(self):
        return {
            "name": _("Solidarity shift offer wizard"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.offer.solidarity.shift",
            "target": "new",
        }

    @api.multi
    def coop_request_solidarity(self):
        return {
            "name": _("Solidarity shift request wizard"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.request.solidarity.shift",
            "target": "new",
        }

    def get_next_tmpl_dated(self):
        """
        Same utility as get_next_shifts() but return beesdoo.shift.template.dated
        :return: beesdoo.shift.template.dated recordset
        """
        shifts = self.get_next_shifts()
        tmpl_dated = self.env["beesdoo.shift.template.dated"]
        if shifts:
            tmpl_dated = self.swap_shift_to_tmpl_dated(shifts)
        return tmpl_dated

    @api.multi
    def send_mail_coop_same_days_same_hour(self, my_tmpl_dated, partner_to):
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_contact_coop", False
        )
        email_values = {"my_tmpl_dated": my_tmpl_dated, "worker_id": partner_to}
        template_rec.write({"partner_to": partner_to.id})
        template_rec.with_context(email_values).send_mail(self.id, False)
