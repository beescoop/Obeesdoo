import logging

from odoo import SUPERUSER_ID
from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # remove all users from group "Manage Packages" sometimes
    # translated as "Gérer les emplacements multiples
    # et les entrepôts"
    _logger.info(
        "removing all users from groups 'Manage Packages',"
        " 'Manage Multiple Stock Locations'"
        " and 'Manage Different Stock Owners'"
    )
    with Environment.manage():
        env = Environment(cr, SUPERUSER_ID, {})
    group_tracking_lot = env.ref("stock.group_tracking_lot")
    group_stock_multi_locations = env.ref("stock.group_stock_multi_locations")
    group_tracking_owner = env.ref("stock.group_tracking_owner")
    group_tracking_lot.users = [(5, 0, 0)]
    group_stock_multi_locations.users = [(5, 0, 0)]
    group_tracking_owner.users = [(5, 0, 0)]
