from datetime import datetime, timedelta

from pytz import timezone, utc

from odoo import http
from odoo.fields import Datetime
from odoo.http import request

#from odoo.addons.beesdoo_shift.models.planning import float_to_time

class BeesdooRegularSwitchShift(http.Controller):
    def is_user_worker(self):
        user = request.env["res.users"].browse(request.uid)
        return user.partner_id.is_worker

    def is_user_irregular(self):
        user = request.env["res.users"].browse(request.uid)
        working_mode = user.partner_id.working_mode
        return working_mode == "irregular"

    def is_user_regular(self):
        user = request.env["res.users"].browse(request.uid)
        working_mode = user.partner_id.working_mode
        return working_mode == "regular"

    def user_can_subscribe(self, user=None):
        """Return True if a user can subscribe to a shift. A user can
        subiscribe if:
            * the user is an regular worker
            * the user is not unsubscribed
            * the user is not resigning
        """
        if not user:
            user = request.env["res.users"].browse(request.uid)
        return (
                user.partner_id.working_mode == "regular"
                and user.partner_id.state != "unsubscribed"
                and user.partner_id.state != "resigning"
        )
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
        cur_user = request.env["res.users"].browse(request.uid)
        user_tz = utc
        if cur_user.tz:
            user_tz = timezone(cur_user.tz)
        elif request.env.context["tz"]:
            user_tz = timezone(request.env.context["tz"])
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


    @http.route("/my/timeslot", auth="user", website=True)
    def my_timeslot(self, **kw):
        """
        Personal page for managing your shifts
        """
        if self.is_user_irregular():
            return "irregular user doesn't have access to bourse au shift"

        if self.is_user_regular():
            return request.render(
                "beesdoo_website_shift.my_shift_regular_worker",
                self.my_shift_regular_worker(),
            )
        if self.is_user_worker():
            return request.render(
                "beesdoo_website_shift.my_shift_new_worker", {}
            )

        return request.render("beesdoo_website_shift.my_shift_non_worker", {})

    def my_shift_regular_worker(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_regular_worker' template
        """
        # Create template context
        template_context = {}

        # Get all the task template
        template = request.env["beesdoo.shift.template"]
        task_templates = template.sudo().search(
            [], order="planning_id, day_nb_id, start_time"
        )

        template_context.update(self.my_shift_worker_status())
        template_context.update(self.my_shift_next_shifts())
        #template_context.update(
        #    {"task_templates": task_templates, "float_to_time": float_to_time}
        #)
        return template_context

    def my_shift_next_shifts(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_next_shifts' template
        """
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)

        # Get shifts where user is subscribed
        now = datetime.now()
        subscribed_shifts_rec = (
            request.env["beesdoo.shift.shift"]
                .sudo()
                .search(
                [
                    ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                    ("worker_id", "=", cur_user.partner_id.id),
                ],
                order="start_time, task_template_id, task_type_id",
                limit=1
            )
        )

        # Create a list of record in order to add new record to it later
        subscribed_shifts = []
        for rec in subscribed_shifts_rec:
            subscribed_shifts.append(rec)

        # In case of regular worker, we compute his fictive next shifts
        # according to the regular_next_shift_limit
        if self.is_user_regular():
            # Compute main shift
            nb_subscribed_shifts = len(subscribed_shifts)
            if nb_subscribed_shifts > 0:
                main_shift = (
                    request.env["beesdoo.shift.timeslots_date"]
                        .sudo()
                        .new(
                        {
                            "date": subscribed_shifts_rec.start_time,
                            "template_id" : subscribed_shifts_rec.task_template_id,

                        }
                    )
                )
            else:
                task_template = (
                    request.env["beesdoo.shift.template"]
                        .sudo()
                        .search(
                        [("worker_ids", "in", cur_user.partner_id.id)],
                        limit=1
                    )
                )
                my_shift = (
                    request.env["beesdoo.shift.shift"]
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
                date = my_shift.start_time
                main_shift = (
                    request.env["beesdoo.shift.timeslots_date"]
                    .sudo()
                    .new(
                        {
                            "date" : date,
                            "template_id" : task_template,

                        }
                    )
                )


            # Get config
            regular_next_shift_limit = request.website.regular_next_shift_limit
            shift_period = int(
                request.env["ir.config_parameter"]
                    .sudo()
                    .get_param("beesdoo_website_shift.shift_period")
            )

            for i in range(1,regular_next_shift_limit):
                # Create the fictive shift
                shift = main_shift.new()
                shift.template_id = main_shift.template_id
                # Set new date
                shift.date = self.add_days(
                    main_shift.date, days=i * shift_period
                )
                # Add the fictive shift to the list of shift
                subscribed_shifts.append(shift)

        return {
            "is_regular": self.is_user_regular(),
            "subscribed_shifts": subscribed_shifts,
        }

    def my_shift_worker_status(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_worker_status_*' template
        """
        cur_user = request.env["res.users"].browse(request.uid)
        return {"status": cur_user.partner_id.cooperative_status_ids}




