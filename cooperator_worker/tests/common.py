# Copyright 2020 Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase

from odoo.addons.cooperator.tests.cooperator_test_mixin import CooperatorTestMixin


class TestWorkerBase(TransactionCase, CooperatorTestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.set_up_cooperator_test_data()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.share_x.write(
            {
                "allow_working": True,
                "allow_shopping": True,
            }
        )
        cls.share_y.write(
            {
                "allow_working": False,
                "allow_shopping": True,
            }
        )
        cls.cooperator_x = cls.env["res.partner"].create({"name": "cooperator y"})
        sr_share_x_vals = cls.get_dummy_subscription_requests_vals(
            partner_id=cls.cooperator_x.id,
            share_product_id=cls.share_x.id,
        )
        sr_share_x = cls.env["subscription.request"].create(sr_share_x_vals)
        cls.validate_subscription_request_and_pay(sr_share_x)

        cls.cooperator_y = cls.env["res.partner"].create({"name": "cooperator y"})
        sr_share_y_vals = cls.get_dummy_subscription_requests_vals(
            partner_id=cls.cooperator_y.id,
            share_product_id=cls.share_y.id,
        )
        sr_share_y = cls.env["subscription.request"].create(sr_share_y_vals)
        cls.validate_subscription_request_and_pay(sr_share_y)
