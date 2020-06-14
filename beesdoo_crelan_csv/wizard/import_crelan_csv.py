import csv
import datetime
import hashlib
from io import StringIO

from odoo import _, models

ACCOUNT = "Compte donneur d'ordre"
CURRENCY = "Devise"
DATE = "Date"
AMOUNT = "Montant"
COUNTERPART_NUMBER = "Compte contrepartie"
COUNTERPART_NAME = "Contrepartie"
COMMUNICATION = "Communication"
TRANSACTION_TYPE = "Type d'opération"


class CodaBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    _date_format = "%d/%m/%Y"

    _decimal_sep = "."
    _csv_delimiter = ";"
    _csv_quote = '"'

    _header = [
        "Date",
        "Montant",
        "Devise",
        "Contrepartie",
        "Compte contrepartie",
        "Type d'opération",
        "Communication",
        "Compte donneur d'ordre",
    ]

    def _generate_note_crelan(self, move):
        notes = []
        notes.append(
            "{}: {}".format(_("Counter Party Name"), move[COUNTERPART_NAME])
        )
        notes.append(
            "{}: {}".format(
                _("Counter Party Account"), move[COUNTERPART_NUMBER]
            )
        )
        notes.append("{}: {}".format(_("Communication"), move[COMMUNICATION]))
        return "\n".join(notes)

    def _get_move_value_crelan(self, move, sequence):
        move_data = {
            "name": move[TRANSACTION_TYPE] + ": " + move[COMMUNICATION],
            "note": self._generate_note_crelan(move),
            "date": self._to_iso_date(move[DATE]),
            "amount": float(move[AMOUNT]),
            "account_number": move[COUNTERPART_NUMBER],  # Ok
            "partner_name": move[COUNTERPART_NAME],  # Ok
            "ref": move[DATE]
            + "-"
            + move[AMOUNT]
            + "-"
            + move[COUNTERPART_NUMBER]
            + "-"
            + move[COUNTERPART_NAME],
            "sequence": sequence,  # Ok
            "unique_import_id": move[DATE]
            + "-"
            + move[AMOUNT]
            + "-"
            + move[COUNTERPART_NUMBER]
            + "-"
            + move[COUNTERPART_NAME]
            + "-"
            + hashlib.new("md5", move[COMMUNICATION].encode()).hexdigest(),
        }
        return move_data

    def _get_statement_data_crelan(
        self, balance_start, balance_end, begin_date, end_date
    ):
        statement_data = {
            "name": _("Bank Statement from %s to %s") % (begin_date, end_date),
            "date": self._to_iso_date(end_date),
            "balance_start": balance_start,  # Ok
            "balance_end_real": balance_end,  # Ok
            "transactions": [],
        }
        return statement_data

    def _get_acc_number_crelan(self, acc_number):
        # Check if we match the exact acc_number or the end of an acc number
        journal = self.env["account.journal"].search(
            [("bank_acc_number", "=like", "%" + acc_number)]
        )
        if not journal or len(journal) > 1:  # If not found or ambiguious
            return acc_number

        return journal.bank_acc_number

    def _get_acc_balance_crelan(self, acc_number):
        if self.init_balance is not None:
            return self.init_balance

        journal = self.env["account.journal"].search(
            [("bank_acc_number", "=like", "%" + acc_number)]
        )
        currency = journal.currency_id or journal.company_id.currency_id
        if not journal or len(journal) > 1:  # If not found or ambiguious
            self.init_balance = 0.0
        else:
            lang = self._context.get("lang", "en_US")
            lang = self.env["res.lang"].search([("code", "=", lang)])
            balance = journal.get_journal_dashboard_datas()["last_balance"][
                :-1
            ]
            self.init_balance = float(
                balance.replace(currency.symbol, "")
                .strip()
                .replace(lang.thousands_sep, "")
                .replace(lang.decimal_point, ".")
            )
        return self.init_balance

    def _to_iso_date(self, orig_date):
        date_obj = datetime.datetime.strptime(orig_date, self._date_format)
        return date_obj.strftime("%Y-%m-%d")

    def _parse_file(self, data_file):

        try:
            csv_file = StringIO(data_file.decode())
            data = csv.DictReader(
                csv_file,
                delimiter=self._csv_delimiter,
                quotechar=self._csv_quote,
            )
            if not data.fieldnames == self._header:
                raise ValueError()
        except ValueError:
            return super(CodaBankStatementImport, self)._parse_file(data_file)

        currency_code = False
        account_number = False
        self.init_balance = None
        begin_date = False
        end_date = False

        transactions = []
        i = 1
        sum_transaction = 0
        for statement in data:
            begin_date = begin_date or statement[DATE]
            end_date = statement[DATE]
            account_number = statement[ACCOUNT]
            balance = self._get_acc_balance_crelan(account_number)
            currency_code = statement[CURRENCY]
            transactions.append(self._get_move_value_crelan(statement, i))
            sum_transaction += float(statement[AMOUNT])
            i += 1
        stmt = self._get_statement_data_crelan(
            balance, balance + sum_transaction, begin_date, end_date
        )
        stmt["transactions"] = transactions
        return (
            currency_code,
            self._get_acc_number_crelan(account_number),
            [stmt],
        )
