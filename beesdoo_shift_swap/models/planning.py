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

        # Get all the changes and store them into a list to sort them
        changes = []

        swaps = self.env["beesdoo.shift.swap"].search(
            [
                ("state", "=", "validated"),
            ]
        )
        for swap in swaps:
            changes.append(swap)

        exchanges = self.env["beesdoo.shift.exchange"].search([])
        for exchange in exchanges:
            changes.append(exchange)

        solidarity_offers = self.env["beesdoo.shift.solidarity.offer"].search(
            [
                ("state", "=", "validated"),
            ]
        )
        for offer in solidarity_offers:
            changes.append(offer)

        solidarity_requests = self.env["beesdoo.shift.solidarity.request"].search(
            [
                ("state", "=", "validated"),
            ]
        )
        for request in solidarity_requests:
            changes.append(request)

        # Sort changes by creation date to evaluate them in the correct order
        changes.sort(key=lambda x: x.create_date)

        swap_subscription_done = []
        for shift in shifts:
            for rec in changes:
                class_name = rec.__class__.__name__
                if class_name == "beesdoo.shift.swap":
                    if (
                        not shift["worker_id"]
                        and rec.wanted_tmpl_dated_id.template_id.id
                        == shift["task_template_id"]
                        and shift["start_time"] == rec.wanted_tmpl_dated_id.date
                        and rec.id not in swap_subscription_done
                    ):
                        shift["worker_id"] = rec.worker_id.id
                        shift["is_regular"] = True
                        swap_subscription_done.append(rec.id)
                    if (
                        rec.worker_id.id == shift["worker_id"]
                        and shift["task_template_id"]
                        == rec.exchanged_tmpl_dated_id.template_id.id
                        and shift["start_time"] == rec.exchanged_tmpl_dated_id.date
                    ):
                        shift["worker_id"] = False
                        shift["is_regular"] = False
                elif class_name == "beesdoo.shift.exchange":
                    if (
                        shift["worker_id"] == rec.first_request_id.worker_id.id
                        and rec.first_request_id.exchanged_tmpl_dated_id.template_id.id
                        == shift["task_template_id"]
                        and shift["start_time"]
                        == rec.first_request_id.exchanged_tmpl_dated_id.date
                    ):
                        shift["worker_id"] = rec.second_request_id.worker_id.id
                        shift["is_regular"] = True
                    if (
                        shift["worker_id"] == rec.second_request_id.worker_id.id
                        and shift["task_template_id"]
                        == rec.second_request_id.exchanged_tmpl_dated_id.template_id.id
                        and shift["start_time"]
                        == rec.second_request_id.exchanged_tmpl_dated_id.date
                    ):
                        shift["worker_id"] = rec.first_request_id.worker_id.id
                        shift["is_regular"] = True
                elif class_name == "beesdoo.shift.solidarity.offer":
                    if (
                        not shift["worker_id"]
                        and shift["task_template_id"]
                        == rec.tmpl_dated_id.template_id.id
                        and shift["start_time"] == rec.tmpl_dated_id.date
                    ):
                        shift["worker_id"] = rec.worker_id.id
                        shift["is_regular"] = True
                        shift["solidarity_offer_ids"] = [(6, 0, rec.ids)]
                        changes.remove(rec)
                elif class_name == "beesdoo.shift.solidarity.request":
                    if (
                        shift["worker_id"] == rec.worker_id.id
                        and rec.tmpl_dated_id
                        and shift["task_template_id"]
                        == rec.tmpl_dated_id.template_id.id
                        and shift["start_time"] == rec.tmpl_dated_id.date
                    ):
                        shift["worker_id"] = False
                        shift["is_regular"] = False
                        changes.remove(rec)

        return shifts
