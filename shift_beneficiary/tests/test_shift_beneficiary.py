from odoo.addons.shift.tests.test_shift_common import TestShiftCommon
from odoo.addons.shift_beneficiary.controllers.main import WebsiteShiftController
from odoo.addons.website.tools import MockRequest


class TestShiftBeneficiary(TestShiftCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WebsiteShiftController = WebsiteShiftController()
        cls.website = cls.env["website"].browse(1)
        cls.task_template = cls.env.ref("shift.task_template_1_demo")
        cls.free_space = 100

    def test_get_selected_beneficiary_if_no_beneficiary(self):
        """if requestion.session["beneficiary"] is empty,
        returns res.partner model"""
        with MockRequest(self.env) as request:
            request.session["beneficiary"] = "1"
            selected_beneficiary = (
                self.WebsiteShiftController.get_selected_beneficiary()
            )
            self.assertEqual(selected_beneficiary, self.env["res.partner"].browse(1))

    def test_get_selected_beneficiary_if_beneficiary(self):
        """returns the record of the beneficiary from the id in
        requestion.session["beneficiary"]"""
        with MockRequest(self.env) as request:
            request.session["beneficiary"] = ""
            selected_beneficiary = (
                self.WebsiteShiftController.get_selected_beneficiary()
            )
            self.assertEqual(selected_beneficiary, self.env["res.partner"])

    def test_compute_display_shift_if_template_has_other_beneficiary(self):
        """only the shifts with beneficiary equals to the selected_beneficiary
        in request.session must be returned by
        filter_available_shift_irregular_worker"""
        with MockRequest(self.env, website=self.website) as request:
            request.session["beneficiary"] = "1"
            request.website.hide_rule = 0
            self.assertFalse(
                self.WebsiteShiftController.compute_display_shift(
                    self.free_space, self.task_template
                )
            )

    def test_compute_display_shift_template_has_correct_beneficiary(self):
        """only the shifts with beneficiary equals to the selected_beneficiary
        in request.session must be returned by
        filter_available_shift_irregular_worker"""
        self.task_template.beneficiary = self.env["res.partner"].browse(1)
        with MockRequest(self.env, website=self.website) as request:
            request.session["beneficiary"] = "1"
            request.website.hide_rule = 0
            self.assertTrue(
                self.WebsiteShiftController.compute_display_shift(
                    self.free_space, self.task_template
                )
            )

    def test_compute_display_shift_if_no_beneficiary(
        self,
    ):
        """if requestion.session["beneficiary"] is empty
        compute_display_shift should always return True"""
        with MockRequest(self.env, website=self.website) as request:
            request.session["beneficiary"] = ""
            request.website.hide_rule = 0
            self.assertTrue(
                self.WebsiteShiftController.compute_display_shift(
                    self.free_space, self.task_template
                )
            )
