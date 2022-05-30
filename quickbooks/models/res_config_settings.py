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

    qk_access_token = fields.Char(string='Access Token', store=True, config_parameter="qbi.qk_access_token")
    qk_refresh_token = fields.Char(string='Refresh Token', store=True, config_parameter="qbi.qk_refresh_token")
    qk_id_token = fields.Char(string='ID Token', store=True, config_parameter="qbi.qk_id_token")
    qk_realm_id = fields.Char(string='Realm ID', store=True, config_parameter="qbi.qk_realm_id")

    qk_redirect_url = fields.Char(string='Redirect Url', config_parameter="qbi.qk_redirect_url")

    qk_income_account = fields.Char('Income Account', store=True, config_parameter="qbi.qk_income_account")
    qk_expense_account = fields.Char('Expense Account', store=True, config_parameter="qbi.qk_expense_account")
    qk_asset_account = fields.Char('Asset Account', store=True, config_parameter="qbi.qk_asset_account")

    qk_webhook_token = fields.Char('Webhook Token', store=True, config_parameter="qbi.qk_webhook_token")

    @api.onchange('qk_client_id')
    def _onchange_qk_client_id(self):
        self.qk_redirect_url = self.env['ir.config_parameter'].get_param(
            'web.base.url') + '/quickbooks/oauth-callback/'

    def button_login_quickbooks(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/quickbooks/oauth-login/',
            'target': 'new',
        }

    def button_refresh_quickbooks(self):
        self.env['quickbooks.quickbooks'].refresh()
