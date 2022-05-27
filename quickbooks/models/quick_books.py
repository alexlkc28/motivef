# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class QuickBooks(models.Model):
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
        }

    def set_config(self, key, value):
        param = self.env['ir.config_parameter'].sudo()
        config_param = 'qbi.' + str(key)
        param.set_param(config_param, value)
