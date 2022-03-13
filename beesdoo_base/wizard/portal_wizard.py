from odoo import api, models


class BeesdooWizard(models.TransientModel):
    _inherit = "portal.wizard"

    @api.onchange("portal_id")
    def onchange_portal(self):
        # for each partner, determine corresponding portal.wizard.user records
        res_partner = self.env["res.partner"]
        partner_ids = self._context.get("active_ids", [])

        contact_ids = set()
        for partner in res_partner.browse(partner_ids):
            for contact in partner.child_ids | partner:
                # make sure that each contact appears at most once in the list
                if contact.id not in contact_ids:
                    contact_ids.add(contact.id)
                    in_portal = self.portal_id in contact.user_ids.mapped("groups_id")
                    self.user_ids |= self.env["portal.wizard.user"].new(
                        {
                            "partner_id": contact.id,
                            "email": contact.email,
                            "in_portal": in_portal,
                        }
                    )
