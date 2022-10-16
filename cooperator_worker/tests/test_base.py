# Copyright 2020 Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo.tests.common import SavepointCase


class TestWorkerBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        product_product_obj = cls.env["product.product"]
        share_line_obj = cls.env["share.line"]

        cls.share_x = product_product_obj.create(
            {
                "name": "Share X",
                "default_code": "share_x",
                "customer": True,
                "allow_working": True,
                "allow_shopping": True,
                "is_share": True,
            }
        )
        cls.share_y = product_product_obj.create(
            {
                "name": "Share Y",
                "default_code": "share_y",
                "customer": True,
                "allow_working": False,
                "allow_shopping": True,
                "is_share": True,
            }
        )
        cls.share_z = product_product_obj.create(
            {
                "name": "Share C",
                "default_code": "share_z",
                "customer": True,
                "allow_working": False,
                "allow_shopping": False,
                "is_share": True,
            }
        )

        cls.cooperator_x = cls.env["res.partner"].create(
            {
                "name": "cooperator 1",
            }
        )
        cls.cooperator_y = cls.env["res.partner"].create(
            {
                "name": "cooperator 2",
            }
        )
        cls.cooperator_z = cls.env["res.partner"].create(
            {
                "name": "cooperator 3",
            }
        )

        cls.share_line_coop_1 = share_line_obj.create(
            {
                "share_product_id": cls.share_x.id,
                "share_number": 2,
                "effective_date": date(2020, 1, 1),
                "partner_id": cls.cooperator_x.id,
            }
        )
        cls.share_line_coop_2 = share_line_obj.create(
            {
                "share_product_id": cls.share_y.id,
                "share_number": 4,
                "effective_date": date(2020, 1, 1),
                "partner_id": cls.cooperator_y.id,
            }
        )
        cls.share_line_coop_3 = share_line_obj.create(
            {
                "share_product_id": cls.share_z.id,
                "share_number": 6,
                "effective_date": date(2020, 1, 1),
                "partner_id": cls.cooperator_z.id,
            }
        )
