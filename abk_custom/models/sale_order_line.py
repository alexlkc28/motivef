# -*- coding: utf-8 -*-

from odoo import models, api, _, fields
from odoo.tools.misc import get_lang

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

        return super(SaleOrderLine, self).product_id_change()

    def _prepare_invoice_line(self):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': 0,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.display_type:
            res['account_id'] = False
        return res
