# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class QBResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    qk_api_url = fields.Float(string='QuickBooks Api Url', store=True,
                              config_parameter="qbi.qk_api_url")
    qk_client_id = fields.Float(string='QuickBooks Client ID', store=True,
                                config_parameter="qbi.qk_client_id")
    qk_client_secret = fields.Float(string='QuickBooks Client Secret', store=True,
                                    config_parameter="qbi.qk_client_secret")
    qk_environment = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'Submitted')
    ], string='QuickBooks Environment', store=True,
        config_parameter="qki.qk_environment")
