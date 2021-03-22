from odoo import http

#class BeesdooRegularSwitchShift(http.Controller):
#     @http.route('/beesdoo_regular_switch_shift/beesdoo_regular_switch_shift/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/beesdoo_regular_switch_shift/beesdoo_regular_switch_shift/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('beesdoo_regular_switch_shift.listing', {
#             'root': '/beesdoo_regular_switch_shift/beesdoo_regular_switch_shift',
#             'objects': http.request.env['beesdoo_regular_switch_shift.beesdoo_regular_switch_shift'].search([]),
#         })

#     @http.route('/beesdoo_regular_switch_shift/beesdoo_regular_switch_shift/objects/<model("beesdoo_regular_switch_shift.beesdoo_regular_switch_shift"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('beesdoo_regular_switch_shift.object', {
#             'object': obj
#         })


