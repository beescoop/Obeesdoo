# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.beesdoo_base.tools import concat_names

class Partner(models.Model):

    _inherit = 'res.partner'

    first_name = fields.Char('First Name')
    last_name = fields.Char('Last Name', required=True)

    eater = fields.Selection([('eater', 'Mangeur'), ('worker_eater', 'Mangeur et Travailleur')], string="Mangeur/Travailleur")

    child_eater_ids = fields.One2many("res.partner", "parent_eater_id", domain=[('customer', '=', True),
                                                                                ('eater', '=', 'eater')])

    parent_eater_id = fields.Many2one("res.partner", string="Parent Travailleur", readonly=True)

    barcode = fields.Char(compute="_get_bar_code", string='Code Barre', store=True)
    parent_barcode = fields.Char(compute="_get_bar_code", string='Code Barre du Parent', store=True)
    member_card_ids = fields.One2many('member.card', 'partner_id')

    @api.onchange('first_name', 'last_name')
    def _on_change_name(self):
        self.name = concat_names(self.first_name, self.last_name)

    @api.one
    @api.constrains('country_id')
    def _check_country(self):
        if len(self.country_id) == 0:
            raise ValidationError(_('Country is mandatory'))

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
    def _only_two_eaters(self):
        if len(self.child_eater_ids) > 2 or len(self.parent_eater_id.child_eater_ids) > 2:
            raise ValidationError(_('You can only set two additional eaters per worker'))

    @api.multi
    def write(self, values):
        if values.get('parent_eater_id') and self.parent_eater_id:
            raise ValidationError(_('You try to assign a eater to a worker but this easer is alread assign to %s please remove it before') % self.parent_eater_id.name)
        #replace many2many command when writing on child_eater_ids to just remove the link
        if 'child_eater_ids' in values:
            for command in values['child_eater_ids']:
                if command[0] == 2:
                    command[0] = 3
        return super(Partner, self).write(values)
    
    @api.multi
    def _deactivate_active_cards(self):
        if len(self.member_card_ids) > 0:
            for c in self.member_card_ids:
                if c.valid:
                    c.valid = False
                    c.end_date = fields.Date.today()      
    @api.multi            
    def _new_card(self, txt):
        self.env['member.card'].create({'partner_id' : self.env.context['active_id'],'comment' : txt})

