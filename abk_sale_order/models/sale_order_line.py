# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sequence = fields.Integer(compute='_compute_item_sequence', store=True)

    @api.depends('sequence', 'order_id')
    def _compute_item_sequence(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.number = number
                number += 1
