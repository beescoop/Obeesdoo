from odoo import models, fields, api
from datetime import datetime, timedelta
from pytz import timezone, utc

from odoo import _
from odoo.exceptions import UserError

class TaskTimeslot(models.Model):
    _inherit = "beesdoo.shift.shift"

    #TODO : mettre dans res.partner

    def add_days(self, datetime, days):
        """
        Add the number of days to datetime. This take the DST in
        account, meaning that the UTC time will be correct even if the
        new datetime has cross the DST boundary.
        :param datetime: a naive datetime expressed in UTC
        :return: a naive datetime expressed in UTC with the added days
        """
        # Ensure that the datetime given is without a timezone
        assert datetime.tzinfo is None
        # Get current user and user timezone
        # Take user tz, if empty use context tz, if empty use UTC
        cur_user = self.env["res.users"].browse(self.uid)
        user_tz = utc
        if cur_user.tz:
            user_tz = timezone(cur_user.tz)
        elif self.env.context["tz"]:
            user_tz = timezone(self.env.context["tz"])
        # Convert to UTC
        dt_utc = utc.localize(datetime, is_dst=False)
        # Convert to user TZ
        dt_local = dt_utc.astimezone(user_tz)
        # Add the number of days
        newdt_local = dt_local + timedelta(days=days)
        # If the newdt_local has cross the DST boundary, its tzinfo is
        # no longer correct. So it will be replaced by the correct one.
        newdt_local = user_tz.localize(newdt_local.replace(tzinfo=None))
        # Now the newdt_local has the right DST so it can be converted
        # to UTC.
        newdt_utc = newdt_local.astimezone(utc)
        return newdt_utc.replace(tzinfo=None)

    def my_shift_next(self,worker_id):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_next_shifts' template
        """
        # Get current user
        cur_user = self.env["res.users"].browse(worker_id)
        # Get shifts where user is subscribed
        now = datetime.now()
        subscribed_shifts_rec = (
            self.env["beesdoo.shift.shift"]
                .sudo()
                .search(
                [
                    ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                    ("worker_id", "=", cur_user.id.id),
                ],
                order="start_time, task_template_id, task_type_id",
            )
        )
        # Create a list of record in order to add new record to it later
        #subscribed_shifts = []
        subscribed_shifts = self.env["beesdoo.shift.shift"]
        for rec in subscribed_shifts_rec:
            subscribed_shifts |= rec

        # In case of regular worker, we compute his fictive next shifts
        # according to the regular_next_shift_limit
        if self.is_regular:
            # Compute main shift
            nb_subscribed_shifts = len(subscribed_shifts)
            if nb_subscribed_shifts > 0:
                main_shift = subscribed_shifts[-1]
            else:
                task_template = (
                    self.env["beesdoo.shift.template"]
                        .sudo()
                        .search(
                        [("worker_ids", "in", cur_user.id)], limit=1
                    )
                )
                main_shift = (
                    self.env["beesdoo.shift.shift"]
                        .sudo()
                        .search(
                        [
                            ("task_template_id", "=", task_template[0].id),
                            ("start_time", "!=", False),
                            ("end_time", "!=", False),
                        ],
                        order="start_time desc",
                        limit=1,
                    )
                )

            # Get config
            regular_next_shift_limit = self.website.regular_next_shift_limit
            shift_period = int(
                self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("beesdoo_website_shift.shift_period")
            )

            for i in range(nb_subscribed_shifts, regular_next_shift_limit):
                # Create the fictive shift
                shift = main_shift.new()
                shift.name = main_shift.name
                shift.task_template_id = shift.task_template_id
                shift.planning_id = main_shift.planning_id
                shift.task_type_id = main_shift.task_type_id
                shift.worker_id = main_shift.worker_id
                shift.state = "open"
                shift.super_coop_id = main_shift.super_coop_id
                shift.color = main_shift.color
                shift.is_regular = main_shift.is_regular
                shift.replaced_id = main_shift.replaced_id
                shift.revert_info = main_shift.revert_info
                # Set new date
                shift.start_time = self.add_days(
                    main_shift.start_time, days=i * shift_period
                )
                shift.end_time = self.add_days(
                    main_shift.end_time, days=i * shift_period
                )
                # Add the fictive shift to the list of shift
                subscribed_shifts |= shift

        return subscribed_shifts



class DatedTemplate(models.Model):
    _name = 'beesdoo.shift.template.dated'

    date = fields.Datetime(required = True)
    template_id = fields.Many2one("beesdoo.shift.template")
    #shift_id = fields.Integer(compute='compute_shift')

    @api.multi
    def name_get(self):
        data = []
        for timeslot in self:
            display_name = ''
            display_name += timeslot.template_id.name
            display_name += ', '
            display_name += str(timeslot.date)
            data.append((timeslot.id, display_name))
        return data


    def swap_shift_to_timeslot(self, list_shift):
        #timeslot_rec = []
        timeslot_rec = self.env["beesdoo.shift.template.dated"]
        first_shift = list_shift[0]
        last_template = first_shift.task_template_id
        new_template = first_shift.task_template_id
        last_date = first_shift.start_time
        new_date = first_shift.start_time

        first_timeslot = self.env["beesdoo.shift.template.dated"].new()
        first_timeslot.template_id = first_shift.task_template_id
        first_timeslot.date = first_shift.start_time
        #timeslot_rec.append((first_timeslot.template_id, first_timeslot.date))
        timeslot_rec |= first_timeslot

        shift_generated_list = []
        for shift_rec in list_shift:
            shift_generated_list.append(shift_rec)

        for i in range(0, len(shift_generated_list)):
            if last_template != new_template or last_date != new_date:
                timeslot = self.env["beesdoo.shift.template.dated"].new()
                yo = shift_generated_list[i].task_template_id
                timeslot.template_id = shift_generated_list[i].task_template_id
                timeslot.date = shift_generated_list[i].start_time
                #timeslot_rec.append((timeslot.template_id, timeslot.date))
                timeslot_rec |= timeslot
                new_template = shift_generated_list[i].task_template_id
                new_date = shift_generated_list[i].start_time
            last_template = shift_generated_list[i].task_template_id
            last_date = shift_generated_list[i].start_time


        shift_generated_list.clear()

        return timeslot_rec

    @api.model
    def display_timeslot(self,my_timeslot):

        start_date = datetime.now()

        #generate timeslot of the shift already generated

        shift_generated = (self.env["beesdoo.shift.shift"].sudo().search([
            ("start_time", ">", start_date.strftime("%Y-%m-%d %H:%M:%S"))
        ],
        order="start_time, task_template_id, task_type_id"))
        #timeslot_rec = []
        #timeslot_rec.append( self.swap_shift_to_timeslot(shift_generated))

        timeslot_rec = self.swap_shift_to_timeslot(shift_generated)

        # generate timeslot of the shift not generated
        last_sequence = int(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("last_planning_seq")
        )
        next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
        next_planning_date = fields.Datetime.from_string(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("next_planning_date", 0)
        )
        #TODO : create system parameters for end_date
        date = my_timeslot.date
        end_date = my_timeslot.date + timedelta(days=2*28)
        next_planning = next_planning.with_context(visualize_date=next_planning_date)
        shift_recset = self.env["beesdoo.shift.shift"]

        '''
        if not next_planning.task_template_ids:
            _logger.error(
                "Could not generate next planning: no task template defined."
            )
            return
        '''

        while next_planning_date < end_date :
            shift_recset = next_planning.task_template_ids._generate_task_day()
            #timeslot_rec.extend(self.swap_shift_to_timeslot(shift_recset))
            timeslot_rec |= self.swap_shift_to_timeslot(shift_recset)
            next_planning_date = next_planning._get_next_planning_date(next_planning_date)
            last_sequence = next_planning.sequence
            next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
            next_planning = next_planning.with_context(visualize_date=next_planning_date)

        return timeslot_rec


    #TODO: show my next timeslot/use myshift_next_shift + swap_shift_to_timeslot
    @api.model
    def my_timeslot(self,worker_id):
        shift = self.env["beesdoo.shift.shift"].my_shift_next(worker_id)
        timeslot = self.swap_shift_to_timeslot(shift)
        return timeslot
