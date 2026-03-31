# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase


class TestShiftSolidarityCommon(TransactionCase):
    def setUp(self):
        super().setUp()

        # Force all operations to run as admin
        self.env = self.env(user=self.env.ref("base.user_admin"))

        self.shift_model = self.env["shift.shift"]
        self.shift_template_model = self.env["shift.template"]
        self.shift_solidarity_offer_model = self.env["shift.solidarity.offer"]
        self.shift_solidarity_request_model = self.env["shift.solidarity.request"]

        self.now = datetime.now()
        self.future = self.now + timedelta(days=30)

        self.worker_regular_1 = self.env.ref("shift.res_partner_worker_1_demo")
        self.worker_regular_2 = self.env.ref("shift.res_partner_worker_3_demo")
        self.worker_irregular_1 = self.env.ref("shift.res_partner_worker_2_demo")

        self.task_template_1 = self.env.ref("shift.task_template_1_demo")
        self.task_template_2 = self.env.ref("shift.task_template_2_demo")
        self.task_template_3 = self.env.ref("shift.task_template_3_demo")

        self.shift1_d2_w1_t1 = self.shift_model.create(
            {
                "name": "shift1_d2_w1_t1",
                "task_template_id": self.task_template_1.id,
                "start_time": self.now + timedelta(days=2),
                "end_time": self.now + timedelta(days=2),
                "is_regular": True,
                "worker_id": self.worker_regular_1.id,
            }
        )

        self.shift2_d2_w2_t2 = self.shift_model.create(
            {
                "name": "shift2_d2_w2_t2",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=2),
                "end_time": self.now + timedelta(days=2),
                "is_regular": True,
                "worker_id": self.worker_regular_2.id,
            }
        )

        self.shift3_d4_nw_t2 = self.shift_model.create(
            {
                "name": "shift3_d4_nw_t2",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=4),
                "end_time": self.now + timedelta(days=4),
                "worker_id": False,
            }
        )

        self.shift4_past_nw_t2 = self.shift_model.create(
            {
                "name": "shift4_past_nw_t2",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now - timedelta(days=4),
                "end_time": self.now,
                "worker_id": False,
            }
        )

        self.shift5_d6_nw_t2 = self.shift_model.create(
            {
                "name": "shift5_d6_nw_t2",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=6),
                "end_time": self.now,
                "worker_id": False,
            }
        )

        self.shift6_h1_nw_t2 = self.shift_model.create(
            {
                "name": "shift6_h1_nw_t2",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(hours=1),
                "end_time": self.now,
                "worker_id": False,
            }
        )

        self.shift7_h1_w1_t1 = self.shift_model.create(
            {
                "name": "shift7_h1_w1_t1",
                "task_template_id": self.task_template_1.id,
                "start_time": self.now + timedelta(hours=1),
                "end_time": self.now,
                "is_regular": True,
                "worker_id": self.worker_regular_1.id,
            }
        )

        # Set context to avoid shift generation in the past
        self.env.context = dict(self.env.context, visualize_date=date.today())

        # Module configaration for tests
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.enable_solidarity", 1
        )
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.solidarity_counter_start_value", 0
        )
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.solidarity_counter_limit", -1
        )
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.max_solidarity_requests_number", 1
        )
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.solidarity_offer_hour_limit", 24
        )
        self.env["ir.config_parameter"].set_param(
            "shift_change.solidarity_request_hour_limit", 24
        )
