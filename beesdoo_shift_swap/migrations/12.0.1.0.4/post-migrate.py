from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set store value to True to avoid unwanted deletion
    solidarity_offers = env["beesdoo.shift.solidarity.offer"].search([])
    for offer in solidarity_offers:
        if offer.tmpl_dated_id:
            offer.tmpl_dated_id.store = True

    solidarity_requests = env["beesdoo.shift.solidarity.request"].search([])
    for request in solidarity_requests:
        if request.tmpl_dated_id:
            request.tmpl_dated_id.store = True

    # Clean wizards
    env.cr.execute("delete from beesdoo_shift_subscribe_shift_exchange *;")
    env.cr.execute("delete from beesdoo_shift_offer_solidarity_shift *;")
    env.cr.execute("delete from beesdoo_shift_request_solidarity_shift *;")
    env.cr.execute("delete from beesdoo_shift_subscribe_shift_swap *;")
