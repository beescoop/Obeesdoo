# coding: utf-8


def migrate(cr, version):
    """Fix bug occuring when trying to save a temporary exempt
     (missing sequence in database). """
    cr.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS beesdoo_website_shift_config_settings_id_seq
        """
    )
    cr.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS beesdoo_shift_temporary_exemption_id_seq
        """
    )
