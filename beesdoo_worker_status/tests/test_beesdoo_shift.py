# Copyright 2019 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

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
            "beesdoo_shift.res_partner_worker_1_demo"
        )
        self.worker_regular_2 = self.env.ref(
            "beesdoo_shift.res_partner_worker_3_demo"
        )
        self.worker_regular_3 = self.env.ref(
            "beesdoo_shift.res_partner_worker_5_demo"
        )
        self.worker_irregular_1 = self.env.ref(
            "beesdoo_shift.res_partner_worker_2_demo"
        )
        self.worker_irregular_2 = self.env.ref(
            "beesdoo_shift.res_partner_worker_4_demo"
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

        self.exempt_reason_1 = self.env.ref(
            "beesdoo_shift.exempt_reason_1_demo"
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

    def test_postponed_alert_start_time_holiday_regular(self):
        """
        Check that alert_start_time is correctly postponed when
        worker take holiday.
        """
        status_id = self.worker_regular_1.cooperative_status_ids
        begin_date = date.today()
        status_id.today = begin_date

        status_id.sr = -1
        status_id.sc = -1
        first_alert_start_time = begin_date - timedelta(days=1)
        status_id.alert_start_time = first_alert_start_time
        self.assertEqual(status_id.status, "alert")

        # Set holiday
        status_id.write(
            {
                "holiday_start_time": begin_date + timedelta(days=5),
                "holiday_end_time": begin_date + timedelta(days=10),
            }
        )
        self.assertEqual(status_id.status, "alert")
        # Alert start time should no change yet
        self.assertEqual(status_id.alert_start_time, first_alert_start_time)

        # Now go in the future during the holiday period
        status_id.today = begin_date + timedelta(days=6)
        self.assertEqual(status_id.status, "holiday")
        # Alert start time should have changed
        self.assertEqual(
            status_id.alert_start_time,
            status_id.holiday_end_time,
        )

    def test_postponed_alert_start_time_holiday_irregular(self):
        """
        Check that alert_start_time is correctly postponed when
        worker take holiday.
        """
        status_id = self.worker_irregular_1.cooperative_status_ids
        begin_date = date.today()
        status_id.today = begin_date

        status_id.sr = -2
        first_alert_start_time = begin_date - timedelta(days=1)
        status_id.alert_start_time = first_alert_start_time
        self.assertEqual(status_id.status, "alert")

        # Set holiday
        status_id.write(
            {
                "holiday_start_time": begin_date + timedelta(days=5),
                "holiday_end_time": begin_date + timedelta(days=10),
            }
        )
        # Alert start time should no change yet
        self.assertEqual(
            status_id.alert_start_time, begin_date - timedelta(days=1)
        )

        # Now go in the future during the holiday period
        status_id.today = begin_date + timedelta(days=6)
        self.assertEqual(status_id.status, "holiday")
        # Alert start time should have changed
        self.assertEqual(
            status_id.alert_start_time,
            status_id.holiday_end_time,
        )

    def test_postponed_alert_start_time_exempted_regular(self):
        """
        Check that alert_start_time is correctly postponed when
        worker is exempted.
        """
        status_id = self.worker_regular_1.cooperative_status_ids
        begin_date = date.today()
        status_id.today = begin_date

        status_id.sr = -1
        status_id.sc = -1
        first_alert_start_time = begin_date - timedelta(days=1)
        status_id.alert_start_time = first_alert_start_time
        self.assertEqual(status_id.status, "alert")

        # Set exemption
        status_id.write(
            {
                "temporary_exempt_start_date": begin_date + timedelta(days=5),
                "temporary_exempt_end_date": begin_date + timedelta(days=10),
                "temporary_exempt_reason_id": self.exempt_reason_1.id,
            }
        )
        # Alert start time should no change yet
        self.assertEqual(
            status_id.alert_start_time, begin_date - timedelta(days=1)
        )

        # Now go in the future during the holiday period
        status_id.today = begin_date + timedelta(days=6)
        self.assertEqual(status_id.status, "exempted")
        # Alert start time should have changed
        self.assertEqual(
            status_id.alert_start_time,
            status_id.temporary_exempt_end_date,
        )

    def test_postponed_alert_start_time_exempted_irregular(self):
        """
        Check that alert_start_time is correctly postponed when
        worker is exempted.
        """
        status_id = self.worker_irregular_1.cooperative_status_ids
        begin_date = date.today()
        status_id.today = begin_date

        status_id.sr = -2
        first_alert_start_time = begin_date - timedelta(days=1)
        status_id.alert_start_time = first_alert_start_time
        self.assertEqual(status_id.status, "alert")

        # Set exemption
        status_id.write(
            {
                "temporary_exempt_start_date": begin_date + timedelta(days=5),
                "temporary_exempt_end_date": begin_date + timedelta(days=10),
                "temporary_exempt_reason_id": self.exempt_reason_1.id,
            }
        )
        # Alert start time should no change yet
        self.assertEqual(
            status_id.alert_start_time, begin_date - timedelta(days=1)
        )

        # Now go in the future during the holiday period
        status_id.today = begin_date + timedelta(days=6)
        self.assertEqual(status_id.status, "exempted")
        # Alert start time should have changed
        self.assertEqual(
            status_id.alert_start_time,
            status_id.temporary_exempt_end_date,
        )
