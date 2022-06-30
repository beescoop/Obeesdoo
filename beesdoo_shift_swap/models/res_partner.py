from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):

    _inherit = "res.partner"

    subscribed_exchange_emails = fields.Boolean(
        string="Echange emails subscription",
        default=True,
    )

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
        generated_shifts, planned_shifts = self.get_next_shifts()
        shifts = generated_shifts + planned_shifts
        return self.env["beesdoo.shift.template.dated"].swap_shift_to_tmpl_dated(shifts)

    @api.multi
    def send_mail_for_exchange(self, my_tmpl_dated, asked_tmpl_dated, partner_to):
        """
        Send a mail to partner_to asking for an exchange
        :param my_tmpl_dated: beesdoo.shift.template.dated
        :param asked_tmpl_dated: beesdoo.shift.template.dated
        :param partner_to: res.partner
        """
        if not self.subscribed_exchange_emails:
            return False
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_contact_coop", False
        )
        email_values = {
            "my_tmpl_dated": my_tmpl_dated,
            "asked_tmpl_dated": asked_tmpl_dated,
            "worker_id": partner_to,
        }
        template_rec.write({"partner_to": partner_to.id})
        template_rec.with_context(email_values).send_mail(self.id, False)
        return True

    def check_shift_number_limit(self, wanted_tmpl_dated):
        """
        Check if subscribing to a shift matching the wanted_tmpl_dated
        would exceed the daily and monthly shift number limit
        :param wanted_tmpl_dated: beesdoo.shift.template.dated
        """
        my_next_tmpl_dated = self.get_next_tmpl_dated()
        shift_in_day = 0
        shift_in_month = 0
        max_shift_per_day = int(
            self.env["ir.config_parameter"].sudo().get_param("max_shift_per_day")
        )
        max_shift_per_month = int(
            self.env["ir.config_parameter"].sudo().get_param("max_shift_per_month")
        )
        for tmpl_dated in my_next_tmpl_dated:
            if tmpl_dated.date.date() == wanted_tmpl_dated.date.date():
                shift_in_day += 1
            if tmpl_dated.date.month == wanted_tmpl_dated.date.month:
                shift_in_month += 1
        if shift_in_day >= max_shift_per_day:
            raise UserError(_("Maximum number of shifts per day reached"))
        if shift_in_month >= max_shift_per_month:
            raise UserError(_("Maximum number of shifts per month reached"))

    def get_next_shifts(self):
        """
        Override get_next_shifts method to take into account
        shift exchanges and solidarity shifts
        """
        generated_shifts, planned_shifts = super(ResPartner, self).get_next_shifts()

        # Get all the changes related to self
        swaps = self.env["beesdoo.shift.swap"].search([("worker_id", "=", self.id)])
        exchange_requests = self.env["beesdoo.shift.exchange_request"].search(
            [
                ("worker_id", "=", self.id),
                ("status", "=", "done"),
            ]
        )
        solidarity_offers = self.env["beesdoo.shift.solidarity.offer"].search(
            [
                ("worker_id", "=", self.id),
                ("state", "=", "validated"),
            ]
        )
        solidarity_requests = self.env["beesdoo.shift.solidarity.request"].search(
            [
                ("worker_id", "=", self.id),
                ("state", "=", "validated"),
            ]
        )

        # Swaps
        for swap in swaps:
            planned_shifts = self.exchange_shifts(
                generated_shifts,
                planned_shifts,
                swap.exchanged_tmpl_dated_id,
                swap.wanted_tmpl_dated_id,
            )

        # Exchanges
        for request in exchange_requests:
            planned_shifts = self.exchange_shifts(
                generated_shifts,
                planned_shifts,
                request.exchanged_tmpl_dated_id,
                request.validate_request_id.exchanged_tmpl_dated_id,
            )

        # Solidarity offers
        for offer in solidarity_offers:
            planned_shifts = self.exchange_shifts(
                generated_shifts,
                planned_shifts,
                wanted_tmpl_dated=offer.tmpl_dated_id,
                solidarity_offer=offer,
            )

        # Solidarity requests
        for sol_request in solidarity_requests:
            planned_shifts = self.exchange_shifts(
                generated_shifts,
                planned_shifts,
                exchanged_tmpl_dated=sol_request.tmpl_dated_id,
            )

        return generated_shifts, planned_shifts

    def exchange_shifts(
        self,
        generated_shifts,
        planned_shifts,
        exchanged_tmpl_dated=None,
        wanted_tmpl_dated=None,
        solidarity_offer=None,
    ):
        """
        Update the personal future shifts list by exchanging two shifts.
        Parameters generated_shifts and planned_shifts are generated
        by method get_next_shifts.
        exchanged_tmpl_dated is the dated template the user has to be unsubscribed from.
        wanted_tmpl_dated is the dated template the user has to be subscribed to.
        One of these two parameters can be None if there are no shifts
        to subscribe/unsubscribe.

        :param generated_shifts: beesdoo.shift.shift list
        :param planned_shift: beesdoo.shift.shift list
        :param exchanged_tmpl_dated: beesdoo.shift.template.dated
        :param wanted_tmpl_dated: beesdoo.shift.template.dated
        :param solidarity_offer: beesdoo.shift.solidarity.offer
        :return planned_shift: beesdoo.shift.shift list
        """
        self.ensure_one()
        if exchanged_tmpl_dated and exchanged_tmpl_dated.date > datetime.now():
            # Remove the exchanged shift from the list if it is not yet generated
            for shift in planned_shifts:
                if (
                    shift.task_template_id == exchanged_tmpl_dated.template_id
                    and shift.start_time == exchanged_tmpl_dated.date
                ):
                    planned_shifts.remove(shift)

        if wanted_tmpl_dated and wanted_tmpl_dated.date > datetime.now():
            # Search if wanted shift is generated
            new_shift_generated = False
            for shift in generated_shifts:
                if (
                    shift.task_template_id == wanted_tmpl_dated.template_id
                    and shift.start_time == wanted_tmpl_dated.date
                ):
                    new_shift_generated = True
                    break
            # If not, create it and add it to the list
            if not new_shift_generated:
                new_shift = wanted_tmpl_dated.new_shift(self)
                if solidarity_offer:
                    new_shift.write(
                        {"solidarity_offer_ids": [(6, 0, solidarity_offer.ids)]}
                    )
                planned_shifts.append(new_shift)

        return planned_shifts
