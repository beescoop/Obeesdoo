# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request

from openerp.addons.easy_my_coop.controllers.main import WebsiteSubscription as Base

class WebsiteSubscription(Base):

    @http.route()
    def display_become_cooperator_page(self, **kwargs):
        response = (super(WebsiteSubscription, self)
                    .display_become_cooperator_page(**kwargs))
        cmp = request.env['res.company']._company_default_get()
        response.qcontext.update({
            'display_info_session': cmp.display_info_session_confirmation,
            'info_session_required': cmp.info_session_confirmation_required,
            'info_session_text': cmp.info_session_confirmation_text,
        })
        return response
