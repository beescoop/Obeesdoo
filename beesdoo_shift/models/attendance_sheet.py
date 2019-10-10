# -*- coding: utf-8 -*-
from openerp import models, exceptions, fields, api
from openerp.exceptions import UserError, ValidationError

from datetime import datetime
from lxml import etree


class AttendanceSheetShift(models.Model):
    _name = "beesdoo.shift.sheet.shift"
    _description = "Copy of an actual shift into an attendance sheet"

    # Related actual shift, not required because doesn't exist for added shift before validation
    # To update after validation
    task_id = fields.Many2one("beesdoo.shift.shift", string="Task")
    attendance_sheet_id = fields.Many2one(
        "beesdoo.shift.sheet",
        string="Attendance Sheet",
        required=True,
        ondelete="cascade",
    )
    stage = fields.Selection(
        [
            ("present", "Present"),
            ("absent", "Absent"),
            ("cancelled", "Cancelled"),
        ],
        string="Shift Stage",
        copy=False,
    )

    worker_id = fields.Many2one(
        "res.partner",
        string="Worker",
        domain=[
            ("eater", "=", "worker_eater"),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        required=True,
    )
    task_type_id = fields.Many2one("beesdoo.shift.type", string="Task Type")
    working_mode = fields.Selection(
        related="worker_id.working_mode", string="Working Mode", store=True
    )

    def get_actual_stage(self):
        """
         Mapping function returning the actual id
         of corresponding beesdoo.shift.stage
         This behavior should be temporary
         (increases lack of understanding).
         """
        if not self.working_mode or not self.stage:
            raise UserError(
                "Impossible to map task status, all values are not set."
            )
        if self.working_mode == "regular":
            if self.stage == "present":
                return "done"
            if self.stage == "absent" and self.compensation_nb:
                if self.compensation_nb == "0":
                    return "excused_necessity"
                if self.compensation_nb == "1":
                    return "excused"
                if self.compensation_nb == "2":
                    return "absent"
            if self.stage == "cancelled":
                return "cancel"
        if self.working_mode == "irregular":
            if self.stage == "present":
                return "done"
            if self.stage == "cancelled":
                return "cancel"
            return "absent"


class AttendanceSheetShiftExpected(models.Model):
    _name = "beesdoo.shift.sheet.expected"
    _description = "Expected Shift"
    _inherit = ["beesdoo.shift.sheet.shift"]

    compensation_nb = fields.Selection(
        [("0", "0"), ("1", "1"), ("2", "2")],
        string="Compensations (if absent)",
    )

    replacement_worker_id = fields.Many2one(
        "res.partner",
        string="Replacement Worker",
        domain=[
            ("eater", "=", "worker_eater"),
            ("working_mode", "=", "regular"),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )

    # The webclient has display issues with this method.
    @api.onchange("stage")
    def on_change_stage(self):
        if self.working_mode == "irregular":
            if self.stage == "present" or "cancelled":
                self.compensation_nb = False
            if self.stage == "absent":
                self.compensation_nb = "1"
        if self.working_mode == "regular":
            if self.stage == "present" or "cancelled":
                self.compensation_nb = False
            if self.stage == "absent":
                self.compensation_nb = "2"


class AttendanceSheetShiftAdded(models.Model):
    """The added shifts stage must be Present
    (add an SQL constraint ?)
    """

    _name = "beesdoo.shift.sheet.added"
    _description = "Added Shift"
    _inherit = ["beesdoo.shift.sheet.shift"]

    # Change the previously determined two booleans for a more comprehensive field
    regular_task_type = fields.Selection(
        [("normal", "Normal"), ("compensation", "Compensation")],
        string="Task Mode (if regular)",
        help="Shift type for regular workers. ",
    )

    @api.model
    def create(self, vals):
        vals["stage"] = "present"
        return super(AttendanceSheetShiftAdded, self).create(vals)

    @api.onchange("working_mode")
    def on_change_working_mode(self):
        self.stage = "present"
        if self.working_mode == "regular":
            self.regular_task_type = "compensation"
        if self.working_mode == "irregular":
            self.regular_task_type = False


class AttendanceSheet(models.Model):
    _name = "beesdoo.shift.sheet"
    _inherit = ["mail.thread"]
    # _inherit = ['mail.thread','ir.needaction_mixin']
    _description = "Attendance sheets with all the shifts in one time range."
    _order = "start_time"

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    state = fields.Selection(
        [
            ("not_validated", "Not Validated"),
            ("validated", "Validated"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="not_validated",
        track_visibility="onchange",
    )

    start_time = fields.Datetime(
        string="Start Time", required=True, readonly=True
    )
    end_time = fields.Datetime(string="End Time", required=True, readonly=True)

    expected_shift_ids = fields.One2many(
        "beesdoo.shift.sheet.expected",
        "attendance_sheet_id",
        string="Expected Shifts",
    )
    added_shift_ids = fields.One2many(
        "beesdoo.shift.sheet.added",
        "attendance_sheet_id",
        string="Added Shifts",
    )

    max_worker_nb = fields.Integer(
        string="Maximum number of workers",
        default=0,
        readonly=True,
        help="Indicative maximum number of workers for the shifts.",
    )
    expected_worker_nb = fields.Integer(
        string="Number of expected workers", readonly=True, default=0
    )
    added_worker_nb = fields.Integer(
        compute="_compute_added_shift_nb",
        string="Number of added workers",
        readonly=True,
        default=0,
    )

    annotation = fields.Text(
        "Attendance Sheet annotation", default="", track_visibility="onchange"
    )
    is_annotated = fields.Boolean(
        compute="_compute_is_annotated",
        string="Annotation",
        readonly=True,
        store=True,
    )
    is_read = fields.Boolean(
        string="Mark as read",
        help="Has annotation been read by an administrator ?",
        default=False,
        track_visibility="onchange",
    )
    feedback = fields.Text(
        "Attendance Sheet feedback", track_visibility="onchange"
    )
    worker_nb_feedback = fields.Selection(
        [
            ("not_enough", "Not enough"),
            ("enough", "Enough"),
            ("too much", "Too much"),
        ],
        string="Feedback regarding the number of workers.",
        track_visibility="onchange",
    )
    attended_worker_nb = fields.Integer(
        string="Number of attended workers",
        default=0,
        help="Number of workers who attended the session.",
    )
    validated_by = fields.Many2one(
        "res.partner",
        string="Validated by",
        domain=[
            ("eater", "=", "worker_eater"),
            ("super", "=", True),
            ("working_mode", "=", "regular"),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        track_visibility="onchange",
    )

    _sql_constraints = [
        (
            "check_no_annotation_mark_read",
            "CHECK ((is_annotated=FALSE AND is_read=FALSE) OR is_annotated=TRUE)",
            "Non-annotated sheets can't be marked as read. ",
        )
    ]

    @api.constrains("expected_shift_ids", "added_shift_ids")
    def _constrain_unique_worker(self):
        added_workers = set(self.added_shift_ids.mapped("worker_id").ids)
        expected_workers = self.expected_shift_ids.mapped("worker_id").ids
        replacement_workers = self.expected_shift_ids.mapped(
            "replacement_worker_id"
        ).ids
        if len(
            added_workers.intersection(replacement_workers + expected_workers)
        ):
            raise UserError("You can't add an already expected worker.")

    @api.depends("added_shift_ids")
    def _compute_added_shift_nb(self):
        self.added_worker_nb = len(self.added_shift_ids)
        return

    # Compute name (not hardcorded to prevent incoherence with timezone)
    @api.depends("start_time", "end_time")
    def _compute_name(self):

        start_time_dt = fields.Datetime.from_string(self.start_time)
        start_time_dt = fields.Datetime.context_timestamp(self, start_time_dt)
        end_time_dt = fields.Datetime.from_string(self.end_time)
        end_time_dt = fields.Datetime.context_timestamp(self, end_time_dt)

        self.name = (
            start_time_dt.strftime("%d/%m/%y")
            + " | "
            + start_time_dt.strftime("%H:%M")
            + "-"
            + end_time_dt.strftime("%H:%M")
        )
        return

    # Is this method necessary ?
    @api.depends("annotation")
    def _compute_is_annotated(self):
        if self.annotation:
            self.is_annotated = len(self.annotation) != 0
        return

    @api.model
    def create(self, vals):
        new_sheet = super(AttendanceSheet, self).create(vals)

        # Creation and addition of the expected shifts corresponding
        # to the time range
        tasks = self.env["beesdoo.shift.shift"]
        tasks = tasks.search(
            [
                ("start_time", "=", new_sheet.start_time),
                ("end_time", "=", new_sheet.end_time),
            ]
        )
        expected_shift = self.env["beesdoo.shift.sheet.expected"]
        task_templates = set()
        for task in tasks:
            if task.working_mode == "irregular":
                compensation_nb = "1"
            else:
                compensation_nb = "2"
            new_expected_shift = expected_shift.create(
                {
                    "attendance_sheet_id": new_sheet.id,
                    "task_id": task.id,
                    "worker_id": task.worker_id.id,
                    "replacement_worker_id": task.replaced_id.id,
                    "task_type_id": task.task_type_id.id,
                    "stage": "absent",
                    "compensation_nb": compensation_nb,
                    "working_mode": task.working_mode,
                }
            )
            task_templates.add(task.task_template_id)
            new_sheet.expected_worker_nb += 1
        # Maximum number of workers calculation
        for task_template in task_templates:
            new_sheet.max_worker_nb += task_template.worker_nb
        return new_sheet

    # @api.model
    # def _needaction_domain_get(self):
    #   return [('state','=','not_validated')]

    @api.multi
    def write(self, vals):
        if self.state == "validated" and not self.env.user.has_group(
            "beesdoo_shift.group_cooperative_admin"
        ):
            raise UserError(
                "The sheet has already been validated and can't be edited."
            )
        return super(AttendanceSheet, self).write(vals)

    @api.one
    def validate(self):
        self.ensure_one()
        if self.state == "validated":
            raise UserError("The sheet has already been validated.")

        shift = self.env["beesdoo.shift.shift"]
        stage = self.env["beesdoo.shift.stage"]

        # Fields validation
        for added_shift in self.added_shift_ids:
            if (
                not added_shift.stage
                or not added_shift.worker_id
                or not added_shift.task_type_id
                or not added_shift.working_mode
                or (
                    added_shift.worker_id.working_mode == "regular"
                    and not added_shift.regular_task_type
                )
            ):
                raise UserError("All fields must be set before validation.")

        # Expected shifts status update
        for expected_shift in self.expected_shift_ids:
            actual_shift = expected_shift.task_id
            actual_stage = stage.search(
                [("code", "=", expected_shift.get_actual_stage())]
            )
            # If the actual stage has been deleted, the sheet is still validated.
            # Raising an exception would stop this.
            # How can we show a message without stopping validation ?
            if actual_stage:
                actual_shift.stage_id = actual_stage
                actual_shift.replacement_worker_id = (
                    expected_shift.replacement_worker_id
                )

        # Added shifts status update
        for added_shift in self.added_shift_ids:
            actual_stage = stage.search(
                [("code", "=", added_shift.get_actual_stage())]
            )
            # WARNING: mapping the selection field to the booleans used in Task
            is_regular_worker = added_shift.worker_id.working_mode == "regular"
            is_regular_shift = added_shift.regular_task_type == "normal"
            # Add an annotation if a regular worker is doing its regular shift
            if is_regular_shift and is_regular_worker:
                self.annotation += (
                    "\n\nWarning : %s attended its shift as a normal one but was not expected."
                    " Something may be wrong in his/her personnal informations.\n"
                    % added_shift.worker_id.name
                )
            # Edit a non-assigned shift or create one if none
            non_assigned_shifts = shift.search(
                [
                    ("worker_id", "=", False),
                    ("start_time", "=", self.start_time),
                    ("end_time", "=", self.end_time),
                    ("task_type_id", "=", added_shift.task_type_id.id)
                ]
            )

            if len(non_assigned_shifts):
                actual_shift = non_assigned_shifts[0]
                actual_shift.write(
                    {
                        "stage_id": actual_stage.id,
                        "worker_id": added_shift.worker_id.id,
                        "stage_id": actual_stage.id,
                        "is_regular": is_regular_shift and is_regular_worker,
                        "is_compensation": not is_regular_shift
                        and is_regular_worker,
                    }
                )
            else:
                actual_shift = self.env["beesdoo.shift.shift"].create(
                    {
                        "name": "Added shift TEST %s" % self.start_time,
                        "task_type_id": added_shift.task_type_id.id,
                        "worker_id": added_shift.worker_id.id,
                        "start_time": self.start_time,
                        "end_time": self.end_time,
                        "stage_id": actual_stage.id,
                        "is_regular": is_regular_shift and is_regular_worker,
                        "is_compensation": not is_regular_shift
                        and is_regular_worker,
                    }
                )
            added_shift.task_id = actual_shift.id

        self.state = "validated"
        return

    # @api.multi is needed to call the wizard, but doesn't match @api.one
    # from the validate() method
    @api.multi
    def validate_via_wizard(self):
        if self.env.user.has_group("beesdoo_shift.group_cooperative_admin"):
            self.validated_by = self.env.user.partner_id
            self.validate()
            return
        return {
            "type": "ir.actions.act_window",
            "res_model": "beesdoo.shift.sheet.validate",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }
