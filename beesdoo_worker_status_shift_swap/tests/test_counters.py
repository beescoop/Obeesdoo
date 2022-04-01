from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestBeesdooWorkerStatusShiftSwap(TransactionCase):
    def setUp(self):
        super(TestBeesdooWorkerStatusShiftSwap, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.shift_template_dated_model = self.env["beesdoo.shift.template.dated"]
        self.shift_solidarity_offer_model = self.env["beesdoo.shift.solidarity.offer"]
        self.shift_solidarity_request_model = self.env[
            "beesdoo.shift.solidarity.request"
        ]

        self.current_time = datetime.now()
        self.user_admin = self.env.ref("base.user_root")

        self.worker_regular_1 = self.env.ref(
            "beesdoo_shift_swap.res_partner_worker_1_demo"
        )
        self.worker_irregular_1 = self.env.ref(
            "beesdoo_shift_swap.res_partner_worker_2_demo"
        )

        self.task_template_1 = self.env.ref("beesdoo_shift_swap.task_template_1_demo")
        self.task_template_2 = self.env.ref("beesdoo_shift_swap.task_template_2_demo")
        self.task_template_3 = self.env.ref("beesdoo_shift_swap.task_template_3_demo")

        self.task_type_1 = self.env.ref("beesdoo_shift.beesdoo_shift_task_type_1_demo")

        self.exempt_reason_1 = self.env.ref("beesdoo_shift.exempt_reason_1_demo")

    def test_counters_solidarity_request(self):
        """
        Test the personal counter updates when requesting a solidarity shift or
        cancelling a request
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": datetime.now() + timedelta(minutes=20),
                "store": True,
            }
        )

        shift_regular = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": template_dated.date,
                "end_time": template_dated.date + timedelta(minutes=10),
                "is_regular": True,
                "is_compensation": False,
            }
        )

        shift_irregular = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_irregular_1.id,
                "start_time": template_dated.date,
                "end_time": template_dated.date + timedelta(minutes=10),
                "is_regular": True,
                "is_compensation": False,
            }
        )

        # Solidarity request creation
        solidarity_request_regular = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated.id,
                "reason": "A good reason",
            }
        )

        self.worker_regular_1.cooperative_status_ids.sr = 0
        self.assertEqual(solidarity_request_regular.state, "validated")
        self.assertTrue(solidarity_request_regular.unsubscribe_shift_if_generated())
        self.assertFalse(shift_regular.worker_id)
        self.assertFalse(shift_regular.is_regular)
        self.assertEqual(self.worker_regular_1.cooperative_status_ids.sr, 0)

        solidarity_request_irregular = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_irregular_1.id,
                "tmpl_dated_id": template_dated.id,
                "reason": "A good reason",
            }
        )

        self.worker_irregular_1.cooperative_status_ids.sr = 0
        self.assertEqual(solidarity_request_irregular.state, "validated")
        self.assertTrue(solidarity_request_irregular.unsubscribe_shift_if_generated())
        self.assertFalse(shift_irregular.worker_id)
        self.assertFalse(shift_irregular.is_regular)
        self.assertEqual(self.worker_irregular_1.cooperative_status_ids.sr, 1)

        # Solidarity request cancellation
        self.worker_regular_1.cooperative_status_ids.sr = 0
        self.assertTrue(solidarity_request_regular.cancel_solidarity_request())
        self.assertEqual(shift_regular.worker_id.id, self.worker_regular_1.id)
        self.assertTrue(shift_regular.is_regular)
        self.assertFalse(solidarity_request_regular.subscribe_shift_if_generated())
        self.assertEqual(self.worker_regular_1.cooperative_status_ids.sr, 0)

        self.worker_irregular_1.cooperative_status_ids.sr = 1
        self.assertTrue(solidarity_request_irregular.cancel_solidarity_request())
        self.assertEqual(shift_irregular.worker_id.id, self.worker_irregular_1.id)
        self.assertTrue(shift_irregular.is_regular)
        self.assertFalse(solidarity_request_irregular.subscribe_shift_if_generated())
        self.assertEqual(self.worker_irregular_1.cooperative_status_ids.sr, 0)

    def test_counters_solidarity_offer(self):
        """
        Verify that the personal counter of an irregular worker is not
        incremented when doing a solidarity shift
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": datetime.now() - timedelta(minutes=30),
                "store": True,
            }
        )

        # Solidarity offer creation
        solidarity_offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_irregular_1.id,
                "tmpl_dated_id": template_dated.id,
            }
        )

        # Shift creation
        shift = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_irregular_1.id,
                "start_time": template_dated.date,
                "end_time": template_dated.date + timedelta(minutes=10),
                "is_regular": True,
                "is_compensation": False,
                "solidarity_offer_ids": [(6, 0, solidarity_offer.ids)],
            }
        )

        self.worker_irregular_1.cooperative_status_ids.sr = 0
        shift.state = "done"
        self.assertEqual(self.worker_irregular_1.cooperative_status_ids.sr, 0)
