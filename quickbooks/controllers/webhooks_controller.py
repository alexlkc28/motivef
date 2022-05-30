# -*- coding: utf-8 -*-
from odoo import http

import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_logger = logging.getLogger(__name__)


class QuickBooksWebhookController(http.Controller):
    @http.route('/quickbooks/webhooks/', auth='none', type='json', cors='*', csrf=False,
                method=['POST'], lover='quickbooks_webhooks')
    def webhooks(self, **kw):
        _logger.info('---------------------------- webhooks')

        headers = http.request.httprequest.headers
        data = http.request.jsonrequest

        settings = http.request.env['quickbooks.quickbooks'].get_config()

        _logger.info(headers)

        http.request.env['quickbooks.quickbooks'].sudo().update_o_invoice(data)
