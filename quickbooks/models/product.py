# -*- coding: utf-8 -*-

from odoo import models, api, _, fields


class UP5QuickBooksProduct(models.Model):
    _inherit = 'product.product'

    quickbooks_id = fields.Char('QuickBooks ID', store=True, readonly=True)
