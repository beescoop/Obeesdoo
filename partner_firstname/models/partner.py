# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

def concat_names(*args):
    """
        Concatenate only args that are not empty
        @param args: a list of string
    """
    return ' '.join(filter(bool, args))

class Partner(models.Model):

    _inherit = 'res.partner'

    firstname = fields.Char('First Name')
    lastname = fields.Char('Last Name', required=True, default="/")
    name = fields.Char(compute='_get_name', inverse='_set_name', store=True)

    @api.depends('firstname', 'lastname')
    def _get_name(self):
        for rec in self:
            rec.name = concat_names(rec.firstname, rec.lastname)

    def _set_name(self):
        """
            This allow to handle the case of code that write directly on the name at creation
            Should never happen but in case it happen write on the lastname
            If there is no firstname lastname and name are the same
        """
        for rec in self:
            if not rec.firstname:
                rec.lastname = rec.name


    def _compatibility_layer(self, vals):
        if 'last_name' in vals:
            if not 'lastname' in vals:
                vals['lastname'] = vals['last_name']
            vals.pop('last_name')
        if 'first_name' in vals:
            if not 'firstname' in vals:
                vals['firstname'] = vals['first_name']
            vals.pop('first_name')
        return vals

    @api.multi
    def write(self, vals):
        return super(Partner, self).write(self._compatibility_layer(vals))

    @api.model
    def create(self, vals):
        return super(Partner, self).create(self._compatibility_layer(vals))
