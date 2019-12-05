# -*- coding: utf-8 -*-
# Copyright 2019 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from openerp.tests.common import TransactionCase


class TestAttendanceSheet(TransactionCase):
    def setUp(self):
        super(TestAttendanceSheet, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.attendance_sheet_model = self.env["beesdoo.shift.sheet"]

        self.current_time = datetime.now()

        self.user_admin = self.env.ref("base.partner_root")
        self.user_permanent = self.env.ref(
            "beesdoo_shift.beesdoo_shift_partner_2_demo"
        )
        self.user_generic = self.env.ref(
            "beesdoo_shift.beesdoo_shift_partner_1_demo"
        )

        self.worker_regular_1 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_6_demo"
        )
        self.worker_regular_2 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_5_demo"
        )
        self.worker_regular_3 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_4_demo"
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
            "beesdoo.shift.beesdoo_shift_task_template_1_demo"
        )
        self.task_template_2 = self.env.ref(
            "beesdoo.shift.beesdoo_shift_task_template_2_demo"
        )

        self.shift_regular_regular_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": self.current_time + timedelta(minutes=5),
                "end_time": self.current_time + timedelta(minutes=10),
                "is_regular": True,
                "is_compensation": False,
            }
        )
        self.shift_regular_regular_2 = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_regular_2.id,
                "start_time": self.current_time - timedelta(minutes=50),
                "end_time": self.current_time - timedelta(minutes=20),
                "is_regular": True,
                "is_compensation": False,
            }
        )
        self.shift_regular_regular_replaced_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_regular_3.id,
                "start_time": self.current_time + timedelta(minutes=5),
                "end_time": self.current_time + timedelta(minutes=10),
                "is_regular": True,
                "is_compensation": False,
                "replaced_id": self.worker_regular_1.id,
            }
        )
        self.shift_regular_compensation_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_super_1.id,
                "start_time": self.current_time + timedelta(minutes=9),
                "end_time": self.current_time + timedelta(minutes=21),
                "is_regular": False,
                "is_compensation": True,
            }
        )
        self.shift_irregular_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_irregular_1.id,
                "start_time": self.current_time + timedelta(minutes=5),
                "end_time": self.current_time + timedelta(minutes=10),
            }
        )
        self.shift_irregular_2 = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_irregular_2.id,
                "start_time": self.current_time + timedelta(minutes=40),
                "end_time": self.current_time + timedelta(minutes=50),
            }
        )
        self.shift_empty_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "start_time": self.current_time + timedelta(minutes=5),
                "end_time": self.current_time + timedelta(minutes=10),
            }
        )
