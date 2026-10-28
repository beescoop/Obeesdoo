
from odoo import http
from odoo.http import request
from odoo import fields 
#*PREVIOUS: from werkzeug.exceptions import Forbidden
#? difference with Odoo exception AccessError?
#* translations, if we keep "raise Forbidden"
#* from odoo.tools.translate import _

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

# Little counter icon - inheriting class from "portal" Odoo module
class VolunteerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        # super() retrieves the dictionary (values) containing all basics data from other Odoo apps (docs, invoices, projects,...).
        # Counters of all other Odoo apps on the portal
        values = super()._prepare_home_portal_values(counters)
        
        if "volunteer_participation_count" in counters:
            # Finding if connected partner is indeed a volunteer in our custom module user groups
            volunteer = request.env['volunteer.volunteer'].sudo().search([
                ('partner_id', '=', request.env.user.partner_id.id)
            ], limit=1)
            
            #* If yes, retrieving their own (id=id) participations count // search_count()  
            if volunteer:
                count = request.env["volunteer.shift.participation"].sudo().search_count(
                    [('volunteer_id', '=', volunteer.id)])
            else:
                count = 0
            values["volunteer_participation_count"] = count
            # values = all the counters for the connected user on their portal (not just shifts / volunteer module data)
        return values 
    
    #? GET (by default) on route to display all shifts' participations of connected volunteer 
    # (my/volunteer-shifts)
   
    # fct to redirect to own shifts participations when btn (defined in portal_template.xml) is clicked
    
    @http.route(
        # second part = paging management => if shifts are displayed on several pages
        ["/my/volunteer-shifts", "/my/volunteer-shifts/page/<int:page>"],
        type="http",
        auth="user",
        # header + footer
        website=True,
    )
    
    def my_volunteer_shifts(self, page=1, **kw):
          
        volunteer = request.env['volunteer.volunteer'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)], limit=1)
        
        #* anartemis test : filtering db to only get connected volunteer's OWN data
        domain = [('volunteer_id', '=', volunteer.id)] if volunteer else [('id', '=', 0)]
        
        #? OR
        #  if not volunteer or participation.volunteer_id.id != volunteer.id:
        #     raise Forbidden(_("UNAUTHORIZED PAGE.")

        # shortcut variable to access records / tables in the model / DB
        Participation = request.env["volunteer.shift.participation"].sudo()
    
        # Prepare pager data
        participation_count = Participation.search_count(domain)
        pager_data = portal_pager(
            url="/my/volunteer-shifts",
            total=participation_count,
            page=page,
            step=self._items_per_page,
        )
        # Recordset according to pager and domain filter + order (= "order by" in SQL) by start time, descending
        participations = Participation.search(domain, limit=self._items_per_page, offset=pager_data["offset"], order="shift_start_time desc")
        # Prepare template values
        values = self._prepare_portal_layout_values()
        values.update(
            {   
                "participations": participations,
                "page_name": "volunteer_shifts",
                "default_url": "/my/volunteer-shifts",
                "pager": pager_data,
            }
        )                                        
        return request.render("volunteer_portal.my_shifts", values)
    
    # =================================================================
    
    #? Display one shift participation for user (details - to be bettered: what info to display here and how)
    
    #! Book method does NOT work (doc + model) for security reasons (in the book, sec files for portal users are defined, here we decided to go through sudo()...)
    # @route(
    #     ["/my/volunteer-shifts/<model('volunteer.shift.participation'):doc>"],
    #     auth="user",
    #     website=True,
    # )
    # def portal_my_project(self, doc=None, **kw):
    #     return request.render(
    #         "volunteer_portal.volunteer_shift_participation_details",
    #         {"doc": doc},
    #     )
    
    #*Display one shift participation

    # Redirecting to own shifts participation detail when btn is clicked (linked to "shift name || "what shift?"" in template)
    
    @http.route(
        #? tried to use the record instance using model syntax passed to the method with the doc keyword argument => does not work: sends me an unauthorized and 'sudo() in controller is never accessed by Odoo.
        #? PREVIOUS ["/my/volunteer-shifts/<model('volunteer.shift.participation'):doc>"],
        ["/my/volunteer-shifts/<int:participation_id>"],
        type="http",
        auth="user",
        website=True,
        methods=["GET"], 
    )
    
    
    def volunteer_single_shift_participation(self, participation_id=None, **kw):
                                               #? PREVIOUS: doc=None   
                                               # doc=None = receives the registering of participation found via the URL
                                               # **kw : Retrieves all other optional parameters passed in the URL (like arguments after "?")  
        #!TOTEST: Verifying WHO is connected to the portal - is it a volunteer?
        volunteer = request.env["volunteer.volunteer"].sudo().search([("partner_id", "=", request.env.user.partner_id.id)], limit=1)
        # ...else => unauthorized / forbidden (403)
        if not volunteer:

            #*PREVIOUS: raise Forbidden(_("UNAUTHORIZED PAGE.")
            return request.render("volunteer_portal.portal_unauthorized_page", {"message": "UNAUTHORIZED PAGE"})
        
        # Checking that this participation belongs to connected volunteer...
        #? Recuperating participation_id with sudo and assigning it to "participation" variable 
        participation = request.env["volunteer.shift.participation"].sudo().browse(participation_id)
        
        # ...else => unauthorized / forbidden (403) 
        if not participation.exists() or participation.volunteer_id.id != volunteer.id:
            #*PREVIOUS: raise Forbidden(_("UNAUTHORIZED PAGE.")
            return request.render("volunteer_portal.portal_unauthorized_page", {"message": "UNAUTHORIZED PAGE"})

        # If security OK => display requested doc ("participation")
        return request.render(
            "volunteer_portal.volunteer_single_shift_participation", 
            {"participation": participation}
        )
        
    
    # ==============================================================================================================================
    
    #*Cancel one shift participation
    
    # Redirecting to shifts participation cancellation when submit btn in form (defined in portal_template.xml) is clicked
    
    @http.route(
        ["/my/volunteer-shifts/<int:participation_id>"],
        #? tried to use the record instance using model syntax passed to the method with the doc keyword argument => does not work: sends me an unauthorized and 'sudo() in controller is never accessed by Odoo.
        #? PREVIOUS ["/my/volunteer-shifts/<model('volunteer.shift.participation'):doc>"],
        type="http",
        auth="user",
        # Header + footer
        website=True,
        # Writing / modifying data in DB
        methods=["POST"], 
    )
    
    def cancel_shift_participation(self, participation_id=None,**kw):
                                         #? PREVIOUS: doc=None   
                                         # doc=None = receives the registering of participation found via the URL
                                         # **kw : Retrieves all other optional parameters passed in the URL (like arguments after "?")
        
        #!TOTEST: Verifying WHO is connected to the portal - is it a volunteer?
        
        volunteer = request.env["volunteer.volunteer"].sudo().search([("partner_id", "=", request.env.user.partner_id.id)],limit=1) 
    
        if not volunteer:
            #  else... 403
            #* PREVIOUS: raise Forbidden(_("UNAUTHORIZED PAGE.")
            return request.render("volunteer_portal.portal_unauthorized_page", {"message": "UNAUTHORIZED PAGE"})
        
        #? Recuperating participation_id with sudo and assigning it to "participation" variable 
        participation = request.env["volunteer.shift.participation"].sudo().browse(participation_id)
        
        #? Checking that this participation belongs to connected volunteer
        if not participation.exists() or participation.volunteer_id.id != volunteer.id:
            #  else... 403
            #* raise Forbidden(_("UNAUTHORIZED PAGE.")
            return request.render("volunteer_portal.portal_unauthorized_page", {"message": "UNAUTHORIZED PAGE"})
            
        #? Security checks OK => defining conditions for a shift participation to be cancellable (future & confirmed shifts only)
        if (
            participation.registration_state == "confirmed"
            and participation.shift_id.start_time >= fields.Datetime.now()
        ):
            # POST "cancel participation"
            participation.write({"registration_state": "canceled"})

            # Back to "My shifts" (URL param : shift participation canceled confirmation)
            return request.redirect("/my/volunteer-shifts?message=canceled")
        
        
        #! TOTEST If error (already canceled, too late)
        return request.redirect("/my/volunteer-shifts?message=error")
    

    # =================================================================


#TODO: registrater your participation to a shift form : 
    #         
    #         request.env["volunteer.shift.participation"].sudo().create({
    #             'shift_id': shift_id,
    #             'volunteer_id': volunteer.id,
    #             'registration_state': 'confirmed',
    #         })
