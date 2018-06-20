# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.beesdoo_base.tools import concat_names

class Partner(models.Model):

    _inherit = 'res.partner'

    eater = fields.Selection([('eater', 'Eater'), ('worker_eater', 'Worker and Eater')], string="Eater/Worker")
    child_eater_ids = fields.One2many("res.partner", "parent_eater_id", domain=[('customer', '=', True),
                                                                                ('eater', '=', 'eater')])
    parent_eater_id = fields.Many2one("res.partner", string="Parent Worker", readonly=True)
    barcode = fields.Char(compute="_get_bar_code", string='Barcode', store=True)
    parent_barcode = fields.Char(compute="_get_bar_code", string='Parent Barcode', store=True)
    member_card_ids = fields.One2many('member.card', 'partner_id')
    country_id = fields.Many2one(required=True, default=lambda self: self.env.ref('base.be'))

    member_card_to_be_printed = fields.Boolean('Print BEES card?')
    last_printed = fields.Datetime('Last printed on')
    cooperator_type = fields.Selection([('share_a', 'Share A'), ('share_b', 'Share B'), ('share_c', 'Share C')], store=True, compute=None)


    @api.one
    @api.depends('parent_eater_id', 'parent_eater_id.barcode', 'eater', 'member_card_ids')
    def _get_bar_code(self):
        if self.eater == 'eater':
            self.parent_barcode = self.parent_eater_id.barcode
        elif self.member_card_ids:
            for c in self.member_card_ids:
                if c.valid:
                    self.barcode = c.barcode

    @api.one
    @api.constrains('child_eater_ids', 'parent_eater_id')
    def _check_number_of_eaters(self):
        """The owner of an A share can have a maximum of two eaters but
        the owner of a B share can have a maximum of three eaters.
        """
        # Get the default_code of the share for the current eater and his parent
        share_type_code = self.cooperator_type
        parent_share_type_code = self.parent_eater_id.cooperator_type
        # Raise exception
        if share_type_code == 'share_b' or parent_share_type_code == 'share_b':
            if len(self.child_eater_ids) > 3 or len(self.parent_eater_id.child_eater_ids) > 3:
                raise ValidationError(_('You can only set three additional eaters per worker'))
        else:
            if len(self.child_eater_ids) > 2 or len(self.parent_eater_id.child_eater_ids) > 2:
                raise ValidationError(_('You can only set two additional eaters per worker'))


    @api.multi
    def write(self, values):
        if values.get('parent_eater_id') and self.parent_eater_id:
            raise ValidationError(_('You try to assign a eater to a worker but this easer is alread assign to %s please remove it before') % self.parent_eater_id.name)
        # replace many2many command when writing on child_eater_ids to just remove the link
        if 'child_eater_ids' in values:
            for command in values['child_eater_ids']:
                if command[0] == 2:
                    command[0] = 3
        return super(Partner, self).write(values)

    @api.one
    def _deactivate_active_cards(self):
        for card in self.member_card_ids.filtered('valid'):
            card.valid = False
            card.end_date = fields.Date.today()

    @api.multi
    def _new_card(self, reason, user_id, barcode=False):
        card_data = {
            'partner_id' : self.id,
            'responsible_id' : user_id,
            'comment' : reason,
        }
        if barcode:
            card_data['barcode'] = barcode
        self.env['member.card'].create(card_data)

    @api.multi
    def _new_eater(self, surname, name, email):
        partner_data = {

                        'lastname' : name,
                        'firstname' : surname,
                        'is_customer' : True,
                        'eater' : 'eater',
                        'parent_eater_id' : self.id,
                        'email' : email,
                        'country_id' : self.country_id.id
                        }
        return self.env['res.partner'].create(partner_data)
