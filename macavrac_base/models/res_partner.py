from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    date_stamp = fields.Date(
        string="Timestamp", help="Date de remplissage du formulaire"
    )
    birthdate = fields.Date(string="Date d'anniversaire")
    payment_date = fields.Date(string="Date de paiement")
    certificate_sent_date = fields.Date(string="Certificat envoyé le")
    fiscal_certificate_sent_date = fields.Date(
        string="Attestation fiscale envoyée le"
    )

    coop_number = fields.Integer(string="Coop N°")
    share_qty = fields.Integer(string="Nombre de part")

    share_amount = fields.Float(
        string="Montant", compute="_compute_share_amount"
    )

    gender = fields.Selection(
        [("female", "Féminin"), ("male", "Masculin"), ("other", "Autre")],
        string="Genre",
    )
    cooperator_type = fields.Selection(
        [
            ("share_a", "Part A"),
            ("share_b", "Part B"),
            ("share_c", "Part C"),
            ("share_d", "Part D"),
        ],
        string="Type de Part",
    )
    state_request = fields.Selection(
        [
            ("ok", "En ordre"),
            ("waiting_payment", "En attente de paiement"),
            ("certificate_to_send", "Certificat à envoyer"),
            ("resigning", "Parts revendues"),
        ]
    )  # TODO should we use the cooperative.status model instead?

    national_register_number = fields.Char(
        string="Numéro de registre national"
    )  # TODO add constraint / check consistancy
    share_numbers = fields.Char(string="Numéro de parts")
    payment_details = fields.Char(string="Détail de paiement")
    iban = fields.Char(string="IBAN")  # TODO remove. Temp for import purpose.
    comment_request = fields.Char(string="Commentaire")

    email_sent = fields.Boolean(string="Email envoyé")
    is_worker = fields.Boolean(
        compute="_compute_is_worker",
        search="_search_is_worker",
        string="is Worker",
        readonly=True,
        related="",
    )

    @api.depends("share_qty")
    def _compute_share_amount(self):
        for rec in self:
            rec.share_amount = (
                rec.share_qty * 25.0
            )  # TODO add ir.config_parameter to make this amount editable

    @api.depends("cooperator_type")
    def _compute_is_worker(self):
        for rec in self:
            rec.is_worker = rec.cooperator_type == "share_b"

    def _search_is_worker(self, operator, value):
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("cooperator_type", "=", "share_b")]
        else:
            return [("cooperator_type", "!=", "share_b")]
