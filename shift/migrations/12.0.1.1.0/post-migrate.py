def migrate(cr, version):
    cr.execute(
        "update "
        "    beesdoo_shift_planning "
        "set "
        "    periodicity = templates.max "
        "from "
        "    ("
        "        select "
        "            MAX(day_nb_id) "
        "        from "
        "            beesdoo_shift_template "
        "    ) as templates;"
    )
