from odoo.tests import common
from odoo.tools.safe_eval import datetime

from ..models.volunteer_shift import _convert_naive_to_str_aware_date


class TestShift(common.TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Shift = self.env["volunteer.shift"]
        self.Type = self.env["volunteer.shift.type"]
        self.type1 = self.Type.create(
            {
                "name": "TypeTest",
                "description": "Type pour autotests",
            }
        )
        self.Tag = self.env["volunteer.shift.tag"]
        self.tag1 = self.Tag.create(
            {
                "name": "TagTest",
                "description": "Tag pour autotests",
            }
        )
        self.Category = self.env["volunteer.shift.category"]
        self.category1 = self.Category.create(
            {
                "name": "CategoryTest",
                "description": "Category pour autotests",
            }
        )
        self.shift_default = self.Shift.create(
            {
                "name": "Test",
                "start_time": datetime.datetime(2025, 12, 24, 10, 5),
                "end_time": datetime.datetime(2025, 12, 24, 12, 5),
                "type_id": self.type1.id,
                "tag_ids": [self.tag1.id],
                "category_id": self.category1.id,
            }
        )
        self.shift1 = self.Shift.create(
            {
                "name": "Test",
                "state": "canceled",
                "start_time": datetime.datetime(2025, 12, 24, 10, 5),
                "end_time": datetime.datetime(2025, 12, 24, 12, 5),
                "timezone": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
                "tag_ids": [self.tag1.id],
                "category_id": self.category1.id,
            }
        )

    def test_shift_create(self):
        self.assertEqual(self.shift1.name, "Test")
        self.assertEqual(self.shift1.state, "canceled")
        self.assertEqual(self.shift1.timezone, "Europe/Brussels")
        self.assertEqual(self.shift1.max_volunteer_nb, 2)
        self.assertEqual(self.shift1.company_id, self.env.user.company_id)

    def test_shift_create_default_values(self):
        self.assertEqual(self.shift_default.name, "Test")
        self.assertEqual(self.shift_default.state, "draft")
        self.assertEqual(self.shift_default.timezone, self.env.user.tz)
        self.assertEqual(self.shift_default.max_volunteer_nb, 1)
        self.assertEqual(self.shift_default.company_id, self.env.user.company_id)

    def test_shift_relations(self):
        self.assertEqual(self.shift_default.type_id.name, "TypeTest")
        self.assertEqual(self.shift_default.tag_ids.name, "TagTest")
        self.assertEqual(self.shift_default.category_id.name, "CategoryTest")

    def test_shift_time_values(self):
        self.assertEqual(
            self.shift_default.start_time, datetime.datetime(2025, 12, 24, 10, 5)
        )
        self.assertEqual(
            self.shift_default.end_time, datetime.datetime(2025, 12, 24, 12, 5)
        )

    def test_convert_naive_date(self):
        aware_date = _convert_naive_to_str_aware_date(
            self.shift_default.start_time, "Europe/Brussels", "%Y/%m/%d_%H:%M"
        )
        self.assertEqual(aware_date, "2025/12/24_11:05")

        ###########################################
        #       Test Computed field name          #
        #       Work in Progress for addition     #
        #       in a future another modules       #
        ###########################################

    # def test_shift_compute_name_custom_tz(self):
    #     formated_start_time = _convert_naive_to_str_aware_date(
    #         self.shift1.start_time, "Europe/Brussels", "%Y/%m/%d_%H:%M"
    #     )
    #     formated_end_time = _convert_naive_to_str_aware_date(
    #         self.shift1.end_time, "Europe/Brussels", "%H:%M"
    #     )
    #     self.assertEqual(
    #         self.shift1.name,
    #         f"{formated_start_time}-{formated_end_time}_CategoryTest_TypeTest",
    #     )
    #
    # def test_shift_compute_name_default_tz(self):
    #     start_time = datetime.datetime(2025, 12, 24, 10, 5).astimezone(
    #         pytz.timezone(self.shift_default.timezone)
    #     )
    #     formated_start_time = datetime.datetime.strftime(start_time, "%Y/%m/%d_%H:%M")
    #     end_time = datetime.datetime(2025, 12, 24, 12, 5).astimezone(
    #         pytz.timezone(self.shift_default.timezone)
    #     )
    #     formated_end_time = datetime.datetime.strftime(end_time, "%H:%M")
    #     self.assertEqual(
    #         self.shift_default.name,
    #         f"{formated_start_time}-{formated_end_time}_CategoryTest_TypeTest",
    #     )
