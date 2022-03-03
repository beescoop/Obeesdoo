from odoo import api, _, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel) :
    _name = 'beesdoo.shift.subscribe.shift.exchange'
    _description = 'Subscribe Exchange shift'

    @api.onchange('worker_id')
    def onchange_exchanged_tmpl_dated(self):
        # TODO : prendre en compte qd il est inscris a aucun shift
        for record in self:
            if not record.worker_id:
                record.exchanged_tmpl_dated_id = False
            else:
                tmpl_dated = self.env["beesdoo.shift.template.dated"].my_tmpl_dated(record.worker_id)
                # record.available_tmpl_dated = tmpl_dated
                temp = self.env["beesdoo.shift.template.dated"]
                for rec in tmpl_dated:
                    template = rec.template_id
                    date = rec.date
                    temp |= temp.create({
                        'template_id': template.id,
                        'date': date,
                        'store': False,
                    })
                return {
                    'domain': {'exchanged_tmpl_dated_id': [('id', 'in', temp.ids)]}
                }

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
    )

    exchanged_tmpl_dated_id = fields.Many2one('beesdoo.shift.template.dated', string='exchanged_tmpl_dated')

    @api.onchange('exchanged_tmpl_dated_id')
    def _get_available_tmpl_dated(self):
        for record in self:
            if not record.exchanged_tmpl_dated_id:
                record.confirmed_tmpl_dated_id = False
            else:
                tmpl_dated = self.env["beesdoo.shift.template.dated"].display_tmpl_dated()
                # record.available_tmpl_dated = tmpl_dated
                temp = self.env["beesdoo.shift.template.dated"]
                for rec in tmpl_dated:
                    template = rec.template_id
                    date = rec.date
                    temp |= temp.create({
                        'template_id': template.id,
                        'date': date,
                        'store': False,
                    })
                return {
                    'domain': {'asked_tmpl_dated_ids': [('id', 'in', temp.ids)]}
                }
    # TODO : relational fields
    asked_tmpl_dated_ids = fields.Many2many(
        comodel_name='beesdoo.shift.template.dated',
        #inverse_name='id',
        relation='wizard_exchange_template_dated',
        string='asked_tmpl_dated',
    )

    @api.onchange('asked_tmpl_dated_ids')
    def get_possible_match(self):
        for record in self :
            if not record.exchanged_tmpl_dated_id or not record.asked_tmpl_dated_ids :
                record.possible_match = False
            else :
                exchanges = self.env["beesdoo.shift.exchange_request"].matching_request(record.asked_tmpl_dated_ids,record.exchanged_tmpl_dated_id)
                return {
                    'domain': {'possible_match': [('id', 'in', exchanges.ids)]}
                }


    possible_match= fields.Many2one(
        'beesdoo.shift.exchange_request',
        string='possible match',
    )


    def _check(self, group="beesdoo_shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(
                _("You don't have the required access for this operation.")
            )
        if (
            self.worker_id == self.env.user.partner_id
            and not self.env.user.has_group(
                "beesdoo_shift.group_cooperative_admin"
            )
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    @api.multi
    def make_change(self):
        self = self._check()
        self.exchanged_tmpl_dated_id.store = True
        #self.asked_tmpl_dated_ids.store = True
        for rec in self.asked_tmpl_dated_ids :
            rec.store = True
            self.env["beesdoo.shift.template.dated"].check_possibility_to_exchange(rec,
                                                                                   self.worker_id)
        #for tmpl_dated in self.asked_tmpl_dated_ids.ids :

        data = {
            "request_date": datetime.date(datetime.now()),
            "worker_id": self.worker_id.id,
            "exchanged_tmpl_dated_id": self.exchanged_tmpl_dated_id.id,
            "asked_tmpl_dated_ids":[(6,False, self.asked_tmpl_dated_ids.ids)],
            "validate_request_id":self.possible_match.id,
            "status": 'validate_match' if self.possible_match else 'no_match',
        }

        useless_tmpl_dated = self.env["beesdoo.shift.template.dated"].search([
            ("store", '=', False)
        ])
        useless_tmpl_dated.unlink()
        record = self.env["beesdoo.shift.exchange_request"].sudo().create(data)
        if self.possible_match :
            self.possible_match.write(
                {'status': 'has_match'}
            )

    @api.multi
    def contact_coop_same_day_same_hour(self):
        partner_rec = self.env["beesdoo.shift.exchange_request"].get_coop_same_days_same_hour(self.exchanged_tmpl_dated_id)
        for rec in partner_rec:
            self.worker_id.send_mail_coop_same_days_same_hour(self.exchanged_tmpl_dated_id,rec)
