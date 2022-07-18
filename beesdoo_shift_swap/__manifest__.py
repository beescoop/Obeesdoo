# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Beesdoo Shift Swap",
    "summary": """
        Module to allow cooperator to swap his/her shift
        when he/she can't attend it, to do solidarity
        shifts, and to request solidarity if needed.""",
    "author": "Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative Management",
    "version": "12.0.2.0.0",
    "depends": [
        "beesdoo_shift",
    ],
    "data": [
        "data/system_parameter.xml",
        "data/cron.xml",
        "data/mail_template.xml",
        "security/ir.model.access.csv",
        "views/shift_swap.xml",
        "views/shift_swap_subscribe.xml",
        "views/shift_swap_tmpl_dated.xml",
        "views/res_config_setting_view.xml",
        "views/shift_swap_proposale.xml",
        "views/shift_swap_set.xml",
        "views/solidarity_shift_offer.xml",
        "views/solidarity_shift_request.xml",
        "views/task.xml",
        "views/res_partner.xml",
        "wizard/exchange_wizard.xml",
        "wizard/offer_solidarity.xml",
        "wizard/request_solidarity.xml",
        "wizard/subscribe_shift_as_solidarity.xml",
        "wizard/subscribe_shift_swap.xml",
        "wizard/validate_exchange.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "license": "AGPL-3",
}
