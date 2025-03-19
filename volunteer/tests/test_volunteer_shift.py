from odoo.tests import common
from odoo.tools.safe_eval import datetime


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
