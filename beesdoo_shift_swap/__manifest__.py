{
    "name": "Beesdoo Shift Swap",
    "summary": """
        Module to allow cooperator to swap his/her shift
        when he/she can't attend it.""",
    "author": "Coop IT Easy SCRLfs",
    "website": "https://coopiteasy.be",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/
    #   odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Cooperative Management",
    "version": "12.0.1.0.2",
    # any module necessary for this one to work correctly
    "depends": [
        "beesdoo_shift",
    ],
    # always loaded
    "data": [
        "data/system_parameter.xml",
        "security/shift_swap_group.xml",
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
        "wizard/exchange_wizard.xml",
        "wizard/offer_solidarity.xml",
        "wizard/request_solidarity.xml",
        "wizard/Subscribe_shift_swap.xml",
        "wizard/validate_exchange.xml",
        "data/mail_template.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "license": "AGPL-3",
}
