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
        swaps = self.env["beesdoo.shift.swap"].search(
            [
                ("state", "=", "validated"),
            ]
        )
        exchanges = self.env["beesdoo.shift.exchange"].search([])
        solidarity_offers = self.env["beesdoo.shift.solidarity.offer"].search(
            [
                ("state", "=", "validated"),
            ]
        )
        solidarity_requests = self.env["beesdoo.shift.solidarity.request"].search(
            [
                ("state", "=", "validated"),
            ]
        )

        changes = (
            list(swaps)
            + list(exchanges)
            + list(solidarity_offers)
            + list(solidarity_requests)
        )

        # Sort changes by validation date to evaluate them in the correct order
        changes.sort(key=lambda x: x.get_validate_date())

        swap_subscription_done = []
        for shift in shifts:
            for rec in changes:
                shift, swap_subscription_done, done = rec.update_shift_data(
                    shift, swap_subscription_done
                )
                if done:
                    changes.remove(rec)

        return shifts
