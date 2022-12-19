from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase


class TestBeesdooShiftSwap(TransactionCase):
    def setUp(self):
        super(TestBeesdooShiftSwap, self).setUp()
        self.shift_model = self.env["shift.shift"]
        self.shift_template_model = self.env["shift.template"]
        self.shift_template_dated_model = self.env["beesdoo.shift.template.dated"]
        self.shift_solidarity_offer_model = self.env["beesdoo.shift.solidarity.offer"]
        self.shift_solidarity_request_model = self.env[
            "beesdoo.shift.solidarity.request"
        ]
        self.shift_swap_model = self.env["beesdoo.shift.swap"]
        self.exchange_request_model = self.env["beesdoo.shift.exchange_request"]
        self.exchange_model = self.env["beesdoo.shift.exchange"]

        self.now = datetime.now()
        self.user_admin = self.env.ref("base.user_root")

        self.worker_regular_1 = self.env.ref("beesdoo_shift.res_partner_worker_1_demo")
        self.worker_regular_2 = self.env.ref("beesdoo_shift.res_partner_worker_3_demo")
        self.worker_irregular_1 = self.env.ref(
            "beesdoo_shift.res_partner_worker_2_demo"
        )

        self.task_template_1 = self.env.ref("beesdoo_shift_swap.task_template_1_demo")
        self.task_template_2 = self.env.ref("beesdoo_shift_swap.task_template_2_demo")
        self.task_template_3 = self.env.ref("beesdoo_shift_swap.task_template_3_demo")

        self.task_type_1 = self.env.ref("beesdoo_shift.beesdoo_shift_task_type_1_demo")

        self.exempt_reason_1 = self.env.ref("beesdoo_shift.exempt_reason_1_demo")

        # Set context to avoid shift generation in the past
        self.env.context = dict(self.env.context, visualize_date=date.today())

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
        self.env["ir.config_parameter"].sudo().set_param("min_hours_to_unsubscribe", 2)
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
        # Setting "visualize_date" to avoid generating a shift in the past
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.task_template_1.start_date,
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
        self.env["ir.config_parameter"].sudo().set_param("min_hours_to_unsubscribe", 0)
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

        self.assertNotIn(self.worker_regular_1.id, self.get_worker_ids(shifts))

        # Set template and shift date in the future to enable cancellation
        template_dated.date = self.now + timedelta(days=30)
        for s in shifts:
            s.start_time = template_dated.date
            s.end_time = template_dated.date + timedelta(minutes=10)

        # Solidarity request cancellation
        self.assertTrue(solidarity_request_regular.cancel_solidarity_request())
        self.assertEqual(solidarity_request_regular.state, "cancelled")
        self.assertIn(self.worker_regular_1.id, self.get_worker_ids(shifts))
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
        self.task_template_3.start_date = self.now + timedelta(minutes=20)

        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_3.id,
                "date": self.task_template_3.start_date,
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

        # Set template and shift date in the future to enable cancellation
        template_dated.date = self.now + timedelta(days=30)
        for s in shifts:
            s.start_time = template_dated.date
            s.end_time = template_dated.date + timedelta(minutes=10)

        self.assertTrue(solidarity_request.cancel_solidarity_request())
        shifts = self.shift_model.search(
            [
                ("start_time", "=", template_dated.date),
                ("task_template_id", "=", self.task_template_3.id),
            ],
        )
        self.assertIn(self.worker_regular_1.id, self.get_worker_ids(shifts))

    def test_solidarity_counter(self):
        """
        Test the update of the global solidarity counter
        """
        template_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.now - timedelta(minutes=30),
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

    def test_shift_swap(self):
        """
        Test swapping between generated shifts
        """
        exchanged_tmpl_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.now + timedelta(minutes=20),
            }
        )

        wanted_tmpl_dated = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_2.id,
                "date": self.now + timedelta(minutes=20),
            }
        )

        exchanged_shift = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_template_1.task_type_id.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": exchanged_tmpl_dated.date,
                "end_time": exchanged_tmpl_dated.date + timedelta(minutes=10),
                "is_regular": True,
                "is_compensation": False,
            }
        )

        wanted_shift = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_template_2.task_type_id.id,
                "worker_id": None,
                "start_time": wanted_tmpl_dated.date,
                "end_time": wanted_tmpl_dated.date + timedelta(minutes=10),
                "is_regular": False,
                "is_compensation": False,
            }
        )

        self.shift_swap_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "exchanged_tmpl_dated_id": exchanged_tmpl_dated.id,
                "wanted_tmpl_dated_id": wanted_tmpl_dated.id,
            }
        )

        self.assertFalse(exchanged_shift.worker_id)
        self.assertFalse(exchanged_shift.is_regular)

        self.assertEqual(wanted_shift.worker_id, self.worker_regular_1)
        self.assertTrue(wanted_shift.is_regular)

    def test_shift_exchange(self):
        """
        Test a shift exchange between generated shifts
        """
        tmpl_dated_1 = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_1.id,
                "date": self.now + timedelta(minutes=20),
            }
        )

        tmpl_dated_2 = self.shift_template_dated_model.create(
            {
                "template_id": self.task_template_2.id,
                "date": self.now + timedelta(minutes=20),
            }
        )

        shift_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_template_1.task_type_id.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": tmpl_dated_1.date,
                "end_time": tmpl_dated_1.date + timedelta(minutes=10),
                "is_regular": True,
                "is_compensation": False,
            }
        )

        shift_2 = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_template_2.task_type_id.id,
                "worker_id": self.worker_regular_2.id,
                "start_time": tmpl_dated_2.date,
                "end_time": tmpl_dated_2.date + timedelta(minutes=10),
                "is_regular": False,
                "is_compensation": False,
            }
        )

        exchange_request_1 = self.exchange_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "exchanged_tmpl_dated_id": tmpl_dated_1.id,
                "asked_tmpl_dated_ids": [(6, False, tmpl_dated_2.ids)],
            }
        )

        self.assertEqual(exchange_request_1.status, "no_match")

        exchange_request_2 = self.exchange_request_model.create(
            {
                "worker_id": self.worker_regular_2.id,
                "exchanged_tmpl_dated_id": tmpl_dated_2.id,
                "asked_tmpl_dated_ids": [(6, False, tmpl_dated_1.ids)],
                "validate_request_id": exchange_request_1.id,
            }
        )

        self.assertEqual(exchange_request_2.status, "awaiting_validation")
        self.assertEqual(exchange_request_1.status, "has_match")

        exchange = self.exchange_model.create(
            {
                "first_request_id": exchange_request_1.id,
                "second_request_id": exchange_request_2.id,
            }
        )

        self.assertEqual(exchange_request_1.status, "done")
        self.assertEqual(exchange_request_1.validate_request_id, exchange_request_2)
        self.assertEqual(exchange_request_1.exchange_id, exchange)

        self.assertEqual(exchange_request_2.status, "done")
        self.assertEqual(exchange_request_2.validate_request_id, exchange_request_1)
        self.assertEqual(exchange_request_2.exchange_id, exchange)

        self.assertEqual(shift_1.worker_id, self.worker_regular_2)
        self.assertEqual(shift_2.worker_id, self.worker_regular_1)

    def get_worker_ids(self, shifts):
        shifts_worker_ids = []
        for s in shifts:
            shifts_worker_ids.append(s.worker_id.id)
        return shifts_worker_ids
