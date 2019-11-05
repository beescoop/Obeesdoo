# -*- coding: utf-8 -*-

def migrate(cr, version):
    if not version:
        return

    cr.execute("UPDATE res_company "
                "SET info_session_confirmation_required = FALSE "
                "WHERE display_info_session_confirmation = FALSE")
