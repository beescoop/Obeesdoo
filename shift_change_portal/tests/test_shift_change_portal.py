# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime, timedelta

from odoo import http
from odoo.tests import HttpCase, tagged


@tagged("-at_install", "post_install")
class TestShiftChangePortalController(HttpCase):
    def setUp(self):
        super().setUp()

        self.shift_model = self.env["shift.shift"]
        self.shift_template_model = self.env["shift.template"]

        self.now = datetime.now()

        # Set up the environment
        self.env = self.env(
            context=dict(
                self.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )

        self.worker_regular_1 = self.env.ref("shift.res_partner_worker_1_demo")
        self.worker_regular_2 = self.env.ref("shift.res_partner_worker_3_demo")
        self.worker_irregular_1 = self.env.ref("shift.res_partner_worker_2_demo")

        self.task_template_1 = self.env.ref("shift_change.task_template_1_demo")
        self.task_template_2 = self.env.ref("shift_change.task_template_2_demo")
        self.task_template_3 = self.env.ref("shift_change.task_template_3_demo")

        self.worker_regular_1_portal_pwd = "fernand"
        self.worker_regular_1_portal = self.env["res.users"].create(
            {
                "name": "Fernand Peso",
                "login": "fernand",
                "email": "fernand_peso@demode.net",
                "password": self.worker_regular_1_portal_pwd,
                "partner_id": self.worker_regular_1.id,
                "groups_id": [(6, 0, [self.env.ref("base.group_portal").id])],
            }
        )

        self.shift_1 = self.shift_model.create(
            {
                "name": "shift_1",
                "task_template_id": self.task_template_1.id,
                "start_time": self.now + timedelta(days=2),
                "end_time": self.now + timedelta(days=2),
                "is_regular": True,
                "worker_id": self.worker_regular_1.id,
            }
        )
        self.shift_2 = self.shift_model.create(
            {
                "name": "shift_2",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=2),
                "end_time": self.now + timedelta(days=2),
                "is_regular": True,
                "worker_id": self.worker_regular_2.id,
            }
        )
        self.shift_3 = self.shift_model.create(
            {
                "name": "shift_3",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=4),
                "end_time": self.now + timedelta(days=4),
                "worker_id": False,
            }
        )
        self.shift_4 = self.shift_model.create(
            {
                "name": "shift_4",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now - timedelta(days=4),
                "end_time": self.now,
                "worker_id": False,
            }
        )
        self.shift_5 = self.shift_model.create(
            {
                "name": "shift_5",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=4),
                "end_time": self.now,
                "worker_id": False,
            }
        )
        self.shift_6 = self.shift_model.create(
            {
                "name": "shift_6",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(hours=1),
                "end_time": self.now,
                "worker_id": False,
            }
        )

        # Set context to avoid shift generation in the past
        self.env.context = dict(self.env.context, visualize_date=date.today())

        # Enable shift changes
        self.env["ir.config_parameter"].set_param(
            "shift_change_portal.enable_shift_change", 1
        )

        # Set maximum change shift for testing
        self.env["ir.config_parameter"].set_param(
            "shift_change.same_shift_change_max", 1
        )

    def _get_new_shift_selection(self, old_shift_id, user, password):
        """Post data to /my/shift/change/<old_shift_id>"""
        self.authenticate(user.login, password)
        response = self.url_open(
            f"/my/shift/change/{old_shift_id.id}",
        )
        return response

    def _post_shift_change(self, old_shift_id, new_shift_id, user, password):
        """Post data to /my/shift/change/<old_shift_id>/<new_shift_id"""
        self.authenticate(user.login, password)
        post_data = {
            "old_shift_id": old_shift_id.id,
            "new_shift_id": new_shift_id.id,
            "csrf_token": http.Request.csrf_token(self),
        }
        response = self.url_open(
            f"/my/shift/change/{old_shift_id.id}/{new_shift_id.id}",
            data=post_data,
        )
        return response

    def test_select_new_shift(self):
        """Test change a shift"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        response = self._get_new_shift_selection(
            self.shift_1,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("alert-danger", response.content.decode("utf-8"))

    def test_shift_change(self):
        """Test change a shift"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
        response = self._post_shift_change(
            self.shift_1,
            self.shift_3,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("alert-danger", response.content.decode("utf-8"))
        change = (
            self.env["shift.change"]
            .sudo()
            .search(
                [
                    ("old_shift_id", "=", self.shift_1.id),
                    ("new_shift_id", "=", self.shift_3.id),
                ]
            )
        )
        self.assertTrue(change)
        self.assertEqual(len(change), 1)

    def test_shift_change_not_empty(self):
        """Test changing a shift to a non empty shift"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertEqual(self.shift_2.worker_id, self.worker_regular_2)
        response = self._post_shift_change(
            self.shift_1,
            self.shift_2,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("alert-danger", response.content.decode("utf-8"))

    def test_shift_change_max(self):
        """Test changing the same shift several times"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
        self.assertFalse(self.shift_5.worker_id)
        response = self._post_shift_change(
            self.shift_1,
            self.shift_3,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("alert-danger", response.content.decode("utf-8"))
        response = self._post_shift_change(
            self.shift_3,
            self.shift_5,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("alert-danger", response.content.decode("utf-8"))

    def test_shift_change_in_past(self):
        """Test changing for a shift in the past"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_4.worker_id)
        response = self._post_shift_change(
            self.shift_1,
            self.shift_4,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("alert-danger", response.content.decode("utf-8"))

    def test_shift_change_wrong_worker(self):
        """Test creating a change with worker that don't match the shift
        worker
        """
        self.assertEqual(self.shift_2.worker_id, self.worker_regular_2)
        self.assertFalse(self.shift_4.worker_id)
        response = self._post_shift_change(
            self.shift_2,
            self.shift_4,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("alert-danger", response.content.decode("utf-8"))

    def test_shift_change_to_close(self):
        """Test changing to a shift to close"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_6.worker_id)
        response = self._post_shift_change(
            self.shift_1,
            self.shift_6,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("alert-danger", response.content.decode("utf-8"))

    def test_shift_origin_empty(self):
        """Test that fails if old_shift is empty"""
        self.assertFalse(self.shift_4.worker_id)
        self.assertFalse(self.shift_3.worker_id)
        response = self._post_shift_change(
            self.shift_4,
            self.shift_3,
            self.worker_regular_1_portal,
            self.worker_regular_1_portal_pwd,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("alert-danger", response.content.decode("utf-8"))
