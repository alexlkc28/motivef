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

        verify = qb.validate_signature_header(http.request.httprequest.get_data(), headers['Intuit-Signature'])

        if verify:
            for event in data.get('eventNotifications'):
                if event.get('dataChangeEvent') and event.get('dataChangeEvent').get('entities'):
                    for entity in event.get('dataChangeEvent').get('entities'):
                        if entity.get('name') == 'Invoice':
                            qb.update_o_invoice(entity)
                        if entity.get('name') == 'Payment':
                            qb.update_o_invoice_from_payment(entity)

        return {'status': 200}
