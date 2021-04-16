from odoo import models, fields, api
from datetime import datetime, timedelta

class TimeslotsDate(models.Model):
    _name = 'beesdoo.shift.timeslots_date'

    date = fields.Datetime(required = True)
    template_id = fields.Many2one("beesdoo.shift.template")
    #shift_id = fields.Integer(compute='compute_shift')


    def swap_shift_to_timeslot(self,shift):
        timeslot= self.env["beesdoo.shift.timeslots_date"].create()
        timeslot.date = shift.start_time
        timeslot.template_id = shift.task_template_id

    @api.model
    def display_timeslot(self,my_timeslot):
        start_date = datetime.now()
        timeslot_rec = []
        template = self.env["beesdoo.shift.template"].search([])

        #generate timeslot of the shift already generated
        shift_generated = (self.env["beesdoo.shift.shift"].sudo().search([
            ("start_time", ">", start_date.strftime("%Y-%m-%d %H:%M:%S"))
        ],
        order="start_time, task_template_id, task_type_id"))
        first_shift = shift_generated[0]
        last_template = first_shift.task_template_id
        new_template = first_shift.task_template_id

        first_timeslot = self.env["beesdoo.shift.timeslots_date"].new()
        first_timeslot.template_id = first_shift.task_template_id
        first_timeslot.date = first_shift.start_time
        timeslot_rec.append((first_timeslot.template_id.name,first_timeslot.date))


        shift_generated_list = []
        for shift_rec in shift_generated :
            shift_generated_list.append(shift_rec)

        for i in range(0,len(shift_generated_list)) :
            if last_template != new_template :
                timeslot = self.env["beesdoo.shift.timeslots_date"].new()
                timeslot.template_id = shift_generated_list[i].task_template_id
                timeslot.date = shift_generated_list[i].start_time
                timeslot_rec.append((timeslot.template_id.name,timeslot.date))
                new_template = shift_generated_list[i].task_template_id
            last_template = shift_generated_list[i].task_template_id

        #return timeslot_rec

        #now we have to generate timeslot of the shift that aren't generated

        #Get parameters

        #TODO : add system parameters of +2months
        shift_period = int(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_website_shift.shift_period")
        )
        end_date = my_timeslot.date + timedelta(days=2*shift_period)
        last_sequence = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("last_planning_seq")
        )
        #change 4 en allant chercher le nombre de planning
        #utiliser get_next_planning
        next_planning_nb = (last_sequence % 4) + 1
        next_planning = self.env["beesdoo.shift.planning"].search([
            ("sequence" , "=" , next_planning_nb)
        ])
        #TODO :check if we have one records for last_planning
        templates = self.env["beesdoo.shift.template"].search(
            [
            ("planning_id","=",next_planning.id),
            ],
            order="day_nb_id" ,
        )

        next_planning_date = datetime.strptime(
            self.env["ir.config_parameter"].sudo().get_param("next_planning_date"),
            '%Y-%m-%d'
        )

        return timeslot_rec






    
