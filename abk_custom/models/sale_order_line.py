# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sequence = fields.Integer(compute='_compute_item_sequence', store=True, readonly=True)

    @api.depends('sequence', 'order_id')
    def _compute_item_sequence(self):
        for record in self:
            for order in record.mapped('order_id'):
                number = 1
                for line in order.order_line:
                    line.sequence = number
                    number += 1

    @api.onchange('product_id')
    def product_id_change(self):
        for record in self:
            for order in record.mapped('order_id'):
                number = 0
                for line in order.order_line:
                    line.sequence = number
                    number += 1

        return super().product_id_change()
