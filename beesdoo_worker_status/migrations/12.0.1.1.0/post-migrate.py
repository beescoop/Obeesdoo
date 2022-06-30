# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


def migrate(cr, version):
    cr.execute(
        """
        UPDATE cooperative_status
        SET is_penalised_irregular = TRUE
        WHERE sr < 0
        """
    )
