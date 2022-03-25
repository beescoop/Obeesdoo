# Copyright 2021 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBeesdooShift(TransactionCase):
    def setUp(self):
        super(TestBeesdooShift, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.subscribe_wizard = self.env["beesdoo.shift.subscribe"]
        self.holiday_wizard = self.env["beesdoo.shift.holiday"]
        self.exemption_wizard = self.env["beesdoo.shift.temporary_exemption"]

        self.current_time = datetime.now()
        self.user_admin = self.env.ref("base.user_root")

        self.worker_regular_1 = self.env.ref("beesdoo_shift.res_partner_worker_1_demo")
        self.worker_irregular_2 = self.env.ref(
            "beesdoo_shift.res_partner_worker_2_demo"
        )
        self.worker_regular_3 = self.env.ref("beesdoo_shift.res_partner_worker_3_demo")
        self.worker_regular_5 = self.env.ref("beesdoo_shift.res_partner_worker_5_demo")
        self.worker_regular_6 = self.env.ref("beesdoo_shift.res_partner_worker_6_demo")

        self.planning_1 = self.env.ref("beesdoo_shift.beesdoo_shift_planning_1_demo")

        self.task_template_1 = self.env.ref("beesdoo_shift.task_template_1_demo")
        self.task_template_2 = self.env.ref("beesdoo_shift.task_template_2_demo")
        self.task_template_3 = self.env.ref("beesdoo_shift.task_template_3_demo")

        self.exempt_reason_1 = self.env.ref("beesdoo_shift.exempt_reason_1_demo")

    def _generate_shifts(self, days=0, nb=1):
        """
        Run _generate_next_planning *nb* times beginning from today - *days*.
        """
        planning_cls = self.env["beesdoo.shift.planning"]
        begin_date = date.today() - timedelta(days=days)
        self.env["ir.config_parameter"].set_param("last_planning_seq", 0)
        for i in range(nb):
            # The following line is a hack to make planning last 7 days.
            # This will not be necessary when the PR will be merged:
            # https://github.com/beescoop/Obeesdoo/pull/207
            # After the merge, the next_planning_date should be set only
            # once at the beginning with last_planning_seq
            self.env["ir.config_parameter"].set_param(
                "next_planning_date",
                (begin_date + timedelta(days=i * 7)).isoformat(),
            )
            # Generate the planning
            planning_cls._generate_next_planning()

    def _count_number_of_shift(self, worker_id):
        """Count number of shift for a worker."""
        return self.shift_model.search_count([("worker_id", "=", worker_id.id)])

    def test_unsubscribe_worker_from_task_template_1(self):
        """
        Check that removing a worker from a task_template via the
        task_template remove the worker from the already generated
        shifts.
        """
        self._generate_shifts(days=1, nb=2)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 2)

        # Unsubscribe a worker from the task template
        self.task_template_1.worker_ids -= self.worker_regular_1

        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 1)

        # Subscribe a worker from the task template
        self.task_template_1.worker_ids += self.worker_regular_1

        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 2)

    def test_unsubscribe_worker_from_task_template_2(self):
        """
        Check that removing a worker from a task_template via the
        res_partner remove the worker from the already generated
        shifts.
        """
        self._generate_shifts(days=1, nb=2)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 2)

        # Unsubscribe a worker from the task template
        self.worker_regular_1.subscribed_shift_ids -= self.task_template_1

        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 1)

        # Subscribe a worker from the task template
        self.worker_regular_1.subscribed_shift_ids += self.task_template_1

        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 2)

    def test_subscribe_worker_from_task_template_with_shifts_1(self):
        """
        Check that adding a worker to a task_template via the
        task_template add the worker to already generated shifts.

        The task template has enough place. So there is empty generated
        shift where the new worker can be subscribed.
        """
        self._generate_shifts(days=1, nb=2)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_5), 2)

        self.task_template_1.worker_ids += self.worker_regular_5

        self.assertEqual(self._count_number_of_shift(self.worker_regular_5), 3)

    def test_subscribe_worker_from_task_template_whitout_shifts_1(self):
        """
        Check that adding a worker to a task_template via the
        task_template add the worker to already generated shifts.

        The task template is full. So there is no empty generated
        shift where the new worker can be subscribed.
        """
        self.task_template_1.worker_nb = 2
        self._generate_shifts(days=1, nb=2)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_5), 2)

        # Open a place for the new worker
        self.task_template_1.worker_nb = 3
        self.task_template_1.worker_ids += self.worker_regular_5

        self.assertEqual(self._count_number_of_shift(self.worker_regular_5), 3)

    def test_change_working_mode_1(self):
        """
        Check that changing a regular worker to irregular via the wizard
        removes the worker from the already generated shifts.
        """
        self._generate_shifts(days=1, nb=2)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 2)

        subscribe_wiz = self.subscribe_wizard.with_context(
            {"active_id": self.worker_regular_1.ids}
        )
        subscribe_wiz = subscribe_wiz.create({"working_mode": "irregular"})
        subscribe_wiz.subscribe()

        self.assertTrue(self.worker_regular_1 not in self.task_template_1.worker_ids)
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 1)

    def test_change_worker_holiday_1(self):
        """
        Change the holiday start and end time on a cooperative_status.
        Check that worker is correctly unsbscribed or subscribed again
        to already generated shifts.
        """
        self._generate_shifts(days=7, nb=5)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        status_id = self.worker_regular_1.cooperative_status_ids
        status_id.today = date.today()

        # Set holiday in the past do not change shift for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (status_id.today - timedelta(days=7)).isoformat(),
                "holiday_end_time": (status_id.today - timedelta(days=1)).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        # Set holiday in the future change shift for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (status_id.today + timedelta(days=1)).isoformat(),
                "holiday_end_time": (status_id.today + timedelta(days=13)).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that beginning holiday later in the future change shift
        # for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (
                    status_id.today + timedelta(days=14)
                ).isoformat(),
                "holiday_end_time": (status_id.today + timedelta(days=20)).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that shorten the holiday in the future change shift
        # for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (status_id.today + timedelta(days=1)).isoformat(),
                "holiday_end_time": (status_id.today + timedelta(days=13)).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

    def test_change_worker_holiday_2(self):
        """
        Change the holiday start and end time on a cooperative_status.
        Check that worker is correctly unsbscribed or subscribed again
        to already generated shifts.

        This test uses the wizard.
        """
        self._generate_shifts(days=7, nb=5)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        holiday_wiz = self.holiday_wizard.with_context(
            {"active_id": self.worker_regular_1.ids}
        )
        status_id = self.worker_regular_1.cooperative_status_ids
        status_id.today = date.today()

        # Set holiday in the past raise error and do not change shift
        # for worker_1
        holiday_wiz = holiday_wiz.create(
            {
                "holiday_start_day": (status_id.today - timedelta(days=7)).isoformat(),
                "holiday_end_day": (status_id.today - timedelta(days=1)).isoformat(),
            }
        )
        with self.assertRaises(ValidationError):
            holiday_wiz.holidays()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        # Set holiday in the future change shift for worker_1
        holiday_wiz = holiday_wiz.create(
            {
                "holiday_start_day": (status_id.today + timedelta(days=1)).isoformat(),
                "holiday_end_day": (status_id.today + timedelta(days=13)).isoformat(),
            }
        )
        holiday_wiz.holidays()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that beginning holiday later in the future change shift
        # for worker_1
        holiday_wiz = holiday_wiz.create(
            {
                "holiday_start_day": (status_id.today + timedelta(days=14)).isoformat(),
                "holiday_end_day": (status_id.today + timedelta(days=20)).isoformat(),
            }
        )
        holiday_wiz.holidays()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that shorten the holiday in the future change shift
        # for worker_1
        holiday_wiz = holiday_wiz.create(
            {
                "holiday_start_day": (status_id.today + timedelta(days=1)).isoformat(),
                "holiday_end_day": (status_id.today + timedelta(days=13)).isoformat(),
            }
        )
        holiday_wiz.holidays()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

    def test_change_worker_temporary_exemption_1(self):
        """
        Change the temporary exemption start and end time on a cooperative_status.
        Check that worker is correctly unsbscribed or subscribed again
        to already generated shifts.
        """
        self._generate_shifts(days=7, nb=5)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        status_id = self.worker_regular_1.cooperative_status_ids
        status_id.today = date.today()

        # Set exemption in the past do not change shift for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "temporary_exempt_start_date": (
                    date.today() - timedelta(days=7)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    date.today() - timedelta(days=1)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        # Set exemption in the future change shift for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "temporary_exempt_start_date": (
                    date.today() + timedelta(days=1)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    date.today() + timedelta(days=13)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that beginning exemption later in the future change shift
        # for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "temporary_exempt_start_date": (
                    date.today() + timedelta(days=14)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    date.today() + timedelta(days=20)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that shorten the exemption in the future change shift
        # for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "temporary_exempt_start_date": (
                    date.today() + timedelta(days=1)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    date.today() + timedelta(days=13)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

    def test_change_worker_temporary_exemption_2(self):
        """
        Change the exemption start and end time on a cooperative_status.
        Check that worker is correctly unsbscribed or subscribed again
        to already generated shifts.

        This test uses the wizard.
        """
        self._generate_shifts(days=7, nb=5)

        # Check that initialisation works well
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        exemption_wiz = self.exemption_wizard.with_context(
            {"active_id": self.worker_regular_1.ids}
        )
        status_id = self.worker_regular_1.cooperative_status_ids
        status_id.today = date.today()

        # Set holiday in the past raise error and do not change shift
        # for worker_1
        exemption_wiz = exemption_wiz.create(
            {
                "temporary_exempt_reason_id": self.exempt_reason_1.id,
                "temporary_exempt_start_date": (
                    status_id.today - timedelta(days=7)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    status_id.today - timedelta(days=1)
                ).isoformat(),
            }
        )
        with self.assertRaises(ValidationError):
            exemption_wiz.exempt()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        # Set holiday in the future change shift for worker_1
        exemption_wiz = exemption_wiz.create(
            {
                "temporary_exempt_reason_id": self.exempt_reason_1.id,
                "temporary_exempt_start_date": (
                    status_id.today + timedelta(days=1)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    status_id.today + timedelta(days=13)
                ).isoformat(),
            }
        )
        exemption_wiz.exempt()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that beginning holiday later in the future change shift
        # for worker_1
        exemption_wiz = exemption_wiz.create(
            {
                "temporary_exempt_reason_id": self.exempt_reason_1.id,
                "temporary_exempt_start_date": (
                    status_id.today + timedelta(days=14)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    status_id.today + timedelta(days=20)
                ).isoformat(),
            }
        )
        exemption_wiz.exempt()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that shorten the holiday in the future change shift
        # for worker_1
        exemption_wiz = exemption_wiz.create(
            {
                "temporary_exempt_reason_id": self.exempt_reason_1.id,
                "temporary_exempt_start_date": (
                    status_id.today + timedelta(days=1)
                ).isoformat(),
                "temporary_exempt_end_date": (
                    status_id.today + timedelta(days=13)
                ).isoformat(),
            }
        )
        exemption_wiz.exempt()
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

    def test_irregular_worker_subscribed_to_shift_before_alert(self):
        self._generate_shifts(days=1, nb=2)
        self.assertFalse(self.worker_irregular_2.cooperative_status_ids.next_shift_id)

        some_empty_shift = self.shift_model.search(
            [("start_time", ">=", datetime.now()), ("worker_id", "=", False)],
            limit=1,
        )

        some_empty_shift.worker_id = self.worker_irregular_2
        self.assertEqual(
            self.worker_irregular_2.cooperative_status_ids.next_shift_id,
            some_empty_shift,
        )

        some_empty_shift.worker_id = False
        self.assertFalse(self.worker_irregular_2.cooperative_status_ids.next_shift_id)

    def test_unsubscribe_worker_from_task_template_computes_next_shift(self):
        self._generate_shifts(days=1, nb=2)
        datetime.now()
        # Check that initialisation works well
        next_shift = self.shift_model.search(
            [
                ("state", "=", "open"),
                ("worker_id", "=", self.worker_regular_1.id),
            ],
            order="start_time",
            limit=1,
        )
        self.assertEqual(
            self.worker_regular_1.cooperative_status_ids.next_shift_id,
            next_shift,
        )

        # Unsubscribe a worker from the task template
        self.task_template_1.worker_ids -= self.worker_regular_1
        next_shift = self.shift_model.search(
            [
                ("state", "=", "open"),
                ("worker_id", "=", self.worker_regular_1.id),
            ],
            order="start_time",
            limit=1,
        )
        self.assertEqual(
            self.worker_regular_1.cooperative_status_ids.next_shift_id,
            next_shift,
        )
        # Subscribe a worker from the task template
        self.task_template_1.worker_ids += self.worker_regular_1
        next_shift = self.shift_model.search(
            [
                ("state", "=", "open"),
                ("worker_id", "=", self.worker_regular_1.id),
            ],
            order="start_time",
            limit=1,
        )
        self.assertEqual(
            self.worker_regular_1.cooperative_status_ids.next_shift_id,
            next_shift,
        )
