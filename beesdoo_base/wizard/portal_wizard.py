from openerp.osv import osv
from openerp import models, fields, api
from openerp import SUPERUSER_ID

class BeesdooWizard(osv.osv_memory):
    
    _inherit = 'portal.wizard'
    
    def onchange_portal_id(self, cr, uid, ids, portal_id, context=None):
        # for each partner, determine corresponding portal.wizard.user records
        res_partner = self.pool.get('res.partner')
        partner_ids = context and context.get('active_ids') or []
        contact_ids = set()
        user_changes = []
        for partner in res_partner.browse(cr, SUPERUSER_ID, partner_ids, context):
            # Bug for BEESDOO : the partner itself did not appear in the list when he has contacts ?
            # Is it a normal behaviour ? Here I have modified this function in order to first add the partner itself
            # then all its contacts to the list
            # make sure that each contact appears at most once in the list
            if partner.id not in contact_ids:
                contact_ids.add(partner.id)
                in_portal = False
                if partner.user_ids:
                     in_portal = portal_id in [g.id for g in partner.user_ids[0].groups_id]
                user_changes.append((0, 0, {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'in_portal': in_portal,
                }))
            for contact in (partner.child_ids):
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    in_portal = False
                    if contact.user_ids:
                        in_portal = portal_id in [g.id for g in contact.user_ids[0].groups_id]
                    user_changes.append((0, 0, {
                        'partner_id': contact.id,
                        'email': contact.email,
                        'in_portal': in_portal,
                    }))
        return {'value': {'user_ids': user_changes}}
