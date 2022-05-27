# -*- coding: utf-8 -*-

from odoo import models, api, _, fields


class UP5QuickBooksAccountMove(models.Model):
    _inherit = 'account.move'

    quickbooks_id = fields.Char('QuickBooks ID', store=True, readonly=True)
