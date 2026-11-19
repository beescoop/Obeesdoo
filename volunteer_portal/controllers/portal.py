from werkzeug.exceptions import Forbidden

from odoo import fields

# Exceptions
from odoo.exceptions import UserError
from odoo.http import request, route

# Translations
from odoo.tools.translate import _

from odoo.addons.portal.controllers.portal import CustomerPortal

# ? ValidationError handled by UserError.
# ? See: https://github.com/odoo/odoo/blob/16.0/odoo/exceptions.py


class VolunteerPortal(CustomerPortal):

    # Counters + badges - inherited class from "portal" Odoo module
    def _prepare_home_portal_values(self, counters):
        """Values for /my & /my/home routes template rendering.

        Includes the record count for the displayed badges.
        where 'counters' is the list of the displayed badges
        and so the list to compute.
        """
        # values = counters values of all other Odoo apps on the portal
        # super() retrieves dictionary (values) containing all data from other Odoo apps
        values = super()._prepare_home_portal_values(counters)
        # if portal requested 'shifts' badge, do the query
        if "volunteer_participation_count" in counters:
            volunteer = self._get_current_volunteer()

            # Security OK: retrieving volunteer's own participations count (values)
            values["volunteer_participation_count"] = (
                request.env["volunteer.shift.participation"]
                .sudo()
                .search_count([("volunteer_id", "=", volunteer.id)])
            )
        # TODO: Display counter if 0 participation
        return values

    # Definitions of private methods (helpers)

    def _get_current_volunteer(self):
        """The volunteer linked to the logged-in user, or "403"."""

        # Checking connected volunteer's ID (session)
        volunteer = (
            request.env["volunteer.volunteer"]
            .sudo()
            .search([("partner_id", "=", request.env.user.partner_id.id)], limit=1)
        )
        # If not a volunteer > not authorized
        if not volunteer:
            raise Forbidden(_("UNAUTHORIZED PAGE"))
        return volunteer

    def _get_own_participation(self, participation_id, volunteer):
        """The participation, if it exists, and belongs to the volunteer, or 403."""

        # Checking that this participation exists / belongs to connected volunteer...
        participation = (
            request.env["volunteer.shift.participation"].sudo().browse(participation_id)
        )
        # If not -> not authorized
        if not participation.exists() or participation.volunteer_id.id != volunteer.id:
            raise Forbidden(_("UNAUTHORIZED PAGE"))
        return participation

    def _cancel_participation(self, participation, now):
        """Apply the cancel participation logic. Returns (errors or success)."""

        # Errors and success catching to give the volunteer feedback messages
        errors, success = {}, {}
        # A participation is cancellable only if shift participation is confirmed
        if participation.registration_state != "confirmed":
            errors["cancel_participation"] = _(
                "Your participation to this shift has already been canceled."
            )
        # A participation is cancellable only if shift has not started
        # Constraint is not defined in models (if backend needsto change)
        elif participation.shift_start_time < now:
            errors["cancel_participation"] = _(
                "You cannot cancel a participation to a shift that has already started."
            )
        else:
            try:
                # Cancel participation
                participation.registration_state = "canceled"
                # TODO: Change either where message appear, or "this shift" by its date & name
                success["cancel_participation"] = _(
                    "You successfully canceled your participation to this shift."
                )

            # Catching other errors, defined in model
            except UserError:
                errors["cancel_participation"] = _(
                    "Your participation to this shift could not be canceled."
                )

        return errors, success

    # * All upcoming shift participations

    @route(
        "/my/upcoming-shifts",
        type="http",
        auth="user",
        # header + footer
        website=True,
        methods=["GET", "POST"],
    )
    def my_upcoming_shifts(self, **kw):
        """Get all connected volunteer's upcoming shift participations."""

        # SECURITY - Checking that the right user is logged-in
        volunteer = self._get_current_volunteer()
        # Creating a shortcut variable to access records in the model
        Participation = request.env["volunteer.shift.participation"].sudo()
        # Filtering DB to only get connected volunteer's OWN data
        domain = [("volunteer_id", "=", volunteer.id)]
        # Creating a "now" variable for UTC (not server local time)
        now = fields.Datetime.now()
        # Errors and success catching to give the volunteer feedback
        errors, success = {}, {}

        # POST
        if request.httprequest.method == "POST":
            # Cancel participation form handling
            if request.params.get("action") == "cancel_participation":
                # SECURITY - Checking that this participation belongs to this volunteer
                participation = self._get_own_participation(
                    int(request.params.get("participation_id")), volunteer
                )
                # Apply cancel participation or error
                errors, success = self._cancel_participation(participation, now)

            # elif request.params.get("action") == "other_form"
            # pass

        # GET

        # Upcoming shifts participations
        upcoming_participations = Participation.search(
            domain + [("shift_start_time", ">=", now)], order="shift_start_time asc"
        )
        values = {
            "upcoming_participations": upcoming_participations,
            "now": now,
            "page_name": "volunteer_shifts",
            "success": success,
            "errors": errors,
        }
        # Rendering the template of all own shifts participations
        return request.render("volunteer_portal.my_upcoming_shifts", values)

    # * All past shift participations

    @route(
        "/my/past-shifts",
        type="http",
        auth="user",
        # header + footer
        website=True,
        methods=["GET", "POST"],
    )
    def my_past_shifts(self, **kw):
        """Get all connected volunteer's past shift participations."""

        # SECURITY - Checking that the right user is logged-in
        volunteer = self._get_current_volunteer()
        # Creating a shortcut variable to access records in the model
        Participation = request.env["volunteer.shift.participation"].sudo()
        # Filtering DB to only get connected volunteer's own data
        domain = [("volunteer_id", "=", volunteer.id)]
        # Creating a "now" variable for UTC (not server local time)
        now = fields.Datetime.now()
        # Errors and success catching to give the volunteer feedback
        errors, success = {}, {}

        # if request.params.get("action") == "form"
        # pass

        # GET

        # Past shifts participations

        past_participations = Participation.search(
            domain + [("shift_start_time", "<", now)], order="shift_start_time desc"
        )

        values = {
            "past_participations": past_participations,
            "now": now,
            "page_name": "volunteer_shifts",
            "success": success,
            "errors": errors,
        }
        # Rendering the template of all own shifts participations
        return request.render("volunteer_portal.my_past_shifts", values)

    # * Shift participation detail (ID already is an int in the URL)

    @route(
        [
            "/my/upcoming-shifts/<int:participation_id>",
            "/my/past-shifts/<int:participation_id>",
        ],
        type="http",
        auth="user",
        # header + footer
        website=True,
        methods=["GET", "POST"],
    )
    def my_shift_participation(self, participation_id, **kw):
        """Get connected volunteer's single shift participation."""

        # SECURITY
        volunteer = self._get_current_volunteer()
        # Checking that this participation belongs to this volunteer
        participation = self._get_own_participation(participation_id, volunteer)
        # Creating a "now" variable for UTC (not server local time)
        now = fields.Datetime.now()
        # Errors and success catching to give the volunteer feedback
        errors, success = {}, {}

        # POST
        if request.httprequest.method == "POST":
            # Cancel participation form handling
            if request.params.get("action") == "cancel_participation":
                # Apply cancel participation or error
                errors, success = self._cancel_participation(participation, now)

        values = {
            "participation": participation,
            "now": now,
            "page_name": "my_shift_participation",
            "success": success,
            "errors": errors,
        }
        # Rendering the template of all own shifts participations
        return request.render("volunteer_portal.my_shift_participation", values)
