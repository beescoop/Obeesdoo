# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.addons.web.http import Controller, route, request
from openerp.addons.web.controllers.main import (
    _serialize_exception,
    content_disposition,
)
from openerp.tools import html_escape

import json
import time
from werkzeug import url_decode
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.datastructures import Headers

from openerp.addons.report.controllers.main import ReportController
from openerp.tools.safe_eval import safe_eval


class ReportCustom(ReportController):
    @route(["/report/download"], type="http", auth="user")
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to trigger the download of
        a pdf/controller report.

        :param data: a javascript array JSON.stringified containg report internal url ([0]) and
        type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        try:
            if type == "qweb-pdf":
                reportname = url.split("/report/pdf/")[1].split("?")[0]

                docids = None
                if "/" in reportname:
                    reportname, docids = reportname.split("/")

                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter="pdf"
                    )
                else:
                    # Particular report:
                    data = url_decode(
                        url.split("?")[1]
                    ).items()  # decoding the args represented in JSON
                    response = self.report_routes(
                        reportname, converter="pdf", **dict(data)
                    )

                cr, uid = request.cr, request.uid
                report = request.registry["report"]._get_report_from_name(
                    cr, uid, reportname
                )
                filename = "%s.%s" % (report.name, "pdf")
                if docids:
                    ids = [int(x) for x in docids.split(",")]
                    obj = request.env[report.model].browse(ids)
                    if report.attachment and not len(obj) > 1:
                        filename = safe_eval(
                            report.attachment, {"object": obj, "time": time}
                        )
                response.headers.add(
                    "Content-Disposition", content_disposition(filename)
                )
                response.set_cookie("fileToken", token)
                return response
            elif type == "controller":
                reqheaders = Headers(request.httprequest.headers)
                response = Client(request.httprequest.app, BaseResponse).get(
                    url, headers=reqheaders, follow_redirects=True
                )
                response.set_cookie("fileToken", token)
                return response
            else:
                return
        except Exception as e:
            se = _serialize_exception(e)
            error = {"code": 200, "message": "Odoo Server Error", "data": se}
            return request.make_response(html_escape(json.dumps(error)))
