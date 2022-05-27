# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class QBResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    qk_api_url = fields.Char(string='Api Url', store=True, config_parameter="qbi.qk_api_url")
    qk_client_id = fields.Char(string='Client ID', store=True, config_parameter="qbi.qk_client_id")
    qk_client_secret = fields.Char(string='Client Secret', store=True, config_parameter="qbi.qk_client_secret")
    qk_environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production')
    ], string='QuickBooks Environment', store=True, config_parameter="qki.qk_environment")

    access_token = fields.Char(string='Access Token', store=True, config_parameter="qbi.access_token")
    refresh_token = fields.Char(string='Refresh Token', store=True, config_parameter="qbi.refresh_token")
    id_token = fields.Char(string='ID Token', store=True, config_parameter="qbi.id_token")
    realm_id = fields.Char(string='Realm ID', store=True, config_parameter="qbi.realm_id")

    def button_login_quickbooks(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/quickbooks/oauth-login/',
            'target': 'new',
        }
