# Copyright 2021 - Today Coop IT Easy SC (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase


class TestShiftCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestShiftCommon, cls).setUpClass()
        cls.shift_model = cls.env["shift.shift"]
        cls.shift_template_model = cls.env["shift.template"]
        cls.subscribe_wizard = cls.env["shift.subscribe"]
        cls.holiday_wizard = cls.env["shift.holiday"]
        cls.exemption_wizard = cls.env["shift.temporary_exemption"]

        cls.current_time = datetime.now()
        cls.user_admin = cls.env.ref("base.user_root")
        cls.user_demo = cls.env.ref("base.user_demo")

        cls.worker_regular_1 = cls.env.ref("shift.res_partner_worker_1_demo")
        cls.worker_irregular_2 = cls.env.ref("shift.res_partner_worker_2_demo")
        cls.worker_regular_3 = cls.env.ref("shift.res_partner_worker_3_demo")
        cls.worker_regular_5 = cls.env.ref("shift.res_partner_worker_5_demo")
        cls.worker_regular_6 = cls.env.ref("shift.res_partner_worker_6_demo")

        cls.planning_1 = cls.env.ref("shift.shift_planning_1_demo")

        cls.task_template_1 = cls.env.ref("shift.task_template_1_demo")
        cls.task_template_2 = cls.env.ref("shift.task_template_2_demo")
        cls.task_template_3 = cls.env.ref("shift.task_template_3_demo")

        cls.exempt_reason_1 = cls.env.ref("shift.exempt_reason_1_demo")

    def _generate_shifts(self, days=0, nb=1):
        """
        Run _generate_next_planning *nb* times beginning from today - *days*.
        """
        planning_cls = self.env["shift.planning"]
        begin_date = date.today() - timedelta(days=days)
        self.env["ir.config_parameter"].set_param("last_planning_seq", 0)
        for i in range(nb):
            # The following line is a hack to make planning last 7 days.
            # This will not be necessary when the PR will be merged:
            # https://github.com/beescoop/Obeesdoo/pull/207
            # After the merge, the next_planning_date should be set only
            # once at the beginning with last_planning_seq
            self.env["ir.config_parameter"].set_param(
                "shift.next_planning_date",
                (begin_date + timedelta(days=i * 7)).isoformat(),
            )
            # Generate the planning
            planning_cls._generate_next_planning()

    def _count_number_of_shift(self, worker_id):
        """Count number of shift for a worker."""
        return self.shift_model.search_count([("worker_id", "=", worker_id.id)])
