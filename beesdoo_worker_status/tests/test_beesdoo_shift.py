# Copyright 2019 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBeesdooShift(TransactionCase):
    def setUp(self):
        super(TestBeesdooShift, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]

        self.current_time = datetime.now()
        self.user_admin = self.env.ref("base.user_root")

        self.worker_regular_1 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_6_demo"
        )
        self.worker_regular_2 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_5_demo"
        )
        self.worker_regular_3 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_3_demo"
        )
        self.worker_regular_super_1 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_1_demo"
        )
        self.worker_irregular_1 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_2_demo"
        )
        self.worker_irregular_2 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_4_demo"
        )

        self.task_type_1 = self.env.ref(
            "beesdoo_shift.beesdoo_shift_task_type_1_demo"
        )
        self.task_type_2 = self.env.ref(
            "beesdoo_shift.beesdoo_shift_task_type_2_demo"
        )
        self.task_type_3 = self.env.ref(
            "beesdoo_shift.beesdoo_shift_task_type_3_demo"
        )

        self.task_template_1 = self.env.ref(
            "beesdoo_worker_status.beesdoo_shift_task_template_1_demo"
        )
        self.task_template_2 = self.env.ref(
            "beesdoo_worker_status.beesdoo_shift_task_template_2_demo"
        )

        # Set time in and out of generation interval parameter
        self.start_in_1 = self.current_time + timedelta(seconds=2)
        self.end_in_1 = self.current_time + timedelta(minutes=10)
        self.start_in_2 = self.current_time + timedelta(minutes=9)
        self.end_in_2 = self.current_time + timedelta(minutes=21)
        self.start_out_1 = self.current_time - timedelta(minutes=50)
        self.end_out_1 = self.current_time - timedelta(minutes=20)
        self.start_out_2 = self.current_time + timedelta(minutes=40)
        self.end_out_2 = self.current_time + timedelta(minutes=50)

        self.shift_regular_regular_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
                "is_regular": True,
                "is_compensation": False,
            }
        )
        self.shift_regular_regular_2 = self.shift_model.create(
            {
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_regular_2.id,
                "start_time": self.start_out_1,
                "end_time": self.end_out_1,
                "is_regular": True,
                "is_compensation": False,
            }
        )
        self.shift_regular_regular_replaced_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_regular_3.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
                "is_regular": True,
                "is_compensation": False,
                "replaced_id": self.worker_regular_2.id,
            }
        )
        self.future_shift_regular = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_super_1.id,
                "start_time": self.start_in_2,
                "end_time": self.end_in_2,
                "is_regular": False,
                "is_compensation": True,
            }
        )
        self.shift_irregular_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_irregular_1.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
            }
        )
        self.shift_irregular_2 = self.shift_model.create(
            {
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_irregular_2.id,
                "start_time": self.start_out_2,
                "end_time": self.end_out_2,
            }
        )
        self.shift_empty_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
            }
        )

    def test_shift_counters(self):
        "Test shift counters calculation and cooperative status update"

        status_1 = self.worker_regular_1.cooperative_status_ids
        status_2 = self.worker_regular_3.cooperative_status_ids
        status_3 = self.worker_irregular_1.cooperative_status_ids

        shift_regular = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": datetime.now() - timedelta(minutes=50),
                "end_time": datetime.now() - timedelta(minutes=40),
                "is_regular": True,
                "is_compensation": False,
            }
        )
        future_shift_regular = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": datetime.now() + timedelta(minutes=20),
                "end_time": datetime.now() + timedelta(minutes=30),
                "is_regular": True,
                "is_compensation": False,
            }
        )
        shift_irregular = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_irregular_1.id,
                "start_time": datetime.now() - timedelta(minutes=15),
                "end_time": datetime.now() - timedelta(minutes=10),
            }
        )

        # For a regular worker
        status_1.sr = 0
        status_1.sc = 0
        self.assertEqual(status_1.status, "ok")
        shift_regular.state = "absent_1"
        self.assertEqual(status_1.sr, -1)
        self.assertEqual(status_1.status, "alert")
        shift_regular.state = "done"
        self.assertEquals(status_1.sr, 0)
        self.assertEquals(status_1.sc, 0)
        shift_regular.state = "open"
        shift_regular.write({"is_regular": False, "is_compensation": True})
        shift_regular.state = "done"
        self.assertEquals(status_1.sr, 1)
        self.assertEquals(status_1.sc, 0)

        # Check unsubscribed status
        status_1.sr = -1
        status_1.sc = -1

        # Subscribe him to another future shift
        future_shift_regular.worker_id = self.worker_regular_1
        with self.assertRaises(ValidationError) as e:
            future_shift_regular.state = "absent_2"
            self.assertIn("future", str(e.exception))
        status_1.sr = -2
        status_1.sc = -2
        self.assertEquals(status_1.status, "unsubscribed")

        # Should be unsubscribed from future shift
        self.assertFalse(future_shift_regular.worker_id)

        # With replacement worker (self.worker_regular_3)
        shift_regular.state = "open"
        status_1.sr = 0
        status_1.sc = 0
        status_2.sr = 0
        status_2.sc = 0
        shift_regular.replaced_id = self.worker_regular_3
        shift_regular.state = "absent_2"
        self.assertEqual(status_1.sr, 0)
        self.assertEqual(status_1.sc, 0)
        self.assertEqual(status_2.sr, -1)
        self.assertEqual(status_2.sc, -1)

        # For an irregular worker
        status_3.sr = 0
        status_3.sc = 0
        self.assertEqual(status_3.status, "ok")
        shift_irregular.state = "done"
        self.assertEqual(status_3.sr, 1)
        shift_irregular.state = "absent_2"
        self.assertEqual(status_3.sr, -1)
