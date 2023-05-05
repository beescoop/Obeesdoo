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

    def test_filter_shift_by_structure_if_structure(self):
        """only the shifts with structure equals to the selected_structure
        in request.session must be returned by
        filter_available_shift_irregular_worker"""
        self._generate_shifts()
        with MockRequest(self.env, website=self.website) as request:
            shifts = self.WebsiteShiftController.get_future_shifts_with_no_worker()
            request.session["structure"] = "1"
            # shifts[0].structure = 
            subscribed_shifts = self.WebsiteShiftController.my_subscribed_shifts()
            highlight_rule_pc = request.website.highlight_rule_pc
            hide_rule = request.website.hide_rule / 100.0



    def test_filter_shift_by_structure_if_no_structure(self,):
        """if requestion.session["structure"] is empty
        filter_available_shift_irregular_worker should returns all shifts"""
        self._generate_shifts()
        with MockRequest(self.env, website=self.website) as request:
            request.session["structure"] = ""
            shifts = self.WebsiteShiftController.get_future_shifts_with_no_worker()
            subscribed_shifts = self.WebsiteShiftController.my_subscribed_shifts()
            highlight_rule_pc = request.website.highlight_rule_pc
            hide_rule = 0 # display all shifts
            displayed_shifts = self.WebsiteShiftController.filter_available_shift_irregular_worker(
                shifts,
                subscribed_shifts,
                highlight_rule_pc,
                hide_rule
            )
            self.assertEqual(len(displayed_shifts),len(shifts))
