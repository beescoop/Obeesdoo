# -*- coding: utf-8 -*-
from odoo import http

# class BeesdooBourseShift(http.Controller):
#     @http.route('/beesdoo_bourse_shift/beesdoo_bourse_shift/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/beesdoo_bourse_shift/beesdoo_bourse_shift/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('beesdoo_bourse_shift.listing', {
#             'root': '/beesdoo_bourse_shift/beesdoo_bourse_shift',
#             'objects': http.request.env['beesdoo_bourse_shift.beesdoo_bourse_shift'].search([]),
#         })

#     @http.route('/beesdoo_bourse_shift/beesdoo_bourse_shift/objects/<model("beesdoo_bourse_shift.beesdoo_bourse_shift"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('beesdoo_bourse_shift.object', {
#             'object': obj
#         })