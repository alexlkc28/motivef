# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class AbkProductTemplate(models.Model):
    _inherit = 'product.template'

    product_specification = fields.Binary('Product Specification')
