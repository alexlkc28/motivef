# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

from intuitlib.client import AuthClient
from intuitlib.exceptions import AuthClientError

from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.invoice import Invoice

import logging

_logger = logging.getLogger(__name__)


class UP5OdooQuickBooks(models.Model):
    _name = 'quickbooks.quickbooks'
    _description = 'QuickBooks Model'

    def get_config(self):
        param = self.env['ir.config_parameter'].sudo()
        return {
            'URL': param.get_param('qbi.qk_api_url') or None,
            'CLIENT_ID': param.get_param('qbi.qk_client_id') or None,
            'CLIENT_SECRET': param.get_param('qbi.qk_client_secret') or None,
            'ENVIRONMENT': param.get_param('qbi.qk_environment') or 'sandbox',
            'REALM_ID': param.get_param('qbi.qk_realm_id') or None,
            'ACCESS_TOKEN': param.get_param('qbi.qk_access_token') or None,
            'REFRESH_TOKEN': param.get_param('qbi.qk_refresh_token') or None,
            'ID_TOKEN': param.get_param('qbi.qk_id_token') or None,
            'REDIRECT_URL': param.get_param('web.base.url') + '/quickbooks/oauth-callback/'
        }

    def set_config(self, key, value):
        param = self.env['ir.config_parameter'].sudo()
        config_param = 'qbi.' + str(key)
        param.set_param(config_param, value)

    def refresh(self):
        settings = self.get_config()

        auth_client = AuthClient(
            settings.get('CLIENT_ID'),
            settings.get('CLIENT_SECRET'),
            settings.get('REDIRECT_URL'),
            settings.get('ENVIRONMENT'),
            access_token=settings.get('ACCESS_TOKEN'),
            refresh_token=settings.get('REFRESH_TOKEN'),
        )

        try:
            auth_client.refresh()
        except AuthClientError as e:
            _logger.info(e)

        self.set_config('qk_access_token', auth_client.access_token)
        self.set_config('qk_refresh_token', auth_client.refresh_token)

    def get_client(self, options=None):
        settings = self.get_config()

        auth_client = AuthClient(
            settings.get('CLIENT_ID'),
            settings.get('CLIENT_SECRET'),
            settings.get('REDIRECT_URL'),
            settings.get('ENVIRONMENT'),
            access_token=settings.get('ACCESS_TOKEN'),
            refresh_token=settings.get('REFRESH_TOKEN'),
        )

        return QuickBooks(
            auth_client=auth_client,
            refresh_token=settings.get('REFRESH_TOKEN'),
            company_id=settings.get('REALM_ID'),
        )

    def get_invoice(self, options=None):
        client = self.get_client()
        return Invoice.all(qb=client)

    def update_all_invoices(self):
        invoices = self.get_invoice()
        _logger.info(invoices)

        return True
