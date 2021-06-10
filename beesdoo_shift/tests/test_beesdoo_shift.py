# Copyright 2021 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

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
