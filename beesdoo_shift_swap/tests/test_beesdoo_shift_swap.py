from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestBeesdooShiftSwap(TransactionCase):
    def setUp(self):
        super(TestBeesdooShiftSwap, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.shift_template_dated_model = self.env["beesdoo.shift.template.dated"]
        self.shift_solidarity_offer_model = self.env["beesdoo.shift.solidarity.offer"]
        self.shift_solidarity_request_model = self.env[
            "beesdoo.shift.solidarity.request"
        ]

        self.now = datetime.now()
        self.user_admin = self.env.ref("base.user_root")

        self.worker_regular_1 = self.env.ref("beesdoo_shift.res_partner_worker_1_demo")
        self.worker_irregular_1 = self.env.ref(
            "beesdoo_shift.res_partner_worker_2_demo"
        )

        self.task_template_1 = self.env.ref("beesdoo_shift_swap.task_template_1_demo")
        self.task_template_2 = self.env.ref("beesdoo_shift_swap.task_template_2_demo")
        self.task_template_3 = self.env.ref("beesdoo_shift_swap.task_template_3_demo")

        self.task_type_1 = self.env.ref("beesdoo_shift.beesdoo_shift_task_type_1_demo")

        self.exempt_reason_1 = self.env.ref("beesdoo_shift.exempt_reason_1_demo")

    def test_solidarity_offer_if_shift_generated(self):
        """
        Test solidarity shift offer creation and cancellation if the related shift
        is already generated
        Test also the control of the date when trying to cancel a solidarity offer
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.now + timedelta(minutes=20),
                "store": True,
            }
        )

        shift = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_template_1.task_type_id.id,
                "worker_id": None,
                "start_time": template_dated.date,
                "end_time": template_dated.date + timedelta(minutes=10),
                "is_regular": False,
                "is_compensation": False,
            }
        )

        # Solidarity offer creation
        solidarity_offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated.id,
            }
        )

        self.assertEqual(solidarity_offer.state, "validated")

        self.assertEqual(solidarity_offer.shift_id.id, shift.id)
        self.assertEqual(solidarity_offer.id, shift.solidarity_offer_ids[0].id)

        self.assertEqual(shift.worker_id.id, self.worker_regular_1.id)
        self.assertTrue(shift.is_regular)
        self.assertTrue(shift.is_solidarity)

        # Solidarity offer cancellation
        self.assertTrue(solidarity_offer.check_offer_date_too_close())
        template_dated.date = self.now + timedelta(days=30)
        shift.start_time = template_dated.date
        shift.end_time = template_dated.date + timedelta(minutes=10)
        self.assertFalse(solidarity_offer.check_offer_date_too_close())
        self.assertTrue(solidarity_offer.cancel_solidarity_offer())

        self.assertFalse(solidarity_offer.shift_id)
        self.assertFalse(shift.solidarity_offer_ids)
        self.assertFalse(shift.worker_id.id)
        self.assertFalse(shift.is_regular)
        self.assertFalse(shift.is_solidarity)

    def test_solidarity_offer_if_shift_not_generated(self):
        """
        Test solidarity shift offer creation and cancellation if the
        related shift is not already generated
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.task_template_1.start_date,
                "store": True,
            }
        )

        # Solidarity offer creation
        solidarity_offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated.id,
            }
        )

        self.assertEqual(solidarity_offer.state, "validated")
        self.assertFalse(solidarity_offer.shift_id)

        # Generate the shifts
        shifts = self.task_template_1.generate_task_day()
        shift = shifts[0]

        self.assertEqual(solidarity_offer.shift_id.id, shift.id)
        self.assertEqual(solidarity_offer.id, shift.solidarity_offer_ids.id)

        self.assertEqual(shift.worker_id.id, self.worker_regular_1.id)
        self.assertTrue(shift.is_regular)
        self.assertTrue(shift.is_solidarity)

        # Solidarity offer cancellation
        self.assertTrue(solidarity_offer.cancel_solidarity_offer())

        self.assertFalse(solidarity_offer.shift_id)
        self.assertFalse(shift.solidarity_offer_ids)
        self.assertFalse(shift.worker_id.id)
        self.assertFalse(shift.is_regular)
        self.assertFalse(shift.is_solidarity)

    def test_solidarity_request_if_shift_generated(self):
        """
        Test solidarity shift request creation and cancellation if the related shift
        is already generated
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.now + timedelta(minutes=20),
                "store": True,
            }
        )

        shift = self.shift_model.create(
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

        # Solidarity offer creation
        solidarity_request_regular = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated.id,
                "reason": "A good reason",
            }
        )

        self.assertEqual(solidarity_request_regular.state, "validated")
        self.assertFalse(shift.worker_id)
        self.assertFalse(shift.is_regular)

        # Solidarity offer cancellation
        self.assertTrue(solidarity_request_regular.cancel_solidarity_request())
        self.assertEqual(shift.worker_id.id, self.worker_regular_1.id)
        self.assertTrue(shift.is_regular)
        self.assertFalse(solidarity_request_regular.cancel_solidarity_request())

    def test_solidarity_request_if_shift_not_generated(self):
        """
        Test solidarity shift request creation and cancellation if the
        related shift is not already generated
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_2.id,
                "date": self.task_template_2.start_date,
                "store": True,
            }
        )

        # Solidarity offer creation
        solidarity_request_regular = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated.id,
                "reason": "A good reason",
            }
        )

        solidarity_request_irregular = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_irregular_1.id,
                "tmpl_dated_id": False,
                "reason": "A good reason",
            }
        )

        self.assertEqual(solidarity_request_regular.state, "validated")
        self.assertEqual(solidarity_request_irregular.state, "validated")

        # Generate the shifts
        shifts = self.task_template_2.generate_task_day()
        shift_regular = shifts[0]

        self.assertFalse(shift_regular.worker_id)
        self.assertFalse(shift_regular.is_regular)

        # Solidarity offer cancellation
        self.assertTrue(solidarity_request_regular.cancel_solidarity_request())
        self.assertEqual(solidarity_request_regular.state, "cancelled")
        self.assertEqual(shift_regular.worker_id.id, self.worker_regular_1.id)
        self.assertTrue(shift_regular.is_regular)
        self.assertFalse(solidarity_request_regular.cancel_solidarity_request())

        self.assertTrue(solidarity_request_irregular.cancel_solidarity_request())
        self.assertEqual(solidarity_request_irregular.state, "cancelled")
        self.assertFalse(solidarity_request_irregular.cancel_solidarity_request())

    def test_shift_creation_when_cancelling_solidarity_request(self):
        """
        Test the shift creation in the (unusual) case where a worker wants to
        cancel a solidarity request but all the shifts in the timeslot were
        taken in the meantime
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_3.id,
                "date": self.task_template_3.start_date,
                "store": True,
            }
        )

        # Generate a shift
        shifts = self.task_template_3.generate_task_day()
        shift = shifts[0]

        solidarity_request = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated.id,
                "reason": "A good reason",
            }
        )

        self.assertFalse(shift.worker_id)
        self.assertFalse(shift.is_regular)

        # Fill the shift with another worker
        shift.write(
            {
                "is_regular": True,
                "worker_id": self.worker_irregular_1.id,
            }
        )

        self.assertTrue(solidarity_request.cancel_solidarity_request())
        shifts = self.env["beesdoo.shift.shift"].search(
            [
                ("start_time", "=", template_dated.date),
                ("task_template_id", "=", self.task_template_3.id),
            ],
        )
        self.assertEqual(shifts[1].worker_id.id, self.worker_regular_1.id)
        self.assertTrue(shifts[1].is_regular)

    def test_solidarity_counter(self):
        """
        Test the update of the global solidarity counter
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.now - timedelta(minutes=30),
                "store": True,
            }
        )

        shift = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": None,
                "start_time": template_dated.date,
                "end_time": template_dated.date + timedelta(minutes=10),
                "is_regular": False,
                "is_compensation": False,
            }
        )

        # Solidarity offer creation
        self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated.id,
            }
        )

        start_value = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.solidarity_counter_start_value")
        )

        self.assertEqual(
            self.env["res.company"]._company_default_get().solidarity_counter(),
            start_value,
        )
        shift.state = "done"
        self.assertEqual(
            self.env["res.company"]._company_default_get().solidarity_counter(),
            start_value + 1,
        )

        template_dated_2 = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_2.id,
                "date": datetime.now() + timedelta(minutes=20),
                "store": True,
            }
        )

        solidarity_request = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "tmpl_dated_id": template_dated_2.id,
                "reason": "A good reason",
            }
        )

        self.assertEqual(
            self.env["res.company"]._company_default_get().solidarity_counter(),
            start_value,
        )
        solidarity_request.state = "cancelled"
        self.assertEqual(
            self.env["res.company"]._company_default_get().solidarity_counter(),
            start_value + 1,
        )
