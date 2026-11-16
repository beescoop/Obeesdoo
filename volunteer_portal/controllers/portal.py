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
            # Checking if connected partner is a volunteer
            volunteer = (
                request.env["volunteer.volunteer"]
                .sudo()
                .search([("partner_id", "=", request.env.user.partner_id.id)], limit=1)
            )

            # Security OK: retrieving volunteer's own participations count (values)
            values["volunteer_participation_count"] = (
                request.env["volunteer.shift.participation"]
                .sudo()
                .search_count([("volunteer_id", "=", volunteer.id)])
            )
        # TODO: Display counter if 0 participation
        return values

    # * All shift participations + cancel a participation and other possible POST forms

    @route(
        "/my/volunteer-shifts",
        type="http",
        auth="user",
        # header + footer
        website=True,
        methods=["GET", "POST"],
    )
    def my_volunteer_shifts(self, **kw):

        # SECURITY

        # Checking connected volunteer's ID (session)
        volunteer = (
            request.env["volunteer.volunteer"]
            .sudo()
            .search([("partner_id", "=", request.env.user.partner_id.id)], limit=1)
        )

        # If connected user is not a volunteer > not authorized
        if not volunteer:
            raise Forbidden(_("UNAUTHORIZED PAGE"))

        # Creating a shortcut variable to access records in the model
        Participation = request.env["volunteer.shift.participation"].sudo()

        # Filtering DB to only get connected volunteer's OWN data
        domain = [("volunteer_id", "=", volunteer.id)]

        # Creating a "now" variable for UTC
        now = fields.Datetime.now()

        # Errors and success catching to give the volunteer feedback
        errors = {}
        success = {}

        # POST

        if request.httprequest.method == "POST":

            # Cancel participation form handling
            if request.params.get("action") == "cancel_participation":

                # Checking that this participation exists / belongs to connected volunteer...
                participation = Participation.browse(
                    int(request.params.get("participation_id"))
                )

                # If not -> not authorized
                if (
                    not participation.exists()
                    or participation.volunteer_id.id != volunteer.id
                ):
                    raise Forbidden(_("UNAUTHORIZED PAGE"))

                # A participation is cancellable only if participation to shift is confirmed
                if participation.registration_state != "confirmed":
                    errors["cancel_participation"] = _(
                        "Your participation to this shift has already been canceled."
                    )

                # A participation is cancellable only if shift is upcoming / has not started
                elif participation.shift_start_time < now:
                    errors["cancel_participation"] = _(
                        "You cannot cancel a participation to a shift that has already started."
                    )

                else:

                    try:
                        # Cancel participation
                        participation.registration_state = "canceled"
                        success["cancel_participation"] = _(
                            "You successfully canceled your participation to this shift."
                        )

                    # ? Catching other errors, defined in model
                    except UserError:
                        errors["cancel_participation"] = _(
                            "Your participation to this shift could not be canceled."
                        )

            # elif request.params.get("action") == "other_form"
            # pass

        # GET

        # Filtering upcoming / past shifts participations
        upcoming_participations = Participation.search(
            domain + [("shift_start_time", ">=", now)], order="shift_start_time asc"
        )
        past_participations = Participation.search(
            domain + [("shift_start_time", "<", now)], order="shift_start_time desc"
        )

        values = {
            "upcoming_participations": upcoming_participations,
            "past_participations": past_participations,
            "now": now,
            "page_name": "volunteer_shifts",
            "success": success,
            "errors": errors,
        }
        # Rendering the template of all own shifts participations
        return request.render("volunteer_portal.my_shifts", values)

    # * Shift participation detail (ID already is an int in the URL)

    @route(
        "/my/volunteer-shifts/<int:participation_id>",
        type="http",
        auth="user",
        # header + footer
        website=True,
        methods=["GET", "POST"],
    )
    def my_shift_participation(self, participation_id, **kw):

        # SECURITY

        # Checking connected volunteer's ID (session)
        volunteer = (
            request.env["volunteer.volunteer"]
            .sudo()
            .search([("partner_id", "=", request.env.user.partner_id.id)], limit=1)
        )

        # If connected user is not a volunteer > not authorized
        if not volunteer:
            raise Forbidden(_("UNAUTHORIZED PAGE"))

        # Checking that this participation exists / belongs to connected volunteer...
        participation = (
            request.env["volunteer.shift.participation"].sudo().browse(participation_id)
        )

        # If not -> not authorized
        if not participation.exists() or participation.volunteer_id.id != volunteer.id:
            raise Forbidden(_("UNAUTHORIZED PAGE"))

        # Creating a "now" variable for UTC (not server local time)
        now = fields.Datetime.now()

        # Errors and success catching to give the volunteer feedback messages
        errors = {}
        success = {}

        # POST

        if request.httprequest.method == "POST":

            # Cancel participation form handling
            if request.params.get("action") == "cancel_participation":

                # A participation is cancellable only if shift participation is confirmed
                if participation.registration_state != "confirmed":
                    errors["cancel_participation"] = _(
                        "Your participation to this shift has already been canceled."
                    )

                # A participation is cancellable only if shift is upcoming / has not started
                elif participation.shift_start_time < now:
                    errors["cancel_participation"] = _(
                        "You cannot cancel a participation to a shift that has already started."
                    )

                else:

                    try:
                        # Cancel participation
                        participation.registration_state = "canceled"
                        success["cancel_participation"] = _(
                            "You successfully canceled your participation to this shift."
                        )

                    # ? Catching other errors, defined in model
                    except UserError:
                        errors["cancel_participation"] = _(
                            "Your participation to this shift could not be canceled."
                        )

            # elif request.params.get("action") == "other_form"
            # pass

        # GET

        values = {
            "participation": participation,
            "now": now,
            "page_name": "my_shift_participation",
            "success": success,
            "errors": errors,
        }
        # Rendering the template of all own shift participation
        return request.render("volunteer_portal.my_shift_participation", values)
