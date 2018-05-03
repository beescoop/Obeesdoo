# -*- coding: utf-8 -*-

# Copyright 2015-2016 Odoo S.A.
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017-2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from werkzeug.exceptions import Forbidden, NotFound

from openerp import http
from openerp.exceptions import AccessError, MissingError
from openerp.http import request

from openerp.addons.website_portal_v10.controllers.main import WebsiteAccount


class CooperatorWebsiteAccount(WebsiteAccount):

    @http.route()
    def account(self):
        """ Add POS Order to main account page """
        response = super(CooperatorWebsiteAccount, self).account()
        partner = request.env.user.partner_id

        pos_order_mgr = request.env['pos.order'].sudo()
        pos_order_count = pos_order_mgr.search_count([
            ('partner_id', 'in', [partner.commercial_partner_id.id]),
        ])

        response.qcontext.update({
            'pos_order_count': pos_order_count,
        })
        return response

    @http.route(
        ['/my/pos_order',
         '/my/pos_order/page/<int:page>'],
        type='http', auth="user", website=True)
    def portal_my_pos_order(self, page=1, date_begin=None,
                            date_end=None, **kw):
        """Render a page that lits the POS order of the connected user."""
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        pos_order_mgr = request.env['pos.order'].sudo()

        domain = [
            ('partner_id', 'in', [partner.commercial_partner_id.id]),
        ]

        if date_begin and date_end:
            domain += [('create_date', '>=', date_begin),
                       ('create_date', '<', date_end)]

        # count for pager
        pos_order_count = pos_order_mgr.search_count(domain)
        # pager
        pager = request.website.pager(
            url="/my/pos_order",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=pos_order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        pos_orders = pos_order_mgr.search(
            domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'date': date_begin,
            'pos_orders': pos_orders,
            'page_name': 'invoice',
            'pager': pager,
            'default_url': '/my/pos_order',
        })
        return request.website.render(
            'beesdoo_website_pos_order.portal_my_pos_order',
            values
        )

    @http.route(['/my/pos_order_receipt/pdf/<int:oid>'],
                type='http', auth="user", website=True)
    def get_pos_order_receipt(self, oid=-1):
        """Render the receipt for a POS order"""
        # Get the POS order and raise an error if the user
        # is not allowed to access to it or if the object is not found.
        partner = request.env.user.partner_id
        pos_order_mgr = request.env['pos.order'].sudo()
        pos_order = pos_order_mgr.browse(oid)
        try:
            if pos_order.partner_id != partner.commercial_partner_id:
                raise Forbidden()
        except AccessError:
            raise Forbidden()
        except MissingError:
            raise NotFound()
        # Get the pdf
        report_mgr = request.env['report'].sudo()
        pdf = report_mgr.get_pdf(
            pos_order,
            'point_of_sale.report_receipt'
        )
        filename = pos_order.pos_reference
        return self._render_pdf(pdf, filename)

    def _render_pdf(self, pdf, filename):
        """Render a http response for a pdf"""
        pdfhttpheaders = [
            ('Content-Disposition', 'inline; filename="%s.pdf"' % filename),
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf))
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)
