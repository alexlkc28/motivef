# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class AbkSaleOrder(models.Model):
    _inherit = 'sale.order'
