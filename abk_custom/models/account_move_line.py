# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sequence = fields.Integer(compute='_compute_item_sequence', store=True, readonly=True)

    @api.depends('sequence', 'move_id')
    def _compute_item_sequence(self):
        for record in self:
            for move in record.mapped('move_id'):
                number = 1
                for line in move.invoice_line_ids:
                    line.sequence = number
                    number += 1

    @api.onchange('sequence')
    def _change_sequence(self):
        for record in self:
            record.sequence = 0
