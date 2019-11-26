# -*- coding: utf-8 -*-

from lxml import etree

from openerp import models, exceptions, fields, api, _
from openerp.exceptions import UserError, ValidationError

from datetime import datetime
from lxml import etree


class AttendanceSheetShift(models.AbstractModel):
    _name = "beesdoo.shift.sheet.shift"
    _description = "Copy of an actual shift into an attendance sheet"

    @api.model
    def _default_task_type_id(self):
        parameters = self.env["ir.config_parameter"]
        id = int(parameters.get_param("beesdoo_shift.default_task_type_id"))
        task_types = self.env["beesdoo.shift.type"]
        return task_types.browse(id)

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
            ("absent_0", "Absent / 0 Compensation"),
            ("absent_1", "Absent / 1 Compensation"),
            ("absent_2", "Absent / 2 Compensations"),
            ("cancelled", "Cancelled"),
        ],
        string="Shift Stage",
    )

    worker_id = fields.Many2one(
        "res.partner",
        string="Worker",
        domain=[
            ("eater", "=", "worker_eater"),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )
    task_type_id = fields.Many2one(
        "beesdoo.shift.type", string="Task Type", default=_default_task_type_id
    )
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
                _("Impossible to map task status, all values are not set.")
            )
        if self.working_mode == "regular":
            if self.stage == "present":
                return "done"
            if self.stage == "absent_0":
                return "excused_necessity"
            if self.stage == "absent_1":
                return "excused"
            if self.stage == "absent_2":
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

    replacement_worker_id = fields.Many2one(
        "res.partner",
        string="Replacement Worker",
        domain=[
            ("eater", "=", "worker_eater"),
            ("working_mode", "=", "regular"),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )


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
    stage = fields.Selection(default="present")

    # WARNING: check the code, readonly fields modified by onchange are not inserted on write
    @api.onchange("working_mode")
    def on_change_working_mode(self):
        self.stage = "present"
        if self.working_mode == "regular":
            self.regular_task_type = "compensation"
        if self.working_mode == "irregular":
            self.regular_task_type = False


class AttendanceSheet(models.Model):
    _name = "beesdoo.shift.sheet"
    _inherit = [
        "mail.thread",
        "ir.needaction_mixin",
        "barcodes.barcode_events_mixin",
    ]
    _description = "Attendance sheets with all the shifts in one time range."
    _order = "start_time"

    name = fields.Char(
        string="Name", compute="_compute_name", store=True, readonly=True
    )
    active = fields.Boolean(string="Active", default=1)
    state = fields.Selection(
        [("not_validated", "Not Validated"), ("validated", "Validated"),],
        string="Status",
        readonly=True,
        index=True,
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
    max_worker_no = fields.Integer(
        string="Maximum number of workers",
        default=0,
        readonly=True,
        help="Indicative maximum number of workers for the shifts.",
    )
    annotation = fields.Text("Annotation", default="")
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
    feedback = fields.Text("Feedback")
    worker_nb_feedback = fields.Selection(
        [
            ("not_enough", "Not enough"),
            ("enough", "Enough"),
            ("too_many", "Too many"),
        ],
        string="Number of workers.",
    )
    attended_worker_nb = fields.Integer(
        string="Number of attended workers",
        default=0,
        help="Number of workers who attended the session.",
        readonly=True,
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
        readonly=True,
    )

    _sql_constraints = [
        (
            "check_no_annotation_mark_read",
            "CHECK ((is_annotated=FALSE AND is_read=FALSE) OR is_annotated=TRUE)",
            _("Non-annotated sheets can't be marked as read."),
        )
    ]

    @api.constrains(
        "expected_shift_ids",
        "added_shift_ids",
        "annotation",
        "feedback",
        "worker_nb_feedback",
    )
    def _lock_after_validation(self):
        if self.state == "validated":
            raise UserError(
                _("The sheet has already been validated and can't be edited.")
            )

    @api.multi
    def button_mark_as_read(self):
        if self.is_read:
            raise UserError(_("The sheet has already been marked as read."))
        self.is_read = True

    @api.constrains("expected_shift_ids", "added_shift_ids")
    def _constrain_unique_worker(self):
        # Warning : map return generator in python3 (for Odoo 12)
        added_ids = map(lambda s: s.worker_id.id, self.added_shift_ids)
        expected_ids = map(lambda s: s.worker_id.id, self.expected_shift_ids)
        replacement_ids = map(
            lambda s: s.replacement_worker_id.id, self.expected_shift_ids
        )
        replacement_ids = filter(bool, replacement_ids)
        ids = added_ids + expected_ids + replacement_ids

        if (len(ids) - len(set(ids))) > 0:
            raise UserError(
                _(
                    "You can't add the same worker more than once to an attendance sheet."
                )
            )

    # Compute name (not hardcorded to prevent incoherence with timezone)
    @api.depends("start_time", "end_time")
    def _compute_name(self):

        start_time_dt = fields.Datetime.from_string(self.start_time)
        start_time_dt = fields.Datetime.context_timestamp(self, start_time_dt)
        end_time_dt = fields.Datetime.from_string(self.end_time)
        end_time_dt = fields.Datetime.context_timestamp(self, end_time_dt)
        self.name = (
            start_time_dt.strftime("%Y-%m-%d")
            + " "
            + start_time_dt.strftime("%H:%M")
            + "-"
            + end_time_dt.strftime("%H:%M")
        )

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
                stage = "absent_1"
            else:
                stage = "absent_2"
            if task.worker_id:
                new_expected_shift = expected_shift.create(
                    {
                        "attendance_sheet_id": new_sheet.id,
                        "task_id": task.id,
                        "worker_id": task.worker_id.id,
                        "replacement_worker_id": task.replaced_id.id,
                        "task_type_id": task.task_type_id.id,
                        "stage": stage,
                        "working_mode": task.working_mode,
                    }
                )
                task_templates.add(task.task_template_id)
        # Maximum number of workers calculation
        new_sheet.max_worker_no = sum(r.worker_nb for r in task_templates)
        return new_sheet

    # Workaround to display notifications only for unread and not validated
    # sheets, via a check on domain.
    @api.model
    def _needaction_count(self, domain=None):
        if domain == [
            ("is_annotated", "=", True),
            ("is_read", "=", False),
        ] or domain == [("state", "=", "not_validated")]:
            return self.search_count(domain)
        return

    def validate(self):
        self.ensure_one()
        if self.state == "validated":
            raise UserError("The sheet has already been validated.")

        shift = self.env["beesdoo.shift.shift"]
        stage = self.env["beesdoo.shift.stage"]

        # Fields validation
        for added_shift in self.added_shift_ids:
            if not added_shift.worker_id:
                raise UserError(
                    _("Worker must be set for shift %s") % added_shift.id
                )
            if not added_shift.stage:
                raise UserError(
                    _("Shift Stage is missing for %s")
                    % added_shift.worker_id.name
                )
            if not added_shift.task_type_id:
                raise UserError(
                    _("Task Type is missing for %s")
                    % added_shift.worker_id.name
                )
            if not added_shift.working_mode:
                raise UserError(
                    _("Working mode is missing for %s")
                    % added_shift.worker_id.name
                )
            if (
                added_shift.worker_id.working_mode == "regular"
                and not added_shift.regular_task_type
            ):
                raise UserError(
                    _("Regular Task Type is missing for %s")
                    % added_shift.worker_id.name
                )

        for expected_shift in self.expected_shift_ids:
            if not expected_shift.stage:
                raise UserError(
                    _("Shift Stage is missing for %s")
                    % expected_shift.worker_id.name
                )

        # Expected shifts status update
        for expected_shift in self.expected_shift_ids:
            actual_shift = expected_shift.task_id
            # We get stage record corresponding to mapped stage id
            actual_stage = self.env.ref(
                "beesdoo_shift.%s" % expected_shift.get_actual_stage()
            )

            # If the actual stage has been deleted, the sheet is still validated.
            # Raising an exception would stop this but would prevent validation.
            # How can we show a message without stopping validation ?
            if actual_stage:
                actual_shift.stage_id = actual_stage
                actual_shift.replaced_id = expected_shift.replacement_worker_id

        # Added shifts status update
        for added_shift in self.added_shift_ids:
            actual_stage = self.env.ref(
                "beesdoo_shift.%s" % added_shift.get_actual_stage()
            )
            is_regular_worker = added_shift.worker_id.working_mode == "regular"
            is_regular_shift = added_shift.regular_task_type == "normal"
            # Add an annotation if a regular worker is doing its regular shift
            if is_regular_shift and is_regular_worker:
                self.annotation += (
                    _(
                        "\n\nWarning : %s attended its shift as a normal one but was not expected."
                        " Something may be wrong in his/her personnal informations.\n"
                    )
                    % added_shift.worker_id.name
                )
            # Edit a non-assigned shift or create one if none
            non_assigned_shifts = shift.search(
                [
                    ("worker_id", "=", False),
                    ("start_time", "=", self.start_time),
                    ("end_time", "=", self.end_time),
                    ("task_type_id", "=", added_shift.task_type_id.id),
                ],
                limit=1,
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
                actual_shift = shift.create(
                    {
                        "name": _("[Added Shift] %s") % self.start_time,
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

    def on_barcode_scanned(self, barcode):

        if self.state == "validated":
            raise UserError(
                _("You cannot modify a validated attendance sheet.")
            )

        worker = self.env["res.partner"].search([("barcode", "=", barcode)])
        if not len(worker):
            raise UserError(_("Worker not found (invalid barcode or status)."))
        if len(worker) > 1:
            raise UserError(
                _("Multiple workers are corresponding this barcode.")
            )

        if worker.state in ("unsubscribed", "resigning"):
            raise UserError(_("Worker is %s.") % worker.state)
        if worker.working_mode not in ("regular", "irregular"):
            raise UserError(
                _("Worker is %s and should be regular or irregular.")
                % worker.working_mode
            )

        for id in self.expected_shift_ids.ids:
            shift = self.env["beesdoo.shift.sheet.expected"].browse(id)
            if (
                shift.worker_id == worker
                or shift.replacement_worker_id == worker
            ):
                shift.stage = "present"
                return

        if worker.working_mode == "regular":
            regular_task_type = "normal"
        else:
            regular_task_type = False

        added_ids = map(lambda s: s.worker_id.id, self.added_shift_ids)
        if worker.id in added_ids:
            raise UserError(_("Worker is already present."))

        self.added_shift_ids |= self.added_shift_ids.new(
            {
                "task_type_id": self.added_shift_ids._default_task_type_id(),
                "stage": "present",
                "attendance_sheet_id": self._origin.id,
                "worker_id": worker.id,
                "regular_task_type": regular_task_type,
            }
        )
