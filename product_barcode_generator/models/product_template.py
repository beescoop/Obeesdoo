# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import uuid

from odoo import api, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def generate_barcode(self):
        self.ensure_one()
        if self.to_weight:
            seq_internal_code = self.env.ref(
                "product_barcode_generator.seq_ean_product_internal_ref"
            )
            bc = ""
            if not self.default_code:
                rule = self.env.ref("pos_price_to_weight.rule_price_to_weight")
                default_code = seq_internal_code.next_by_id()
                while self.search_count([("default_code", "=", default_code)]) > 1:
                    default_code = seq_internal_code.next_by_id()
                self.default_code = default_code
            ean = "02" + self.default_code[0:5] + "000000"
            bc = ean[0:12] + str(self.env["barcode.nomenclature"].ean_checksum(ean))
        else:
            rule = self.env.ref(
                "product_barcode_generator.product_barcode_generator_rule"
            )
            size = 13 - len(rule.pattern)
            ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
            bc = ean[0:12] + str(self.env["barcode.nomenclature"].ean_checksum(ean))
            # Make sure there is no other active member with the same barcode
            while self.search_count([("barcode", "=", bc)]) > 1:
                ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
                bc = ean[0:12] + str(self.env["barcode.nomenclature"].ean_checksum(ean))
        _logger.info("barcode :", bc)
        self.barcode = bc
