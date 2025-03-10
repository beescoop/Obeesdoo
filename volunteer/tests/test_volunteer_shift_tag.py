from odoo.tests import common


class TestShift(common.TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Tag = self.env["volunteer.shift.tag"]
        self.tag1 = self.Tag.create(
            {
                "name": "TagTest",
                "description": "Tag pour autotests",
            }
        )

    def test_tag_create(self):
        self.assertEqual(self.tag1.name, "TagTest")
        self.assertEqual(self.tag1.description, "Tag pour autotests")
        self.assertEqual(self.tag1.company_id, self.env.user.company_id)
