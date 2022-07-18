# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

# undefined name 'env'
env = env  # noqa: F821

# Comments are there to prevent merge conflicts. Put the dictionary entry UNDER
# the comment of the respective module.
renamed_modules = {}

_logger.info("rename beesdoo_x modules")
openupgrade.update_module_names(env.cr, renamed_modules.items(), merge_modules=True)
env.cr.commit()
