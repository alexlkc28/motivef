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

        qb = http.request.env['quickbooks.quickbooks'].sudo()

        headers = http.request.httprequest.headers
        data = http.request.jsonrequest
        _logger.info(headers)
        _logger.info(data)

        body = http.request.httprequest.get_data()
        _logger.info(body)

        verify = qb.validate_signature_header(body, headers['Intuit-Signature'])
        _logger.info(verify)

        qb.update_o_invoice(data)

        return {'status': 200}
