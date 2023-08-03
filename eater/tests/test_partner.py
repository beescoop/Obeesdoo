from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.worker_1 = cls.env["res.partner"].create(
            {
                "name": "Worker 1",
                "eater": "worker_eater",
            }
        )
        cls.worker_2 = cls.env["res.partner"].create(
            {
                "name": "Worker 2",
                "eater": "worker_eater",
            }
        )
        cls.eater_1 = cls.env["res.partner"].create(
            {
                "name": "Eater 1",
                "eater": "eater",
            }
        )
        cls.eater_2 = cls.env["res.partner"].create(
            {
                "name": "Eater 2",
                "eater": "eater",
            }
        )

    def test_eater_not_parent_of_worker_eater(self):
        with self.assertRaises(ValidationError):
            self.worker_1.parent_eater_id = self.eater_1

    def test_worker_eater_not_child_of_eater(self):
        with self.assertRaises(ValidationError):
            self.eater_1.child_eater_ids = self.worker_1

    def test_eater_not_parent_of_eater(self):
        with self.assertRaises(ValidationError):
            self.eater_1.parent_eater_id = self.eater_2

    def test_worker_eater_no_parent(self):
        with self.assertRaises(ValidationError):
            self.worker_2.parent_eater_id = self.worker_1

    def test_no_parent_of_self(self):
        with self.assertRaises(ValidationError):
            self.worker_2.parent_eater_id = self.worker_2

    def test_worker_eater_parent_of_eater(self):
        self.eater_1.parent_eater_id = self.worker_1
