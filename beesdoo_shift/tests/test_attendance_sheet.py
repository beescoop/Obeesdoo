# -*- coding: utf-8 -*-
# Copyright 2019 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from openerp import fields

from openerp.tests.common import TransactionCase


class TestAttendanceSheet(TransactionCase):
    def setUp(self):
        super(TestAttendanceSheet, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.attendance_sheet_model = self.env["beesdoo.shift.sheet"]
        self.shift_expected_model = self.env["beesdoo.shift.sheet.expected"]
        self.shift_added_model = self.env["beesdoo.shift.sheet.added"]

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
            "beesdoo_shift.beesdoo_shift_task_template_1_demo"
        )
        self.task_template_2 = self.env.ref(
            "beesdoo_shift.beesdoo_shift_task_template_2_demo"
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
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_irregular_1.id,
                "start_time": self.current_time + timedelta(minutes=5),
                "end_time": self.current_time + timedelta(minutes=10),
            }
        )
        self.shift_irregular_2 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_irregular_2.id,
                "start_time": self.current_time + timedelta(minutes=40),
                "end_time": self.current_time + timedelta(minutes=50),
            }
        )
        self.shift_empty_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_1.id,
                "start_time": self.current_time + timedelta(minutes=5),
                "end_time": self.current_time + timedelta(minutes=10),
            }
        )

    def _search_sheets(self, start_time, end_time):
        return self.attendance_sheet_model.search(
            [("start_time", "=", start_time), ("end_time", "=", end_time)]
        )

    def test_attendance_sheet_creation(self):
        "Test the creation of an attendance sheet with all its expected shifts"

        start_in_1 = self.shift_regular_regular_1.start_time
        end_in_1 = self.shift_regular_regular_1.end_time
        start_in_2 = self.shift_regular_compensation_1.start_time
        end_in_2 = self.shift_regular_compensation_1.end_time
        start_out_1 = self.shift_regular_regular_2.start_time
        end_out_1 = self.shift_regular_regular_2.end_time
        start_out_2 = self.shift_irregular_2.start_time
        end_out_2 = self.shift_irregular_2.end_time

        # test attendance sheets creation
        self.attendance_sheet_model._generate_attendance_sheet()

        self.assertEquals(len(self._search_sheets(start_in_1, end_in_1)), 1)
        self.assertEquals(len(self._search_sheets(start_in_2, end_in_2)), 1)
        self.assertEquals(len(self._search_sheets(start_out_1, end_out_1)), 0)
        self.assertEquals(len(self._search_sheets(start_out_2, end_out_2)), 0)

        # test expected shifts creation
        sheet_1 = self._search_sheets(start_in_1, end_in_1)
        sheet_2 = self._search_sheets(start_in_2, end_in_2)

        self.assertTrue(sheet_1.start_time)
        self.assertTrue(sheet_1.end_time)

        # empty shift should not be added
        self.assertEquals(len(sheet_1.expected_shift_ids), 3)
        self.assertEquals(len(sheet_1.added_shift_ids), 0)
        self.assertEquals(len(sheet_2.expected_shift_ids), 1)

        # test consistency with actual shift
        for shift in sheet_1.expected_shift_ids:
            self.assertEquals(shift.worker_id, shift.task_id.worker_id)
            self.assertEquals(
                shift.replacement_worker_id, shift.task_id.replaced_id
            )
            self.assertEquals(shift.task_type_id, shift.task_id.task_type_id)
            self.assertEquals(shift.super_coop_id, shift.task_id.super_coop_id)
            self.assertEquals(shift.working_mode, shift.task_id.working_mode)

            if shift.working_mode == "regular":
                self.assertEquals(shift.stage, "absent_2")
            if shift.working_mode == "irregular":
                self.assertEquals(shift.stage, "absent_1")

        # test maximum number of workers calculation from task_templates
        self.assertEquals(sheet_1.max_worker_no, 21)

        # test default values creation
        self.assertTrue(sheet_1.time_slot)
        self.assertTrue(sheet_1.name)
        day = fields.Datetime.from_string(sheet_1.start_time)
        self.assertEquals(sheet_1.day, fields.Date.to_string(day))
        self.assertFalse(sheet_1.annotation)
        self.assertFalse(sheet_1.is_annotated)

        # test default super-cooperator setting
        self.assertTrue(self.shift_expected_model.default_task_type_id())
