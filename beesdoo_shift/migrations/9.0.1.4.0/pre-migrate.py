# coding: utf-8


def migrate(cr, version):
    # Record information from old shift stage
    cr.execute('ALTER TABLE beesdoo_shift_shift ADD old_code varchar')
    cr.execute(
        """
        UPDATE beesdoo_shift_shift
        SET old_code = (
            SELECT code
            FROM beesdoo_shift_stage
            WHERE id = stage_id
        )
        """
    )
