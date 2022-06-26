# Copyright 2017-2020 Coop IT Easy SCRLfs (http://coopiteasy.be)
#   Rémy Taymans <remy@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# Copyright 2017-2018 Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from itertools import groupby

from pytz import timezone, utc
from werkzeug.exceptions import Forbidden

from odoo import _, http
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

        if (
            irregular_enable_sign_up
            and self.user_can_subscribe()
            and shift
            and shift.state == "open"
            and shift.start_time > start_time_limit
            and not shift.worker_id
        ):
            shift.worker_id = cur_user.partner_id
            request.session["success_message"] = self.subscribe_success_message()
        else:
            request.session["error_message"] = self.subscribe_error_message()
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

    @http.route("/shift/compensation", auth="user", website=True)
    def get_next_shifts_for_compensation(self, **kw):
        """
        Display underpopulated available shifts for a regular worker to
        subscribe to a compensation shift.
        If argument "display_all" is provided in the URL, display all available
        shifts.
        """
        cur_user = request.env["res.users"].browse(request.uid)
        if not self.can_subscribe_compensation(cur_user.partner_id):
            raise Forbidden()

        display_all = False
        next_shifts = (
            request.env["beesdoo.shift.shift"]
            .sudo()
            .search(
                [
                    ("start_time", ">", datetime.now()),
                    ("worker_id", "=", False),
                    ("state", "=", "open"),
                ],
                order="start_time desc, task_template_id, task_type_id",
            )
        )
        if "display_all" not in kw:
            # Get only underpopulated shifts
            displayed_shifts = request.env["beesdoo.shift.shift"].sudo()
            min_percentage_presence = int(
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("min_percentage_presence")
            )
            for shift in next_shifts:
                nb_worker_wanted = shift.task_template_id.worker_nb
                if nb_worker_wanted:
                    nb_worker_present = (
                        nb_worker_wanted - shift.task_template_id.remaining_worker
                    )
                    percentage_presence = (nb_worker_present / nb_worker_wanted) * 100
                    if percentage_presence <= min_percentage_presence:
                        displayed_shifts |= shift
        else:
            displayed_shifts = next_shifts
            display_all = True

        # Create template context
        template_context = {}
        template_context.update(self.get_compensation_shift_grid(displayed_shifts))
        template_context["all_shifts"] = display_all

        return request.render(
            "beesdoo_website_shift.choose_compensation_shift",
            template_context,
        )

    @http.route(
        "/shift/compensation/<int:shift_id>/subscribe", auth="user", website=True
    )
    def subscribe_to_compensation_shift(self, shift_id=-1, **kw):
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)
        if not self.can_subscribe_compensation(cur_user.partner_id):
            raise Forbidden()

        # Get the shift
        shift = request.env["beesdoo.shift.shift"].sudo().browse(shift_id)

        if (
            shift
            and shift.state == "open"
            and shift.start_time > datetime.now()
            and not shift.worker_id
        ):
            shift.write(
                {
                    "worker_id": cur_user.partner_id.id,
                    "is_compensation": True,
                }
            )
            request.session["success_message"] = self.subscribe_success_message()
        else:
            request.session["error_message"] = self.subscribe_error_message()

        return request.redirect("/my/shift")

    @http.route("/shift/<int:shift_id>/unsubscribe", auth="user", website=True)
    def unsubscribe_to_shift(self, shift_id=-1, **kw):
        shift = request.env["beesdoo.shift.shift"].sudo().browse(shift_id)
        cur_user = request.env["res.users"].browse(request.uid)
        if shift:
            if (
                cur_user.partner_id != shift.worker_id
                or not shift.can_unsubscribe
                or (
                    shift.is_compensation
                    and not request.website.enable_unsubscribe_compensation
                )
                or (
                    cur_user.partner_id.working_mode == "irregular"
                    and not request.website.irregular_enable_unsubscribe
                )
            ):
                raise Forbidden()
            shift.write(
                {"is_regular": False, "is_compensation": False, "worker_id": False}
            )
            request.session["success_message"] = _(
                "You have been successfully unsubscribed."
            )
        else:
            request.session["error_message"] = _(
                "Unsubscription failed, impossible to find shift."
            )
        return request.redirect(kw["nexturl"])

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

        # Add feedback about the success or failure of operations
        template_context["display_message"] = False
        if "success_message" in request.session:
            template_context["display_message"] = True
            template_context["success_message"] = request.session.get("success_message")
            del request.session["success_message"]
        elif "error_message" in request.session:
            template_context["display_message"] = True
            template_context["error_message"] = request.session.get("error_message")
            del request.session["error_message"]

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

        cur_user = request.env["res.users"].browse(request.uid)

        template_context.update(self.my_shift_worker_status())
        template_context.update(self.my_shift_next_shifts())
        template_context.update(self.my_shift_past_shifts())
        template_context.update(
            {
                "task_templates": task_templates,
                "float_to_time": float_to_time,
                "compensation_ok": self.can_subscribe_compensation(cur_user.partner_id),
            }
        )

        # Add feedback about the success or failure of operations
        template_context["display_message"] = False
        if "success_message" in request.session:
            template_context["display_message"] = True
            template_context["success_message"] = request.session.get("success_message")
            del request.session["success_message"]
        elif "error_message" in request.session:
            template_context["display_message"] = True
            template_context["error_message"] = request.session.get("error_message")
            del request.session["error_message"]

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
            "week_days": self.get_week_days(),
            "nexturl": nexturl,
            "irregular_enable_sign_up": irregular_enable_sign_up,
        }

    def my_shift_next_shifts(self, partner=None):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_next_shifts' template
        """
        if not partner:
            # Get current user
            partner = request.env["res.users"].browse(request.uid).partner_id

        my_shifts = partner.sudo().get_next_shifts()

        subscribed_shifts = []
        for rec in my_shifts:
            subscribed_shifts.append(rec)

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

    def get_compensation_shift_grid(self, shifts):
        cur_user = request.env["res.users"].browse(request.uid)

        groupby_iter = groupby(
            shifts,
            lambda s: (s.task_template_id, s.start_time, s.task_type_id),
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

        displayed_shifts = []
        for keys, grouped_shifts in groupby_iter:
            task_template, start_time, task_type = keys
            shift_list = list(grouped_shifts)
            is_subscribed = any(
                (
                    sub_shift.task_template_id == task_template
                    and sub_shift.start_time == start_time
                    and sub_shift.task_type_id == task_type
                )
                for sub_shift in subscribed_shifts
            )
            if not is_subscribed:
                displayed_shifts.append(
                    DisplayedShift(
                        shift_list[0],
                        None,
                        None,
                        None,
                    )
                )

        shift_weeks = build_shift_grid(displayed_shifts)
        return {
            "shift_weeks": shift_weeks,
            "week_days": self.get_week_days(),
        }

    def can_subscribe_compensation(self, worker_id):
        """
        Return True if:
        - The user is regular
        - The user is not already subscribed to enough compensation shifts
        - The sum of the user's counters is negative
        - The user is not unsubscribed / exempted / resigning
        - Compensation subscription is enabled
        """
        status = worker_id.cooperative_status_ids
        counter = status.sr + status.sc
        nb_compensation_shift = (
            request.env["beesdoo.shift.shift"]
            .sudo()
            .search_count(
                [
                    ("worker_id", "=", worker_id.id),
                    ("is_compensation", "=", True),
                    ("start_time", ">", datetime.now()),
                ]
            )
        )
        return (
            worker_id.working_mode == "regular"
            and counter < 0
            and abs(counter) > nb_compensation_shift
            and worker_id.state not in ["unsubscribed", "exempted", "resigning"]
            and request.website.enable_subscribe_compensation
        )

    def get_week_days(self):
        return [
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday"),
        ]

    def subscribe_success_message(self):
        return _("Your subscription has succeded.")

    def subscribe_error_message(self):
        return _(
            "Your subscription has failed. Someone subscribed before you "
            "or the shift was deleted. Try again in a moment."
        )
