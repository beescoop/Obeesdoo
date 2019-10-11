# -*- coding: utf-8 -*-
from openerp import models, fields

class AttendanceSheetShift(models.Abstract):
    _name = "beesdoo.shift.sheet_shift"
    _description = "Copy of an actual shift into an attendance sheet"

    # Related actual shift
    task_id = fields.Many2one("beesdoo.shift.shift", string ="Task")
    attendance_sheet_id = fields.Many2one("beesdoo.shift.sheet", string = "Attendance Sheet")
    status = fields.Selection([('present', 'Present'),
                                ('absent 0', 'Absent - 0 Compensation'),
                                ('absent 1', 'Absent - 1 Compensations'),
                                ('absent 2', 'Absent - 2 Compensations'),
                                ('cancelled', 'Cancelled')
                                ],
    string="Status", copy=False, default="not validated", track_visibility="onchange")
    # The worker should be editable for added shifts but not for expected ones.
    worker_id = fields.Many2One('res.partner', track_visibility='onchange',
                                domain=[
                                    ('eater', '=', 'worker_eater'),
                                    ('working_mode', 'in', ('regular', 'irregular')),
                                    ('state', 'not in', ('unsubscribed', 'resigning')),
                                ]))
    task_type_id = fields.Many2one('beesdoo.shift.type', string="Task Type")
    working_mode = fields.Selection(related='worker_id.working_mode', string="Working Mode")


class AttendanceSheetShiftExpected:
    _name = "beesdoo.shift.sheet_shift_expected"
    _description = "Expected Shift"
    _inherit = "beesdoo.shift.sheet_shift"

    replacement_worker_id = fields.Many2One('res.partner', string="Replacement worker")


class AttendanceSheetShiftAdded:
    _name = "beesdoo.shift.sheet_shift_added"
    _description = "Added Shift"
    _inherit = "beesdoo.shift.sheet_shift"

    # Change the previously determined string for a more comprehensive one
    is_regular = fields.Boolean(default=False, string="Normal shift")
    is_compensation = fields.Boolean(default=False, string="Compensation shift")


class AttendanceSheet(models.Model):
    _name = "beesdoo.shift.sheet"
    _inherit = ['mail.thread']
    _description = "The attendance sheets contains all the shifts for the \
    same hours and their attendance status."
    _order = 'start_time'

    state = fields.Selection([
    ('not validated', 'Not Validated'),
    ('validated', 'Validated'),
    ('cancelled', 'Cancelled')],
    string="Status", readonly=True, index=True, copy=False, default="not validated", track_visibility="onchange")

    day = fields.Datetime(string="Attendance Sheet Day", compute="_get_day")
    start_time = fields.Datetime(string="Attendance Sheet Start Time")
    end_time = fields.Datetime(string="Attendance Sheet End Time")

    task_template_ids = fields.One2many('beesdoo.shift.template', )
    expected_shift_ids = fields.One2many('beesdoo.shift.sheet_shift_expected', 'attendance_sheet_id', string="Expected Shifts")
    added_shift_ids = fields.One2many('beesdoo.shift.sheet_shift_added', 'attendance_sheet_id', string="Added Shifts")

    max_worker_nb = fields.Integer(string="Max number of workers", compute="_get_worker_nb", default=0,
        help="Indicative maximum number of workers for the shifts.")
    expected_worker_nb = fields.Integer(string="Expected Workers Number", compute="_get_expected_worker_nb", default=0)

    annotation = fields.Text("Attendance Sheet annotation")
    feedback = fields.Text("Attendance Sheet feedback")
    worker_nb_feedback = fields.Selection([
    ('not enough', 'Not Enough'),
    ('Enough', 'Enough'),
    ('too much', 'Fine')],
    string="Feedback concerning the number of workers")
    attended_worker_nb = fields.Integer(string="Attended Workers Number", default=0,
        help="Number of workers who attended the session.")

    @api.depends('start_time', 'end_time')
    def _get_day(self):

    @api.depends('expected_shift_ids')
    def _get_worker_nb(self):

    @api.depends('expected_shift_ids')
    def _get_expected_worker_nb(self):

    # Following method change the number of added shift displayed
    # on the  sheet. Should we add an attribute as well, filled after validation ?
    @api.onchange('added_shift_ids')
    def _onchange_added_shift_nb(self):

    def is_annotated(self):

    def validate(self):
