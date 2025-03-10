from odoo.tests import common


class TestCategory(common.TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Category = self.env["volunteer.shift.category"]
        self.category1 = self.Category.create(
            {
                "name": "CategoryTest",
                "description": "Category pour autotests",
            }
        )

    def test_category_create(self):
        self.assertEqual(self.category1.name, "CategoryTest")
        self.assertEqual(self.category1.description, "Category pour autotests")
        self.assertEqual(self.category1.company_id, self.env.user.company_id)
