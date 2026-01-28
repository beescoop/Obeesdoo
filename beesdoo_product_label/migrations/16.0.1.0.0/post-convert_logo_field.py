# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


def convert_logo_field(env):
    # logo was a binary field in version 12.0, which is by default stored in
    # a column in the database. odoo 13.0 changed the default to use
    # attachments instead. the logo field has now been changed to an image
    # field (which inherits from binary), keeping the default of using
    # attachments. the column is still present at this stage, so all that is
    # needed is to read the data from the database and assign it to the field,
    # so that odoo stores it in an attachment. the data in the database is
    # base64-encoded, which is what odoo expects when assigning a value to an
    # image or binary field.
    env.cr.execute(
        """
        select id, logo
        from beesdoo_product_label
        where logo is not null
        """
    )
    rows = env.cr.fetchall()
    model = env["beesdoo.product.label"].with_context(active_test=False)
    for id, logo in rows:
        record = model.browse(id)
        record.logo = logo


@openupgrade.migrate()
def migrate(env, version):
    convert_logo_field(env)
