# -*- coding: utf-8 -*-
# Copyright 2019 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from openerp import exceptions, fields
from openerp.exceptions import UserError, ValidationError
from openerp.tests.common import TransactionCase


class TestAttendanceSheet(TransactionCase):
    def setUp(self):
        super(TestAttendanceSheet, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.attendance_sheet_model = self.env["beesdoo.shift.sheet"]
        self.attendance_sheet_shift_model = self.env[
            "beesdoo.shift.sheet.shift"
        ]
        self.shift_expected_model = self.env["beesdoo.shift.sheet.expected"]
        self.shift_added_model = self.env["beesdoo.shift.sheet.added"]
        self.default_task_type_id = self.env["ir.config_parameter"].get_param(
            "beesdoo_shift.default_task_type_id"
        )

        self.current_time = datetime.now()
        self.user_admin = self.env.ref("base.user_root")
        self.user_generic = self.env.ref(
            "beesdoo_shift.beesdoo_shift_user_1_demo"
        )
        self.user_permanent = self.env.ref(
            "beesdoo_shift.beesdoo_shift_user_2_demo"
        )

        self.worker_regular_1 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_6_demo"
        )
        self.worker_regular_2 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_5_demo"
        )
        self.worker_regular_3 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_3_demo"
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
                "replaced_id": self.worker_regular_2.id,
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

    def test_default_task_type_setting(self):
        "Test default task type setting"
        setting_wizard = self.env["beesdoo.shift.config.settings"].sudo(
            self.user_admin
        )

        for task_type in (self.task_type_1, self.task_type_2):
            # setting default value
            setting_wizard_1 = setting_wizard.create(
                {"default_task_type_id": task_type.id}
            )
            setting_wizard_1.execute()
            param_id = self.env["ir.config_parameter"].get_param(
                "beesdoo_shift.default_task_type_id"
            )
            self.assertEquals(int(param_id), task_type.id)
            # check propagation on attendance sheet shifts
            self.assertEquals(
                self.attendance_sheet_shift_model.default_task_type_id(),
                task_type,
            )

    def test_attendance_sheet_creation(self):
        "Test creation of an attendance sheet with all its expected shifts"

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

    def test_attendance_sheet_barcode_scanner(self):
        "Test edition of an attendance sheet with barcode scanner"

        # attendance sheet generation
        self.attendance_sheet_model.sudo(self.user_generic)._generate_attendance_sheet()
        sheet_1 = self._search_sheets(
            self.shift_regular_regular_1.start_time,
            self.shift_regular_regular_1.end_time,
        )

        """
        Expected workers :
            worker_regular_1 (barcode : 421457731745)
            worker_regular_3 replaced by worker_regular_2 (barcode : 421457731744))
            worker_irregular_1 (barcode : 429919251493)
        """

        # scan barcode for expected workers
        for barcode in [421457731745, 421457731744, 429919251493]:
            sheet_1.on_barcode_scanned(barcode)

        # check expected shifts update
        for id in sheet_1.expected_shift_ids.ids:
            shift = sheet_1.expected_shift_ids.browse(id)
            self.assertEquals(shift.stage, "present")

        """
        Added workers :
            worker_regular_super_1 (barcode : 421457731741)
            worker_irregular_2 (barcode : 421457731743)
        """

        # _onchange method not applying on temporary object in tests
        sheet_1._origin = sheet_1

        # scan barcode for added workers
        sheet_1.on_barcode_scanned(421457731741)
        self.assertEquals(len(sheet_1.added_shift_ids), 1)
        sheet_1.on_barcode_scanned(421457731743)
        # scan an already added worker should not change anything
        sheet_1.on_barcode_scanned(421457731743)
        self.assertEquals(len(sheet_1.added_shift_ids), 2)

        # check added shifts fields
        for id in sheet_1.added_shift_ids.ids:
            shift = sheet_1.added_shift_ids.browse(id)
            self.assertEquals(sheet_1, shift.attendance_sheet_id)
            self.assertEquals(shift.stage, "present")
            self.assertEquals(
                shift.task_type_id,
                self.attendance_sheet_shift_model.default_task_type_id(),
            )
            if shift.working_mode == "regular":
                self.assertEquals(shift.regular_task_type, "compensation")
            else:
                self.assertFalse(shift.regular_task_type)

        # add a worker that should be replaced
        with self.assertRaises(UserError) as e:
            sheet_1.on_barcode_scanned(421457731742)
        # wrong barcode
        with self.assertRaises(UserError) as e:
            sheet_1.on_barcode_scanned(101010)

        # add an already expected worker
        with self.assertRaises(ValidationError) as e:
            sheet_1.added_shift_ids |= sheet_1.added_shift_ids.new(
                {
                    "task_type_id": sheet_1.added_shift_ids.default_task_type_id(),
                    "stage": "present",
                    "attendance_sheet_id": sheet_1.id,
                    "worker_id": self.worker_regular_1.id,
                    "regular_task_type": "normal",
                }
            )
