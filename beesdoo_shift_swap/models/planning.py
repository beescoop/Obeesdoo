from odoo import models, api

class TaskTemplate(models.Model):

    _inherit = "beesdoo.shift.template"

    @api.multi
    def _generate_task_day(self):
        """
        Override _generate_task_day() function to take
        into account all the exchange.
        :return: beesdoo.shift.shift new() object (not save in db)
        """
        shifts = super(TaskTemplate,self)._generate_task_day()

        #get all the exchanges
        exchanges = self.env["beesdoo.shift.subscribed_underpopulated_shift"].search([])
        people_exchanges = self.env["beesdoo.shift.exchange"].search([])

        template = {"initial" : None, "modified" : None}
        for shift in shifts :
            template["initial"] = shift.task_template_id
            for exchange in exchanges :
                if shift.worker_id.name == False and exchange.confirmed_tmpl_dated_id.template_id == shift.task_template_id and shift.start_time == exchange.confirmed_tmpl_dated_id.date:
                    if template["initial"] != template["modified"]:
                        updated_data = {
                            "worker_id": exchange.worker_id.id,
                            "is_regular": True,
                        }
                        shift.update(updated_data)
                        template["modified"] = shift.task_template_id
                if exchange.worker_id == shift.worker_id and shift.task_template_id == exchange.exchanged_tmpl_dated_id.template_id and shift.start_time == exchange.exchanged_tmpl_dated_id.date:
                    updated_data = {
                        "worker_id": False,
                        "is_regular": False,
                    }
                    shift.update(updated_data)
            for record in people_exchanges :
                if shift.worker_id == record.first_request_id.worker_id and record.first_request_id.exchanged_tmpl_dated_id.template_id == shift.task_template_id and shift.start_time == record.first_request_id.exchanged_tmpl_dated_id.date :
                    updated_data = {
                        "worker_id": record.second_request_id.worker_id.id,
                        "is_regular": True,
                    }
                    shift.update(updated_data)
                if shift.worker_id == record.second_request_id.worker_id and shift.task_template_id == record.second_request_id.exchanged_tmpl_dated_id.template_id and shift.start_time == record.second_request_id.exchanged_tmpl_dated_id.date :
                    updated_data = {
                        "worker_id": record.first_request_id.worker_id.id,
                        "is_regular": True,
                    }
                    shift.update(updated_data)
        return shifts
