# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # This is an impossible scenario. It causes an endless loop bug that I'm not
    # able to debug exactly, but it's easier to just get rid of this scenario.
    sql = """
        UPDATE res_partner
        SET parent_eater_id = null
        WHERE eater = 'worker_eater'
    """
    openupgrade.logged_query(env.cr, sql)
