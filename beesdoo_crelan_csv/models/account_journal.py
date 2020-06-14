from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_bank_statements_available_import_formats(self):
        formats_list = super()._get_bank_statements_available_import_formats()
        formats_list.append("Crelan")
        return formats_list
