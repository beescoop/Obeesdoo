# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def cron_cleanup_procurement_order(self):
        running_procurement = self.env["procurement.order"].search(
            [("state", "=", "running")]
        )

        # checks if procurement order is done
        # -> if all moves are 'done' or 'cancel'
        _logger.info("check procurements in running state.")
        running_procurement.check()

        # in remaining procurement, cancel those with no procurement order
        unlinked_procurement = self.env["procurement.order"].search(
            [("state", "=", "running"), ("purchase_line_id", "=", False)]
        )
        _logger.info(
            "cancelling %s procurement unlinked from PO."
            % len(unlinked_procurement)
        )
        unlinked_procurement.cancel()

        # in remaining procurement, delete those from 'done' purchase order
        procurement_linked_to_done_PO = self.env["procurement.order"].search(
            [
                ("state", "=", "running"),
                ("purchase_line_id", "!=", False),
                ("purchase_line_id.order_id.state", "=", "done"),
            ]
        )
        _logger.info(
            "set %s procurement to done (linked to done PO)"
            % len(procurement_linked_to_done_PO)
        )
        procurement_linked_to_done_PO.write({"state": "done"})

        # cancel procurement order from exceptions
        # Refused by SPP - La Fève, overload this function in custom modules
        # to automate cleanup of exceptions

        # exception_procurement = self.env["procurement.order"].search(
        #     [("state", "=", "exception"), ("purchase_line_id", "=", False)]
        # )
        # _logger.info(
        #     "cancelling %s procurement in exception"
        #     % len(exception_procurement)
        # )
        # exception_procurement.cancel()
