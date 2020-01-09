# coding: utf-8


def migrate(cr, version):
    """
        The Char field 'code' from shift stage is now a Selection Field
        named 'state'.
    """
    # Set new field state
    cr.execute(
        """
        UPDATE beesdoo_shift_shift
        SET state = old_code
    """
    )
    # Map new stage from corresponding old stage
    cr.execute(
        """
            UPDATE beesdoo_shift_shift
            SET state = 'absent_2'
            FROM res_partner
            WHERE beesdoo_shift_shift.worker_id = res_partner.id
                AND (
                    beesdoo_shift_shift.old_code = 'absent'
                    OR (
                        beesdoo_shift_shift.old_code = 'excused'
                        AND res_partner.working_mode = 'irregular'
                    )
                )
        """
    )
    cr.execute(
        """
            UPDATE beesdoo_shift_shift
            SET state = 'absent_1'
            FROM res_partner
            WHERE beesdoo_shift_shift.worker_id = res_partner.id
                AND beesdoo_shift_shift.old_code = 'excused'
                AND res_partner.working_mode = 'regular'
        """
    )
    cr.execute(
        """
            UPDATE beesdoo_shift_shift
            SET state = 'absent_0'
            FROM res_partner
            WHERE beesdoo_shift_shift.worker_id = res_partner.id
                AND beesdoo_shift_shift.old_code = 'excused_necessity'
        """
    )
    cr.execute(
        """
            UPDATE beesdoo_shift_shift
            SET state = 'absent_0'
            WHERE beesdoo_shift_shift.state = 'excused'
        """
    )
    cr.execute(
        """
            DELETE FROM beesdoo_shift_shift
            WHERE beesdoo_shift_shift.state = 'absent'
        """
    )

    # Drop temporary columns
    cr.execute("ALTER TABLE beesdoo_shift_shift DROP COLUMN old_code")
