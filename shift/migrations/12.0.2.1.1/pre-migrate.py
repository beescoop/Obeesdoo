def migrate(cr, version):
    # Renamed parameters, delete old names
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='shift.min_percentage_presence';"
    )
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='shift.regular_next_shift_limit';"
    )
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='beesdoo_website_shift.shift_period';"
    )
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='shift.max_shift_per_day';"
    )
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='shift.max_shift_per_month';"
    )
