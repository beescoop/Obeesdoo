# Copyright 2019 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime, timedelta

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestBeesdooShift(TransactionCase):
    def setUp(self):
        super(TestBeesdooShift, self).setUp()
        self.shift_model = self.env["beesdoo.shift.shift"]
        self.shift_template_model = self.env["beesdoo.shift.template"]
        self.attendance_sheet_model = self.env["beesdoo.shift.sheet"]
        self.attendance_sheet_shift_model = self.env["beesdoo.shift.sheet.shift"]
        self.shift_expected_model = self.env["beesdoo.shift.sheet.expected"]
        self.shift_added_model = self.env["beesdoo.shift.sheet.added"]
        self.pre_filled_task_type_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift_attendance.pre_filled_task_type_id")
        )

        self.current_time = datetime.now()
        self.user_admin = self.env.ref("base.user_root")
        self.user_generic = self.env.ref(
            "beesdoo_shift_attendance.beesdoo_shift_user_1_demo"
        )
        self.user_permanent = self.env.ref(
            "beesdoo_shift_attendance.beesdoo_shift_user_2_demo"
        )

        self.setting_wizard = self.env["res.config.settings"].sudo(self.user_admin)

        self.worker_regular_1 = self.env.ref("beesdoo_shift.res_partner_worker_6_demo")
        self.worker_regular_2 = self.env.ref("beesdoo_shift.res_partner_worker_5_demo")
        self.worker_regular_3 = self.env.ref("beesdoo_shift.res_partner_worker_3_demo")
        self.worker_regular_super_1 = self.env.ref(
            "beesdoo_shift.res_partner_worker_1_demo"
        )
        self.worker_irregular_1 = self.env.ref(
            "beesdoo_shift.res_partner_worker_2_demo"
        )
        self.worker_irregular_2 = self.env.ref(
            "beesdoo_shift.res_partner_worker_4_demo"
        )

        self.task_type_1 = self.env.ref("beesdoo_shift.beesdoo_shift_task_type_1_demo")
        self.task_type_2 = self.env.ref("beesdoo_shift.beesdoo_shift_task_type_2_demo")
        self.task_type_3 = self.env.ref("beesdoo_shift.beesdoo_shift_task_type_3_demo")

        self.task_template_1 = self.env.ref(
            "beesdoo_worker_status.beesdoo_shift_task_template_1_demo"
        )
        self.task_template_2 = self.env.ref(
            "beesdoo_worker_status.beesdoo_shift_task_template_2_demo"
        )

        # Set time in and out of generation interval parameter
        self.start_in_1 = self.current_time + timedelta(seconds=2)
        self.end_in_1 = self.current_time + timedelta(minutes=10)
        self.start_in_2 = self.current_time + timedelta(minutes=9)
        self.end_in_2 = self.current_time + timedelta(minutes=21)
        self.start_out_1 = self.current_time - timedelta(minutes=50)
        self.end_out_1 = self.current_time - timedelta(minutes=20)
        self.start_out_2 = self.current_time + timedelta(minutes=40)
        self.end_out_2 = self.current_time + timedelta(minutes=50)

        self.shift_regular_regular_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_1.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
                "is_regular": True,
                "is_compensation": False,
            }
        )
        self.shift_regular_regular_2 = self.shift_model.create(
            {
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_regular_2.id,
                "start_time": self.start_out_1,
                "end_time": self.end_out_1,
                "is_regular": True,
                "is_compensation": False,
            }
        )
        self.shift_regular_regular_replaced_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_regular_3.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
                "is_regular": True,
                "is_compensation": False,
                "replaced_id": self.worker_regular_2.id,
            }
        )
        self.future_shift_regular = self.shift_model.create(
            {
                "task_template_id": self.task_template_2.id,
                "task_type_id": self.task_type_1.id,
                "worker_id": self.worker_regular_super_1.id,
                "start_time": self.start_in_2,
                "end_time": self.end_in_2,
                "is_regular": False,
                "is_compensation": True,
            }
        )
        self.shift_irregular_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_2.id,
                "worker_id": self.worker_irregular_1.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
            }
        )
        self.shift_irregular_2 = self.shift_model.create(
            {
                "task_type_id": self.task_type_3.id,
                "worker_id": self.worker_irregular_2.id,
                "start_time": self.start_out_2,
                "end_time": self.end_out_2,
            }
        )
        self.shift_empty_1 = self.shift_model.create(
            {
                "task_template_id": self.task_template_1.id,
                "task_type_id": self.task_type_1.id,
                "start_time": self.start_in_1,
                "end_time": self.end_in_1,
            }
        )

    def search_sheets(self, start_time, end_time):
        if (type(start_time) and type(end_time)) == datetime:
            return self.attendance_sheet_model.search(
                [("start_time", "=", start_time), ("end_time", "=", end_time)]
            )

    def test_attendance_sheet_creation(self):
        "Test creation of an attendance sheet with all its expected shifts"

        # Set generation interval setting
        setting_wizard_1 = self.setting_wizard.create(
            {
                "pre_filled_task_type_id": self.task_type_1.id,
                "attendance_sheet_generation_interval": 15,
                "attendance_sheet_default_shift_state": "done",
            }
        )
        setting_wizard_1.execute()

        # Test attendance sheets creation
        self.attendance_sheet_model._generate_attendance_sheet()

        self.assertEqual(len(self.search_sheets(self.start_in_1, self.end_in_1)), 1)
        self.assertEqual(len(self.search_sheets(self.start_in_2, self.end_in_2)), 1)
        self.assertEqual(len(self.search_sheets(self.start_out_1, self.end_out_1)), 0)
        self.assertEqual(len(self.search_sheets(self.start_out_2, self.end_out_2)), 0)

        # Test expected shifts creation
        # Sheet 1 starts at current time + 2 secs, ends at current time + 10 min
        # Sheet 2 starts at current time + 9 min, ends at current time + 21 min

        sheet_1 = self.search_sheets(self.start_in_1, self.end_in_1)
        sheet_2 = self.search_sheets(self.start_in_2, self.end_in_2)

        self.assertTrue(sheet_1.start_time)
        self.assertTrue(sheet_1.end_time)

        # Empty shift should not be added
        self.assertEqual(len(sheet_1.expected_shift_ids), 3)
        self.assertEqual(len(sheet_1.added_shift_ids), 0)
        self.assertEqual(len(sheet_2.expected_shift_ids), 1)

        # Test consistency with actual shift for sheet 1
        for shift in sheet_1.expected_shift_ids:
            self.assertEqual(shift.worker_id, shift.task_id.worker_id)
            self.assertEqual(shift.replaced_id, shift.task_id.replaced_id)
            self.assertEqual(shift.task_type_id, shift.task_id.task_type_id)
            self.assertEqual(shift.super_coop_id, shift.task_id.super_coop_id)
            self.assertEqual(shift.working_mode, shift.task_id.working_mode)
            self.assertEqual(shift.state, "done")  # cf settings

        # Empty shift should be considered in max worker number calculation
        self.assertEqual(sheet_1.max_worker_no, 4)

        # Test default values creation
        self.assertTrue(sheet_1.time_slot)
        self.assertEqual(sheet_1.day, self.start_in_1.date())
        self.assertEqual(sheet_1.day_abbrevation, "Lundi")
        self.assertEqual(sheet_1.week, "Semaine A")
        self.assertTrue(sheet_1.name)
        self.assertFalse(sheet_1.notes)
        self.assertFalse(sheet_1.is_annotated)

    def test_attendance_sheet_barcode_scan(self):
        """
        Edition of an attendance sheet
        with barcode scanner, as a generic user"
        """

        # Attendance sheet generation
        self.attendance_sheet_model.sudo(self.user_generic)._generate_attendance_sheet()
        sheet_1 = self.search_sheets(self.start_in_1, self.end_in_1)
        sheet_1 = sheet_1.sudo(self.user_generic)

        # Expected workers are :
        #     worker_regular_1 (barcode : 521457731745)
        #     worker_regular_3 replaced by worker_regular_2 (barcode : 521457731744))
        #     worker_irregular_1 (barcode : 529919251493)

        # Scan barcode for expected workers
        for barcode in [521457731745, 521457731744, 529919251493]:
            sheet_1.on_barcode_scanned(barcode)

        # Check expected shifts update
        for id_ in sheet_1.expected_shift_ids.ids:
            shift = sheet_1.expected_shift_ids.browse(id_)
            self.assertEqual(shift.state, "done")

        # Added workers are :
        #     worker_regular_super_1 (barcode : 521457731741)
        #     worker_irregular_2 (barcode : 521457731743)

        # Workararound for _onchange method
        # (not applying on temporary object in tests)
        sheet_1._origin = sheet_1

        # Scan barcode for added workers
        sheet_1.on_barcode_scanned(521457731741)
        self.assertEqual(len(sheet_1.added_shift_ids), 1)
        sheet_1.on_barcode_scanned(521457731743)
        # Scan an already added worker should not change anything
        sheet_1.on_barcode_scanned(521457731743)
        self.assertEqual(len(sheet_1.added_shift_ids), 2)

        # Check added shifts fields
        for id_ in sheet_1.added_shift_ids.ids:
            shift = sheet_1.added_shift_ids.browse(id_)
            self.assertEqual(sheet_1, shift.attendance_sheet_id)
            self.assertEqual(shift.state, "done")
            self.assertEqual(
                shift.task_type_id,
                self.attendance_sheet_shift_model.pre_filled_task_type_id(),
            )
            if shift.working_mode == "regular":
                self.assertTrue(shift.is_compensation)
            else:
                self.assertFalse(shift.is_compensation)

        # Add a worker that should be replaced
        with self.assertRaises(UserError):
            sheet_1.on_barcode_scanned(521457731742)
        # Wrong barcode
        with self.assertRaises(UserError):
            sheet_1.on_barcode_scanned(101010)

        # Add an unsubscribed worker
        self.worker_regular_1.cooperative_status_ids.sr = -2
        self.worker_regular_1.cooperative_status_ids.sc = -2
        with self.assertRaises(UserError):
            sheet_1.on_barcode_scanned(521457731745)

    def test_attendance_sheet_edition(self):

        # Attendance sheet generation
        self.attendance_sheet_model.sudo(self.user_generic)._generate_attendance_sheet()
        sheet_1 = self.search_sheets(self.start_in_1, self.end_in_1)

        # Expected shifts edition
        sheet_1.expected_shift_ids[1].state = "done"
        sheet_1.expected_shift_ids[2].state = "absent_1"

        # Added shits addition
        sheet_1.added_shift_ids |= sheet_1.added_shift_ids.new(
            {
                "task_type_id": self.task_type_2.id,
                "state": "done",
                "attendance_sheet_id": sheet_1.id,
                "worker_id": self.worker_irregular_2.id,
                "is_compensation": False,
                "is_regular": False,
            }
        )
        # Same task type as empty shift (should edit it on validation)
        sheet_1.added_shift_ids |= sheet_1.added_shift_ids.new(
            {
                "task_type_id": self.task_type_1.id,
                "state": "done",
                "attendance_sheet_id": sheet_1.id,
                "worker_id": self.worker_regular_super_1.id,
                "is_compensation": True,
                "is_regular": False,
            }
        )

        # TODO: test validation with wizard (as generic user)
        # class odoo.tests.common.Form(recordp, view=None)
        # is only available from version 12

        # sheet_1 = sheet_1.sudo(self.user_generic)

        # Validation without wizard (as admin user)
        sheet_1 = sheet_1.sudo(self.user_admin)

        # Wait necessary time for shifts to begin
        waiting_time = (self.start_in_1 - datetime.now()).total_seconds()
        if waiting_time > 0:
            with self.assertRaises(UserError) as econtext:
                sheet_1.validate_with_checks()
            self.assertIn("once the shifts have started", str(econtext.exception))
            time.sleep(waiting_time)

        sheet_1.worker_nb_feedback = "enough"
        sheet_1.feedback = "Great session."
        sheet_1.notes = "Important information."

        sheet_1.validate_with_checks()

        with self.assertRaises(UserError) as econtext:
            sheet_1.validate_with_checks()
        self.assertIn("already been validated", str(econtext.exception))

        self.assertEqual(sheet_1.state, "validated")
        self.assertEqual(sheet_1.validated_by, self.user_admin.partner_id)
        self.assertTrue(sheet_1.is_annotated)
        self.assertFalse(sheet_1.is_read)

        # Check actual shifts update
        workers = sheet_1.expected_shift_ids.mapped(
            "worker_id"
        ) | sheet_1.added_shift_ids.mapped("worker_id")
        self.assertEqual(len(workers), 5)
        self.assertEqual(sheet_1.expected_shift_ids[0].task_id.state, "absent_2")
        self.assertEqual(sheet_1.expected_shift_ids[1].task_id.state, "done")
        self.assertEqual(sheet_1.expected_shift_ids[2].task_id.state, "absent_1")
        self.assertEqual(sheet_1.added_shift_ids[0].task_id.state, "done")
        self.assertEqual(sheet_1.added_shift_ids[1].task_id.state, "done")

        # Empty shift should have been updated
        self.assertEqual(sheet_1.added_shift_ids[0].task_id, self.shift_empty_1)

        # sheet_1.expected_shift_ids[0].worker_id
