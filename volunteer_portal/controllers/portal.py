
#*PREVIOUS from odoo import http
from odoo.http import route
from odoo.http import request
from odoo import fields 
from werkzeug.exceptions import Forbidden
# Translations
from odoo.tools.translate import _

from odoo.addons.portal.controllers.portal import CustomerPortal

#!TODO: When a volunteer has no shifts participation, still display counter (now if 0 participation -> no counter...)

class VolunteerPortal(CustomerPortal):
    
    # Counters + badges - inherited class from "portal" Odoo module
    def _prepare_home_portal_values(self, counters):
        """Values for /my & /my/home routes template rendering.

        Includes the record count for the displayed badges.
        where 'counters' is the list of the displayed badges
        and so the list to compute.
        """
        # values = counters values of all other Odoo apps on the portal
        # super() retrieves the dictionary (values) containing all basics data from other Odoo apps (docs, invoices, projects,...).
        values = super()._prepare_home_portal_values(counters)
        # if portal requested 'shifts' badge, do the query
        if "volunteer_participation_count" in counters:
            # Security: checking if connected partner is indeed a volunteer in our custom module user groups
            volunteer = request.env['volunteer.volunteer'].sudo().search([
                ('partner_id', '=', request.env.user.partner_id.id)
            ], limit=1)

            # Security OK: retrieving volunteer's own participations count (values)
            values["volunteer_participation_count"] = request.env["volunteer.shift.participation"].sudo().search_count([('volunteer_id', '=', volunteer.id)])
    
        return values 
    
    #! -----------------------------------------------------------------------------------------------------------------------------------
    #* One route test for getting all participations, getting a participation detail, cancelling a participation and other possible POST forms
    
    @route(["/my/volunteer-shifts", "/my/volunteer-shifts/<int:participation_id>"],
           type="http",
           auth="user",
           # header + footer
           website=True,
           methods=["GET", "POST"])
    
                                # **kw : Retrieves all other optional parameters passed in the URL (like arguments after "?")  
                                # "None" because default URL has no ID
    def my_volunteer_shifts(self, participation_id=None, **kw):
        
        # Checking connected volunteer's ID (session)
        volunteer = request.env['volunteer.volunteer'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        
        # If connected user is not a volunteer > not authorized
        if not volunteer:
            raise Forbidden(_("UNAUTHORIZED PAGE"))
        
        # Creating a shortcut variable to access records in the model
        Participation = request.env["volunteer.shift.participation"].sudo()
        
        # Creating a "now" variable for UTC (not server local time), in order to split views correctly into "past shifts" & "future shifts"
        now = fields.Datetime.now()
        
        #* DETAIL
        
        if request.httprequest.method == "GET" and participation_id is not None:
            participation = Participation.browse(participation_id)
            # Checking that participation belongs to connected volunteer
            if not participation.exists() or participation.volunteer_id.id != volunteer.id:
                raise Forbidden(_("UNAUTHORIZED PAGE"))
            # Rendering the template of single shift participation detail
            return request.render("volunteer_portal.volunteer_single_shift_participation", {"participation" : participation})
        
        #* LIST ALL & POST
        
        # Filtering DB to only get connected volunteer's OWN data 
        domain = [('volunteer_id', '=', volunteer.id)] 
        
        # Errors and success catching to give the volunteer feedback
        errors = {}
        success = {}
        
        if request.httprequest.method == "POST":
            # Cancel participation form handling
            if request.params.get("action") == "cancel_participation":
                
                # id is a string, it must be a (valid) int
                participation_id_int = request.params.get("participation_id")
               
                participation = Participation.browse(int(participation_id_int)) if (participation_id_int or "").isdigit() else Participation
                
                
                # Checking that participation belongs to connected volunteer
                if not participation.exists() or participation.volunteer_id.id != volunteer.id:
                    raise Forbidden(_("UNAUTHORIZED PAGE"))
                
                
                # A participation is cancellable only if future & confirmed shift
                if  participation.registration_state == "confirmed" and participation.shift_id.start_time >= now:
                    
                    # Cancel participation
                    participation.registration_state = "canceled"
                    
                    success["cancel_participation"] = _("You successfully canceled your participation to this shift")
                else:
                    errors["cancel_participation"] = _("An error occurred while canceling participation to shift")   
                    
        #FORLATER elif request.params.get("action") == "other_form"
            # pass
            
            #TODO: register your participation to a shift form : 

    #         request.env["volunteer.shift.participation"].sudo().create({
    #             'shift_id': shift_id,
    #             'volunteer_id': volunteer.id,
    #             'registration_state': 'confirmed',
    #         })
    
    
        # GET 
        
        # Filtering future / past shifts participations
        future_participations = Participation.search(domain + [('shift_start_time', '>=', now)], order='shift_start_time asc')
        past_participations = Participation.search(domain + [('shift_start_time', '<', now)], order='shift_start_time desc')

        values = {
                
        "future_participations": future_participations,
        "past_participations": past_participations,
        "now": now,
        "page_name": "volunteer_shifts",
        "success" : success,
        "errors" : errors,
        }
        # Rendering the template of all own shifts participations
        return request.render("volunteer_portal.my_shifts", values)
    
    #! ------------------------------------------------------------------------------------------
        
    #*Display one shift participation - method with another route for the GET on part_id

    #!TOCHECK Single shift participation detail (ID already is an int in the URL) 
    # @route("/my/volunteer-shifts/<int:participation_id>",
    #     type="http",
    #     auth="user",
    #     # header + footer 
    #     website=True,
    #     methods=["GET"])
    
    # def my_single_shift_participation(self, participation_id, **kw):
                                                            
    #     # Checking connected volunteer's ID (session)
    #     volunteer = request.env["volunteer.volunteer"].sudo().search([("partner_id", "=", request.env.user.partner_id.id)], limit=1)
        
    #     # If connected user is not a volunteer -> unauthorized
    #     if not volunteer:
    #         raise Forbidden(_("UNAUTHORIZED PAGE"))
    #         #* PREVIOUS return request.render("volunteer_portal.portal_unauthorized_page", {"message": "UNAUTHORIZED PAGE"})
        
    #     # Checking that this participation exists / belongs to connected volunteer...
    #     participation = request.env["volunteer.shift.participation"].sudo().browse(participation_id)
        
    #     # If not -> unauthorized
    #     if not participation.exists() or participation.volunteer_id.id != volunteer.id:
    #         raise Forbidden(_("UNAUTHORIZED PAGE"))
    #         #* PREVIOUS return request.render("volunteer_portal.portal_unauthorized_page", {"message": "UNAUTHORIZED PAGE"})

    #     # Security OK -> display shift participation detail
    #     return request.render(
    #         "volunteer_portal.volunteer_single_shift_participation", 
    #         {"participation": participation}
    #     )
        



