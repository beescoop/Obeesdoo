from odoo import _, api, models
from odoo.exceptions import UserError


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
        return self.env["beesdoo.shift.template.dated"].swap_shift_to_tmpl_dated(shifts)

    @api.multi
    def send_mail_coop_same_days_same_hour(self, my_tmpl_dated, partner_to):
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_contact_coop", False
        )
        email_values = {"my_tmpl_dated": my_tmpl_dated, "worker_id": partner_to}
        template_rec.write({"partner_to": partner_to.id})
        template_rec.with_context(email_values).send_mail(self.id, False)

    def check_shift_number_limit(self, wanted_tmpl_dated):
        """
        Check if subscribing to a shift would exceed the daily and
        monthly shift number limit
        :param wanted_tmpl_dated: the tmpl_dated matching the shift to subscribe
        """
        my_next_tmpl_dated = self.get_next_tmpl_dated()
        shift_in_day = 0
        shift_in_month = 0
        for tmpl_dated in my_next_tmpl_dated:
            if tmpl_dated.date.date() == wanted_tmpl_dated.date.date():
                shift_in_day += 1
            if tmpl_dated.date.month == wanted_tmpl_dated.date.month:
                shift_in_month += 1
        if shift_in_day >= 2:
            raise UserError(_("You already have 2 shifts in a day"))
        if shift_in_month >= 5:
            raise UserError(_("You already have 5 shifts in a month"))
