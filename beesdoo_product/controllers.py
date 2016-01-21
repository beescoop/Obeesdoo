# -*- coding: utf-8 -*-
from openerp import http

# class BeesdooLabel(http.Controller):
#     @http.route('/beesdoo_product/beesdoo_product/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/beesdoo_product/beesdoo_product/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('beesdoo_product.listing', {
#             'root': '/beesdoo_product/beesdoo_product',
#             'objects': http.request.env['beesdoo_product.beesdoo_product'].search([]),
#         })

#     @http.route('/beesdoo_product/beesdoo_product/objects/<model("beesdoo_product.beesdoo_product"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('beesdoo_product.object', {
#             'object': obj
#         })