# coding: utf-8


def migrate(cr, version):
    """Create a sequence for beesdoo_website_shift_config_settings."""
    cr.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS
        beesdoo_website_shift_config_settings_id_seq
        """
    )
