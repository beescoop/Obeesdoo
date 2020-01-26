# Copyright 2017-2018 Elise Dupont
# Copyright 2017-2020 Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Beescoop  Account Module",
    "summary": """
		Module that customize account module for Beescoop
     """,
    "description": """
        Makes date_invoice field required in account.invoice_form and
        account.invoice_supplier_form
    """,
    "author": "Beescoop - Cellule IT",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Account Module",
    "version": "12.0.1.0.0",
    "depends": ["account", "beesdoo_base"],
    "data": ["views/account_invoice.xml"],
}
