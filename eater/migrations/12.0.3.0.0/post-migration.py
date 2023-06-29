# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Parent and child eaters should be customers.
    sql = """
        UPDATE res_partner
        SET customer = true
        WHERE parent_eater_id IS NOT NULL OR id IN (
            SELECT parent_eater_id
            FROM res_partner
            WHERE parent_eater_id IS NOT NULL
        )
    """
    openupgrade.logged_query(env.cr, sql)
