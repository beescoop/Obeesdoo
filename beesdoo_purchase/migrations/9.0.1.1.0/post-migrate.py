# coding: utf-8


def migrate(cr, version):
    """Set the new supervisor_id field if this one is empty."""
    cr.execute(
        """
        UPDATE purchase_order
        SET supervisor_id = create_uid
        WHERE supervisor_id IS NULL
        """
    )
