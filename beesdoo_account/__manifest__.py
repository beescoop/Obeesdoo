# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Vincent Van Rossem <vincent@coopiteasy.be>
#   - Elise Dupont
#   - Augustin Borsu
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Beescoop  Account Module",
    "summary": """
        - Makes date_invoice field required in account.invoice_form and
        account.invoice_supplier_form
        - Allow validating an invoice with a negative total amount
             """,
    "author": "Beescoop - Cellule IT, Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Account Module",
    "version": "12.0.2.0.0",
    "depends": [
        "account",
        "account_invoice_date_required",
        "account_invoice_negative_total",
    ],
    "data": [
        "views/account_invoice.xml",
    ],
    "license": "AGPL-3",
}
