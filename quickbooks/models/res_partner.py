# -*- coding: utf-8 -*-

from odoo import models, api, _, fields


class UP5QuickBooksResPartner(models.Model):
    _inherit = 'res.partner'

    quickbooks_id = fields.Char('QuickBooks ID', store=True, readonly=True)
