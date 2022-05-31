from odoo import api, models


class TaskTemplate(models.Model):

    _inherit = "beesdoo.shift.template"

    @api.multi
    def _prepare_task_day(self):
        """
        Override _prepare_task_day() function to take
        into account all the changes.
        """
        shifts = super(TaskTemplate, self)._prepare_task_day()

        # Get all the changes
        exchanges = self.env["beesdoo.shift.swap"].search([])
        people_exchanges = self.env["beesdoo.shift.exchange"].search([])
        solidarity_offers = self.env["beesdoo.shift.solidarity.offer"].search([])
        solidarity_requests = self.env["beesdoo.shift.solidarity.request"].search([])

        template = {
            "initial": None,
            "exchange_modified": None,
            "solidarity_modified": None,
        }
        for shift in shifts:
            template["initial"] = shift["task_template_id"]
            for exchange in exchanges:
                if (
                    not shift["worker_id"]
                    and exchange.wanted_tmpl_dated_id.template_id.id
                    == shift["task_template_id"]
                    and shift["start_time"] == exchange.wanted_tmpl_dated_id.date
                ):
                    if template["initial"] != template["exchange_modified"]:
                        shift["worker_id"] = exchange.worker_id.id
                        shift["is_regular"] = True
                        template["exchange_modified"] = shift["task_template_id"]
                if (
                    exchange.worker_id.id == shift["worker_id"]
                    and shift["task_template_id"]
                    == exchange.exchanged_tmpl_dated_id.template_id.id
                    and shift["start_time"] == exchange.exchanged_tmpl_dated_id.date
                ):
                    shift["worker_id"] = False
                    shift["is_regular"] = False
            for record in people_exchanges:
                if (
                    shift["worker_id"] == record.first_request_id.worker_id.id
                    and record.first_request_id.exchanged_tmpl_dated_id.template_id.id
                    == shift["task_template_id"]
                    and shift["start_time"]
                    == record.first_request_id.exchanged_tmpl_dated_id.date
                ):
                    shift["worker_id"] = record.second_request_id.worker_id.id
                    shift["is_regular"] = True
                if (
                    shift["worker_id"] == record.second_request_id.worker_id.id
                    and shift["task_template_id"]
                    == record.second_request_id.exchanged_tmpl_dated_id.template_id.id
                    and shift["start_time"]
                    == record.second_request_id.exchanged_tmpl_dated_id.date
                ):
                    shift["worker_id"] = record.first_request_id.worker_id.id
                    shift["is_regular"] = True
            for request in solidarity_requests:
                if (
                    shift["worker_id"] == request.worker_id.id
                    and request.tmpl_dated_id
                    and shift["task_template_id"]
                    == request.tmpl_dated_id.template_id.id
                    and shift["start_time"] == request.tmpl_dated_id.date
                    and request.state != "cancelled"
                ):
                    shift["worker_id"] = False
                    shift["is_regular"] = False
            for offer in solidarity_offers:
                if (
                    not shift["worker_id"]
                    and shift["task_template_id"] == offer.tmpl_dated_id.template_id.id
                    and shift["start_time"] == offer.tmpl_dated_id.date
                    and offer.state != "cancelled"
                ):
                    if template["initial"] != template["solidarity_modified"]:
                        shift["worker_id"] = offer.worker_id.id
                        shift["is_regular"] = True
                        shift["solidarity_offer_ids"] = [(6, 0, offer.ids)]
                        template["solidarity_modified"] = shift["task_template_id"]
        return shifts
