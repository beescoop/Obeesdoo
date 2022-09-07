import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Make sure all cooperator types and can_shop are computed"""
    _logger.info("compute cooperator_type and can_shop on all partners.")
    env = api.Environment(cr, SUPERUSER_ID, {})
    partners = env["res.partner"].search([])
    partners._compute_cooperator_type()
    partners._compute_can_shop()
