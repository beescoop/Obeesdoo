def migrate(cr, version):
    cr.execute(
        "update "
        "    shift_planning "
        "set "
        "    periodicity = templates.max "
        "from "
        "    ("
        "        select "
        "            MAX(day_nb_id) "
        "        from "
        "            shift_template "
        "    ) as templates;"
    )
