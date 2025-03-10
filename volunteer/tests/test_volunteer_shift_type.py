from odoo.tests import common


class TestShift(common.TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.Type = self.env["volunteer.shift.type"]
        self.type1 = self.Type.create(
            {
                "name": "TypeTest",
                "description": "Type pour autotests",
            }
        )

    def test_type_create(self):
        self.assertEqual(self.type1.name, "TypeTest")
        self.assertEqual(self.type1.description, "Type pour autotests")
        self.assertEqual(self.type1.company_id, self.env.user.company_id)
