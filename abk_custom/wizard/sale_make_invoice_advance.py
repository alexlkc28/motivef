# -*- coding: utf-8 -*-

import logging
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AbkSaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    # def _prepare_invoice_values(self, order, name, amount, so_lines):
    #     invoice_line_ids = []
    #     for so_line in so_lines:
    #         invoice_line_ids.append((0, 0, {
    #             'name': so_line.name,
    #             'price_unit': so_line.amount,
    #             'quantity': 1.0,
    #             'product_id': so_line.product_id.id,
    #             'product_uom_id': so_line.product_uom.id,
    #             'tax_ids': [(6, 0, so_line.tax_id.ids)],
    #             'sale_line_ids': [(6, 0, [so_line.id])],
    #             'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
    #             'analytic_account_id': order.analytic_account_id.id or False,
    #         }))
    #
    #     invoice_vals = {
    #         'ref': order.client_order_ref,
    #         'type': 'out_invoice',
    #         'invoice_origin': order.name,
    #         'invoice_user_id': order.user_id.id,
    #         'narration': order.note,
    #         'partner_id': order.partner_invoice_id.id,
    #         'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
    #         'partner_shipping_id': order.partner_shipping_id.id,
    #         'currency_id': order.pricelist_id.currency_id.id,
    #         'invoice_payment_ref': order.reference,
    #         'invoice_payment_term_id': order.payment_term_id.id,
    #         'invoice_partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
    #         'team_id': order.team_id.id,
    #         'campaign_id': order.campaign_id.id,
    #         'medium_id': order.medium_id.id,
    #         'source_id': order.source_id.id,
    #         'invoice_line_ids': invoice_line_ids,
    #     }
    #
    #     return invoice_vals
    #
    # def _prepare_so_lines(self, order, analytic_tag_ids, tax_ids, amount):
    #     so_lines = []
    #     for line in order.order_line:
    #         so_lines.append({
    #             'name': line.name,
    #             'price_unit': amount,
    #             'product_uom_qty': 0.0,
    #             'order_id': order.id,
    #             'discount': 0.0,
    #             'product_uom': line.product_id.uom_id.id,
    #             'product_id': line.product_id.id,
    #             'analytic_tag_ids': analytic_tag_ids,
    #             'tax_id': [(6, 0, tax_ids)],
    #             'is_downpayment': True,
    #         })
    #     return so_lines
    #
    # def create_invoices(self):
    #     sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
    #
    #     if self.advance_payment_method == 'delivered':
    #         sale_orders._create_invoices(final=self.deduct_down_payments)
    #     else:
    #         # Create deposit product if necessary
    #         if not self.product_id:
    #             vals = self._prepare_deposit_product()
    #             self.product_id = self.env['product.product'].create(vals)
    #             self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)
    #
    #         sale_line_obj = self.env['sale.order.line']
    #         for order in sale_orders:
    #             amount, name = self._get_advance_details(order)
    #
    #             if self.product_id.invoice_policy != 'order':
    #                 raise UserError(
    #                     _('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
    #             if self.product_id.type != 'service':
    #                 raise UserError(
    #                     _("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
    #             taxes = self.product_id.taxes_id.filtered(
    #                 lambda r: not order.company_id or r.company_id == order.company_id)
    #             if order.fiscal_position_id and taxes:
    #                 tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
    #             else:
    #                 tax_ids = taxes.ids
    #             context = {'lang': order.partner_id.lang}
    #             analytic_tag_ids = []
    #             for line in order.order_line:
    #                 analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
    #
    #             so_line_values = self._prepare_so_lines(order, analytic_tag_ids, tax_ids, amount)
    #             so_lines = []
    #             for line_vals in so_line_values:
    #                 so_line = sale_line_obj.create(line_vals)
    #                 so_lines.append(so_line)
    #             del context
    #             self._create_invoice(order, so_lines, amount)
    #     if self._context.get('open_invoices', False):
    #         return sale_orders.action_view_invoice()
    #     return {'type': 'ir.actions.act_window_close'}
