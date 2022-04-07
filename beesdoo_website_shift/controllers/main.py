# Copyright 2017-2020 Coop IT Easy SCRLfs (http://coopiteasy.be)
#   Rémy Taymans <remy@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# Copyright 2017-2018 Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from itertools import groupby

from pytz import timezone, utc

from odoo import http
from odoo.fields import Datetime
from odoo.http import request

from odoo.addons.beesdoo_shift.models.planning import float_to_time

from .shift_grid_utils import DisplayedShift, build_shift_grid


class WebsiteShiftController(http.Controller):
    def is_user_worker(self):
        user = request.env["res.users"].browse(request.uid).sudo()
        return user.partner_id.is_worker

    def is_user_irregular(self):
        user = request.env["res.users"].browse(request.uid).sudo()
        working_mode = user.partner_id.working_mode
        return working_mode == "irregular"

    def is_user_regular(self):
        user = request.env["res.users"].browse(request.uid).sudo()
        working_mode = user.partner_id.working_mode
        return working_mode == "regular"

    def is_user_regular_without_shift(self):
        user = request.env["res.users"].browse(request.uid).sudo()
        return not user.partner_id.subscribed_shift_ids.ids and self.is_user_regular()

    def is_user_exempted(self):
        user = request.env["res.users"].browse(request.uid).sudo()
        working_mode = user.partner_id.working_mode
        return working_mode == "exempt"

    def user_can_subscribe(self, user=None):
        """Return True if a user can subscribe to a shift. A user can
        subiscribe if:
            * the user is an irregular worker
            * the user is not unsubscribed
            * the user is not resigning
        """
        if not user:
            user = request.env["res.users"].browse(request.uid).sudo()
        return (
            user.partner_id.working_mode == "irregular"
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

    @http.route("/my/shift", auth="user", website=True)
    def my_shift(self, **kw):
        """
        Personal page for managing your shifts
        """
        if self.is_user_irregular():
            return request.render(
                "beesdoo_website_shift.my_shift_irregular_worker",
                self.my_shift_irregular_worker(nexturl="/my/shift"),
            )
        if self.is_user_regular_without_shift():
            return request.render(
                "beesdoo_website_shift.my_shift_regular_worker_without_shift",
                self.my_shift_regular_worker_without_shift(),
            )
        if self.is_user_regular():
            return request.render(
                "beesdoo_website_shift.my_shift_regular_worker",
                self.my_shift_regular_worker(),
            )
        if self.is_user_exempted():
            return request.render(
                "beesdoo_website_shift.my_shift_exempted_worker",
                self.my_shift_exempted_worker(),
            )
        if self.is_user_worker():
            return request.render("beesdoo_website_shift.my_shift_new_worker", {})

        return request.render("beesdoo_website_shift.my_shift_non_worker", {})

    @http.route("/shift/<int:shift_id>/subscribe", auth="user", website=True)
    def subscribe_to_shift(self, shift_id=-1, **kw):
        """
        Subscribe the current connected user into the given shift
        This is done only if :
            * shift sign up is authorised via configuration panel
            * the user can subscribe
            * the given shift exist
            * the shift status is open
            * the shift is free for subscription
            * the shift is starting after the time interval
            for attendance sheet generation defined in beesdoo_shift settings
        """
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)
        # Get the shift
        shift = request.env["beesdoo.shift.shift"].sudo().browse(shift_id)
        # Get config
        irregular_enable_sign_up = request.website.irregular_enable_sign_up
        # Set start time limit as defined in beesdoo_shift settings
        # TODO: Move this into the attendance_sheet module
        # setting = request.website.attendance_sheet_generation_interval
        start_time_limit = datetime.now()  # + timedelta(minutes=setting)
        request.session["success"] = False

        if (
            irregular_enable_sign_up
            and self.user_can_subscribe()
            and shift
            and shift.state == "open"
            and shift.start_time > start_time_limit
            and not shift.worker_id
        ):
            shift.worker_id = cur_user.partner_id
            request.session["success"] = True
        return request.redirect(kw["nexturl"])

    @http.route("/shift_irregular_worker", auth="public", website=True)
    def public_shift_irregular_worker(self, **kw):
        """
        Show a public access page that show all the available shifts for
        irregular worker.
        """
        nexturl = "/shift_irregular_worker"
        irregular_enable_sign_up = False

        # Create template context
        template_context = {}
        template_context.update(
            self.available_shift_irregular_worker(irregular_enable_sign_up, nexturl)
        )

        return request.render(
            "beesdoo_website_shift.public_shift_irregular_worker",
            template_context,
        )

    @http.route("/shift_template_regular_worker", auth="public", website=True)
    def public_shift_template_regular_worker(self, **kw):
        """
        Show a public access page that show all the available shift templates
        for regular worker.
        """
        # Get all the task template
        template = request.env["beesdoo.shift.template"]
        task_templates = template.sudo().search(
            [], order="planning_id, day_nb_id, start_time"
        )

        # Get config
        regular_highlight_rule = request.website.regular_highlight_rule

        task_tpls_data = []
        for task_tpl in task_templates:
            has_enough_workers = task_tpl.remaining_worker <= (
                task_tpl.worker_nb * regular_highlight_rule / 100
            )
            task_tpls_data.append((task_tpl, has_enough_workers))

        return request.render(
            "beesdoo_website_shift.public_shift_template_regular_worker",
            {"task_tpls_data": task_tpls_data, "float_to_time": float_to_time},
        )

    def my_shift_irregular_worker(self, nexturl=""):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_irregular_worker' template
        """
        # Get config
        irregular_enable_sign_up = request.website.irregular_enable_sign_up

        # Create template context
        template_context = {}

        template_context.update(self.my_shift_worker_status())
        template_context.update(self.my_shift_next_shifts())
        template_context.update(self.my_shift_past_shifts())
        template_context.update(
            self.available_shift_irregular_worker(
                irregular_enable_sign_up and self.user_can_subscribe(), nexturl
            )
        )

        # Add feedback about the success or the fail of the subscription
        template_context["back_from_subscription"] = False
        if "success" in request.session:
            template_context["back_from_subscription"] = True
            template_context["success"] = request.session.get("success")
            del request.session["success"]

        # Add setting for subscription allowed time
        # TODO: move this to the attendance_sheet module
        # subscription_time_limit = (
        #     request.website.attendance_sheet_generation_interval
        # )
        subscription_time_limit = 0
        template_context["subscription_time_limit"] = subscription_time_limit

        return template_context

    def my_shift_regular_worker_without_shift(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_regular_worker_without_shift' template
        """
        return self.my_shift_worker_status()

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
        template_context.update(self.my_shift_past_shifts())
        template_context.update(
            {"task_templates": task_templates, "float_to_time": float_to_time}
        )
        return template_context

    def my_shift_exempted_worker(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_exempted_worker' template
        """
        return self.my_shift_worker_status()

    def available_shift_irregular_worker(
        self, irregular_enable_sign_up=False, nexturl=""
    ):
        """
        Return template variables for
        'beesdoo_website_shift.available_shift_irregular_worker_grid'
        """
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)

        # Get all the shifts in the future with no worker
        shifts = (
            request.env["beesdoo.shift.shift"]
            .sudo()
            .search(
                [
                    ("start_time", ">", Datetime.now()),
                    ("worker_id", "=", False),
                    ("state", "=", "open"),
                ],
                order="task_template_id, start_time, task_type_id",
            )
        )

        # Get shifts where user is subscribed
        subscribed_shifts = (
            request.env["beesdoo.shift.shift"]
            .sudo()
            .search(
                [
                    ("start_time", ">", Datetime.now()),
                    ("worker_id", "=", cur_user.partner_id.id),
                ],
                order="task_template_id, start_time, task_type_id",
            )
        )

        # Get config
        highlight_rule_pc = request.website.highlight_rule_pc
        hide_rule = request.website.hide_rule / 100.0

        groupby_iter = groupby(
            shifts,
            lambda s: (s.task_template_id, s.start_time, s.task_type_id),
        )

        displayed_shifts = []
        for keys, grouped_shifts in groupby_iter:
            task_template, start_time, task_type = keys
            shift_list = list(grouped_shifts)
            # Compute available space
            free_space = len(shift_list)
            # Is the current user subscribed to this task_template
            is_subscribed = any(
                (
                    sub_shift.task_template_id == task_template
                    and sub_shift.start_time == start_time
                    and sub_shift.task_type_id == task_type
                )
                for sub_shift in subscribed_shifts
            )
            # Check the necessary number of worker based on the
            # highlight_rule_pc
            has_enough_workers = (
                free_space <= (task_template.worker_nb * highlight_rule_pc) / 100
            )
            if free_space >= task_template.worker_nb * hide_rule:
                displayed_shifts.append(
                    DisplayedShift(
                        shift_list[0],
                        free_space,
                        is_subscribed,
                        has_enough_workers,
                    )
                )

        shift_weeks = build_shift_grid(displayed_shifts)
        return {
            "shift_weeks": shift_weeks,
            "nexturl": nexturl,
            "irregular_enable_sign_up": irregular_enable_sign_up,
        }

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
            task_template = (
                request.env["beesdoo.shift.template"]
                .sudo()
                .search([("worker_ids", "in", cur_user.partner_id.id)], limit=1)
            )
            main_shift = (
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

            # Get config
            regular_next_shift_limit = request.website.regular_next_shift_limit
            shift_period = int(
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_website_shift.shift_period")
            )

            for i in range(1, regular_next_shift_limit - len(subscribed_shifts) + 1):
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
                subscribed_shifts.append(shift)

        return {
            "is_regular": self.is_user_regular(),
            "subscribed_shifts": subscribed_shifts,
        }

    def my_shift_past_shifts(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_past_shifts' template
        """
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)
        # Get config
        past_shift_limit = 0
        if self.is_user_irregular():
            past_shift_limit = request.website.irregular_past_shift_limit
        if self.is_user_regular():
            past_shift_limit = request.website.regular_past_shift_limit
        # Get shifts where user was subscribed
        now = datetime.now()
        if past_shift_limit > 0:
            past_shifts = (
                request.env["beesdoo.shift.shift"]
                .sudo()
                .search(
                    [
                        (
                            "start_time",
                            "<=",
                            now.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        ("worker_id", "=", cur_user.partner_id.id),
                    ],
                    order="start_time desc, task_template_id, task_type_id",
                    limit=past_shift_limit,
                )
            )
        else:
            past_shifts = (
                request.env["beesdoo.shift.shift"]
                .sudo()
                .search(
                    [
                        (
                            "start_time",
                            "<=",
                            now.strftime("%Y-%m-%d %H:%M:%S"),
                        ),
                        ("worker_id", "=", cur_user.partner_id.id),
                    ],
                    order="start_time desc, task_template_id, task_type_id",
                )
            )

        return {"past_shifts": past_shifts}

    def my_shift_worker_status(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_worker_status_*' template
        """
        cur_user = request.env["res.users"].browse(request.uid)
        return {"status": cur_user.partner_id.cooperative_status_ids}
