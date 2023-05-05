from odoo.addons.shift_structure.controllers.main import WebsiteShiftController
from odoo.addons.shift.tests.test_shift_common import TestShiftCommon
from odoo.addons.website.tools import MockRequest
from odoo.fields import Datetime

class TestShiftStructure(TestShiftCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WebsiteShiftController = WebsiteShiftController()
        cls.website = cls.env['website'].browse(1)
        cls.task_template = cls.env.ref("shift.task_template_1_demo")
        cls.free_space = 100

    def test_get_selected_structure_if_no_structure(self):
        """if requestion.session["structure"] is empty,
        returns res.partner model"""
        with MockRequest(self.env) as request:
            request.session["structure"] = "1"
            selected_structure = self.WebsiteShiftController.get_selected_structure()
            self.assertEqual(selected_structure, self.env["res.partner"].browse(1))


    def test_get_selected_structure_if_structure(self):
        """returns the record of the structure from the id in 
        requestion.session["structure"]"""
        with MockRequest(self.env) as request:
            request.session["structure"] = ""
            selected_structure = self.WebsiteShiftController.get_selected_structure()
            self.assertEqual(selected_structure, self.env["res.partner"])

    def test_compute_display_shift_if_template_has_other_structure(self):
        """only the shifts with structure equals to the selected_structure
        in request.session must be returned by
        filter_available_shift_irregular_worker"""
        with MockRequest(self.env, website=self.website) as request:
            request.session["structure"] = "1"
            request.website.hide_rule = 0
            self.assertFalse(
                self.WebsiteShiftController.compute_display_shift(
                    self.free_space,
                    self.task_template
                    )
                )

    def test_compute_display_shift_template_has_correct_structure(self):
        """only the shifts with structure equals to the selected_structure
        in request.session must be returned by
        filter_available_shift_irregular_worker"""
        self.task_template.structure = self.env['res.partner'].browse(1)
        with MockRequest(self.env, website=self.website) as request:
            request.session["structure"] = "1"
            request.website.hide_rule = 0
            self.assertTrue(
                self.WebsiteShiftController.compute_display_shift(
                    self.free_space,
                    self.task_template
                    )
                )


    def test_compute_display_shift_if_no_structure(self,):
        """if requestion.session["structure"] is empty
        compute_display_shift should always return True"""
        with MockRequest(self.env, website=self.website) as request:
            request.session["structure"] = ""
            request.website.hide_rule = 0
            self.assertTrue(
                self.WebsiteShiftController.compute_display_shift(
                    self.free_space,
                    self.task_template
                    )
                )
