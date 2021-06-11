# Copyright 2021 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase


class TestBeesdooShift(TransactionCase):
    def setUp(self):
        super(TestBeesdooShift, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.subscribe_wizard = self.env["beesdoo.shift.subscribe"]

        self.current_time = datetime.now()
        self.user_admin = self.env.ref("base.user_root")

        self.worker_regular_1 = self.env.ref(
            "beesdoo_shift.res_partner_worker_1_demo"
        )
        self.worker_regular_3 = self.env.ref(
            "beesdoo_shift.res_partner_worker_3_demo"
        )
        self.worker_regular_5 = self.env.ref(
            "beesdoo_shift.res_partner_worker_5_demo"
        )
        self.worker_regular_6 = self.env.ref(
            "beesdoo_shift.res_partner_worker_6_demo"
        )

        self.planning_1 = self.env.ref(
            "beesdoo_shift.beesdoo_shift_planning_1_demo"
        )

        self.task_template_1 = self.env.ref(
            "beesdoo_shift.task_template_1_demo"
        )
        self.task_template_2 = self.env.ref(
            "beesdoo_shift.task_template_2_demo"
        )
        self.task_template_3 = self.env.ref(
            "beesdoo_shift.task_template_3_demo"
        )

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
        return self.shift_model.search_count(
            [("worker_id", "=", worker_id.id)]
        )

    def test_unsubscribe_worker_from_task_template_1(self):
        """
        Check that removing a worker from a task_template via the
        task_template remove the worker from the already generated
        shifts.
        """
        # Generate shift
        # Timedelta 1 day because we test on monday from planning 1.
        # We need a shift in the past and a shift in the future.
        self.env["ir.config_parameter"].set_param("last_planning_seq", 0)
        self.env["ir.config_parameter"].set_param(
            "next_planning_date",
            (datetime.today() - timedelta(days=1)).isoformat(),
        )
        # Generate the previous week planning
        self.planning_1._generate_next_planning()
        # Generate the current week planning
        self.planning_1._generate_next_planning()

        # Check that initialisation works well
        # two shift for this worker
        number_shift_worker_1 = self.shift_model.search_count(
            [("worker_id", "=", self.worker_regular_1.id)]
        )
        self.assertEqual(number_shift_worker_1, 2)

        # Unsubscribe a worker from the task template
        self.task_template_1.worker_ids -= self.worker_regular_1

        number_shift_worker_1 = self.shift_model.search_count(
            [("worker_id", "=", self.worker_regular_1.id)]
        )
        self.assertEqual(number_shift_worker_1, 1)

    def test_unsubscribe_worker_from_task_template_2(self):
        """
        Check that removing a worker from a task_template via the
        res_partner remove the worker from the already generated
        shifts.
        """
        # Generate shift
        # Timedelta 1 day because we test on monday from planning 1.
        # We need a shift in the past and a shift in the future.
        self.env["ir.config_parameter"].set_param("last_planning_seq", 0)
        self.env["ir.config_parameter"].set_param(
            "next_planning_date",
            (datetime.today() - timedelta(days=1)).isoformat(),
        )
        # Generate the previous week planning
        self.planning_1._generate_next_planning()
        # Generate the current week planning
        self.planning_1._generate_next_planning()

        # Check that initialisation works well
        # two shift for this worker
        number_shift_worker_1 = self.shift_model.search_count(
            [("worker_id", "=", self.worker_regular_1.id)]
        )
        self.assertEqual(number_shift_worker_1, 2)

        # Unsubscribe a worker from the task template
        self.worker_regular_1.subscribed_shift_ids -= self.task_template_1

        number_shift_worker_1 = self.shift_model.search_count(
            [("worker_id", "=", self.worker_regular_1.id)]
        )
        self.assertEqual(number_shift_worker_1, 1)

    def test_change_working_mode_1(self):
        """
        Check that changing a regular worker to irregular via the wizard
        removes the worker from the already generated shifts.
        """
        # Generate shift
        # Timedelta 1 day because we test on monday from planning 1.
        # We need a shift in the past and a shift in the future.
        self.env["ir.config_parameter"].set_param("last_planning_seq", 0)
        self.env["ir.config_parameter"].set_param(
            "next_planning_date",
            (datetime.today() - timedelta(days=1)).isoformat(),
        )
        # Generate the previous week planning
        self.planning_1._generate_next_planning()
        # Generate the current week planning
        self.planning_1._generate_next_planning()

        # Check that initialisation works well
        # two shift for this worker
        number_shift_worker_1 = self.shift_model.search_count(
            [("worker_id", "=", self.worker_regular_1.id)]
        )
        self.assertEqual(number_shift_worker_1, 2)

        subscribe_wiz = self.subscribe_wizard.with_context(
            {"active_id": self.worker_regular_1.ids}
        )
        subscribe_wiz = subscribe_wiz.create({"working_mode": "irregular"})
        subscribe_wiz.subscribe()

        number_shift_worker_1 = self.shift_model.search_count(
            [("worker_id", "=", self.worker_regular_1.id)]
        )
        self.assertTrue(
            self.worker_regular_1 not in self.task_template_1.worker_ids
        )
        self.assertEqual(number_shift_worker_1, 1)

    def test_change_worker_holiday_1(self):
        """
        Change the holiday start and end time on a cooperative_status.
        Check that worker is correctly unsbscribed or subscribed again
        to already generated shifts.
        """
        self._generate_shifts(days=7, nb=5)

        # Check that initialisation works well
        # two shift for this worker
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        # Set holiday in the past do not change shift for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (
                    date.today() - timedelta(days=7)
                ).isoformat(),
                "holiday_end_time": (
                    date.today() - timedelta(days=1)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 5)

        # Set holiday in the future change shift for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (
                    date.today() + timedelta(days=1)
                ).isoformat(),
                "holiday_end_time": (
                    date.today() + timedelta(days=13)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that beginning holiday later in the future change shift
        # for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (
                    date.today() + timedelta(days=14)
                ).isoformat(),
                "holiday_end_time": (
                    date.today() + timedelta(days=20)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)

        # Check that shorten the holiday in the future change shift
        # for worker_1
        self.worker_regular_1.cooperative_status_ids.write(
            {
                "holiday_start_time": (
                    date.today() + timedelta(days=1)
                ).isoformat(),
                "holiday_end_time": (
                    date.today() + timedelta(days=13)
                ).isoformat(),
            }
        )
        self.assertEqual(self._count_number_of_shift(self.worker_regular_1), 4)
