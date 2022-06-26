def migrate(cr, version):
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='beesdoo_shift.min_percentage_presence';"
    )
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='beesdoo_shift.regular_next_shift_limit';"
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
        "    key='beesdoo_shift.max_shift_per_day';"
    )
    cr.execute(
        "delete from "
        "    ir_config_parameter "
        "where "
        "    key='beesdoo_shift.max_shift_per_month';"
    )
