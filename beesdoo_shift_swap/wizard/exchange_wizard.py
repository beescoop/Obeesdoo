from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel):
    _name = "beesdoo.shift.subscribe.shift.exchange"
    _description = "Subscribe Exchange shift"

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
    )

    exchanged_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="Exchanged shift",
        required=True,
    )

    asked_tmpl_dated_ids = fields.Many2many(
        comodel_name="beesdoo.shift.template.dated",
        relation="wizard_exchange_template_dated",
        string="Asked shifts",
    )

    possible_match = fields.Many2one(
        "beesdoo.shift.exchange_request",
        string="Possible match",
    )

    @api.onchange("worker_id")
    def _get_template_dated(self):
        for record in self:
            tmpl_dated = record.worker_id.get_next_tmpl_dated()
            tmpl_dated_possible = self.env["beesdoo.shift.template.dated"]
            for template in tmpl_dated:
                tmpl_dated_possible |= tmpl_dated_possible.create(
                    {
                        "template_id": template.template_id.id,
                        "date": template.date,
                        "store": False,
                    }
                )
            return {
                "domain": {
                    "exchanged_tmpl_dated_id": [("id", "in", tmpl_dated_possible.ids)]
                }
            }

    @api.onchange("worker_id")
    def _get_possible_tmpl_dated(self):
        for record in self:
            day_limit_ask_for_exchange = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_shift.day_limit_ask_for_exchange")
            )
            end_date = datetime.now() + timedelta(days=day_limit_ask_for_exchange)
            available_tmpl_dated = self.env[
                "beesdoo.shift.template.dated"
            ].get_available_tmpl_dated(end_date=end_date)
            tmpl_dated_possible = available_tmpl_dated.remove_already_subscribed_shifts(
                record.worker_id
            )
            tmpl_dated_wanted = self.env["beesdoo.shift.template.dated"]
            for template in tmpl_dated_possible:
                tmpl_dated_wanted |= tmpl_dated_wanted.create(
                    {
                        "template_id": template.template_id.id,
                        "date": template.date,
                        "store": False,
                    }
                )
            return {
                "domain": {
                    "asked_tmpl_dated_ids": [("id", "in", tmpl_dated_wanted.ids)]
                }
            }

    @api.onchange("exchanged_tmpl_dated_id", "asked_tmpl_dated_ids")
    def _get_possible_match(self):
        for record in self:
            if not record.exchanged_tmpl_dated_id:
                record.possible_match = False
            else:
                if record.asked_tmpl_dated_ids:
                    matches = self.env[
                        "beesdoo.shift.exchange_request"
                    ].matching_request(
                        record.asked_tmpl_dated_ids, record.exchanged_tmpl_dated_id
                    )
                else:
                    matches = self.env[
                        "beesdoo.shift.exchange_request"
                    ].get_possible_match(record.exchanged_tmpl_dated_id)
                return {"domain": {"possible_match": [("id", "in", matches.ids)]}}

    def _check(self, group="shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if self.worker_id == self.env.user.partner_id and not self.env.user.has_group(
            "shift.group_cooperative_admin"
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    def request_exchange(self):
        self = self._check()
        if not self.asked_tmpl_dated_ids and not self.possible_match:
            raise UserError(
                _("Please either ask for shifts to exchange or select a match")
            )

        self.exchanged_tmpl_dated_id.store = True
        for rec in self.asked_tmpl_dated_ids:
            rec.store = True
            self.worker_id.check_shift_number_limit(rec)

        self.env["beesdoo.shift.template.dated"].search(
            [("store", "=", False)]
        ).unlink()

        data = {
            "worker_id": self.worker_id.id,
            "exchanged_tmpl_dated_id": self.exchanged_tmpl_dated_id.id,
            "asked_tmpl_dated_ids": [
                (6, False, self.possible_match.exchanged_tmpl_dated_id.ids)
            ]
            if self.possible_match
            else [(6, False, self.asked_tmpl_dated_ids.ids)],
            "validate_request_id": self.possible_match.id
            if self.possible_match
            else False,
        }
        self.env["beesdoo.shift.exchange_request"].sudo().create(data)

    def contact_coop(self):
        """
        Send a mail to all workers of asked_tmpl_dated_ids
        before creating the exchange request
        """
        if not self.asked_tmpl_dated_ids:
            raise UserError(_("Please ask for at least one shift"))

        self.request_exchange()

        for tmpl_dated in self.asked_tmpl_dated_ids:
            for worker in tmpl_dated.template_id.worker_ids:
                self.worker_id.send_mail_for_exchange(
                    self.exchanged_tmpl_dated_id, tmpl_dated, worker
                )
