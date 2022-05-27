# -*- coding: utf-8 -*-

from odoo import models, api, _, fields
from datetime import date

from intuitlib.client import AuthClient
from intuitlib.exceptions import AuthClientError

from quickbooks import QuickBooks
from quickbooks.objects.base import Address, PhoneNumber, EmailAddress, CustomerMemo, Ref
from quickbooks.objects.customer import Customer
from quickbooks.objects.account import Account
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.item import Item
from quickbooks.objects.detailline import SalesItemLine, SalesItemLineDetail
from quickbooks.exceptions import AuthorizationException, QuickbooksException

import logging

_logger = logging.getLogger(__name__)


class UP5OdooQuickBooks(models.Model):
    _name = 'quickbooks.quickbooks'
    _description = 'QuickBooks Model'

    def get_config(self):
        param = self.env['ir.config_parameter'].sudo()
        return {
            'URL': param.get_param('qbi.qk_api_url') or None,
            'CLIENT_ID': param.get_param('qbi.qk_client_id') or None,
            'CLIENT_SECRET': param.get_param('qbi.qk_client_secret') or None,
            'ENVIRONMENT': param.get_param('qbi.qk_environment') or 'sandbox',
            'REALM_ID': param.get_param('qbi.qk_realm_id') or None,
            'ACCESS_TOKEN': param.get_param('qbi.qk_access_token') or None,
            'REFRESH_TOKEN': param.get_param('qbi.qk_refresh_token') or None,
            'ID_TOKEN': param.get_param('qbi.qk_id_token') or None,
            'REDIRECT_URL': param.get_param('web.base.url') + '/quickbooks/oauth-callback/',
            'INCOME_ACCOUNT': param.get_param('qbi.qk_income_account') or None,
            'EXPENSE_ACCOUNT': param.get_param('qbi.qk_expense_account') or None,
            'ASSET_ACCOUNT': param.get_param('qbi.qk_asset_account') or None,
        }

    def set_config(self, key, value):
        param = self.env['ir.config_parameter'].sudo()
        config_param = 'qbi.' + str(key)
        param.set_param(config_param, value)

    def refresh(self):
        settings = self.get_config()

        auth_client = AuthClient(
            settings.get('CLIENT_ID'),
            settings.get('CLIENT_SECRET'),
            settings.get('REDIRECT_URL'),
            settings.get('ENVIRONMENT'),
            access_token=settings.get('ACCESS_TOKEN'),
            refresh_token=settings.get('REFRESH_TOKEN'),
        )

        try:
            auth_client.refresh()
        except AuthClientError as e:
            _logger.info(e)

        self.set_config('qk_access_token', auth_client.access_token)
        self.set_config('qk_refresh_token', auth_client.refresh_token)

    def get_client(self, options=None):
        settings = self.get_config()

        auth_client = AuthClient(
            settings.get('CLIENT_ID'),
            settings.get('CLIENT_SECRET'),
            settings.get('REDIRECT_URL'),
            settings.get('ENVIRONMENT'),
            access_token=settings.get('ACCESS_TOKEN'),
        )

        return QuickBooks(
            auth_client=auth_client,
            refresh_token=settings.get('REFRESH_TOKEN'),
            company_id=settings.get('REALM_ID'),
        )

    def get_invoices(self, options=None):
        client = self.get_client()
        try:
            return Invoice.all(qb=client)
        except AuthorizationException as e:
            self.refresh()
            return Invoice.all(qb=client)
        except QuickbooksException as e:
            _logger.error(e.message)

    def create_or_update_customer(self, res_partner):
        _logger.info('Create Customer: ' + res_partner.name + ' - ' + str(res_partner.id))

        client = self.get_client()

        if res_partner.quickbooks_id:
            return Customer.get(res_partner.quickbooks_id, qb=client)

        customers = Customer.filter(DisplayName=res_partner.display_name, qb=client)
        for customer in customers:
            return customer

        customer = Customer()

        customer.Title = res_partner.name
        customer.GivenName = res_partner.x_studio_first_name or ''
        customer.MiddleName = ''
        customer.FamilyName = res_partner.x_studio_last_name or res_partner.name
        customer.Suffix = res_partner.title.name
        customer.FullyQualifiedName = res_partner.x_studio_preferred_name
        customer.CompanyName = res_partner.x_studio_related_company_chinese
        customer.DisplayName = res_partner.display_name

        customer.BillAddr = Address()
        customer.BillAddr.Line1 = res_partner.street
        customer.BillAddr.Line2 = res_partner.street2
        customer.BillAddr.City = res_partner.city
        customer.BillAddr.Country = res_partner.country_id.name
        customer.BillAddr.CountrySubDivisionCode = res_partner.country_id.code
        customer.BillAddr.PostalCode = res_partner.zip

        if res_partner.phone:
            customer.PrimaryPhone = PhoneNumber()
            customer.PrimaryPhone.FreeFormNumber = res_partner.phone

        if res_partner.email:
            customer.PrimaryEmailAddr = EmailAddress()
            customer.PrimaryEmailAddr.Address = res_partner.email

        # push
        try:
            customer.save(qb=client)
            res_partner.write({'quickbooks_id': customer.Id})
            return customer
        except QuickbooksException | Exception as e:
            _logger.error('[ERROR] Create Customer: ' + e.message)
            return None

    def create_or_update_item(self, o_pro):
        _logger.info('Create Item: ' + o_pro.name + ' ' + str(o_pro.id))

        client = self.get_client()

        if o_pro.quickbooks_id:
            return Item.get(o_pro.quickbooks_id, qb=client)

        item = Item()

        item.Name = o_pro.name
        item.Type = "Inventory"
        item.TrackQtyOnHand = False
        item.QtyOnHand = int(o_pro.free_qty)
        item.Sku = str(o_pro.code) or str(o_pro.id)

        _logger.info(str(item.QtyOnHand) + '/' + str(item.Sku))

        today = date.today()
        item.InvStartDate = today.strftime("%Y-%m-%d")

        settings = self.get_config()
        if not settings.get('INCOME_ACCOUNT') or not settings.get('EXPENSE_ACCOUNT') or not settings.get(
                'ASSET_ACCOUNT'):
            return None

        income_account = Account.get(settings.get('INCOME_ACCOUNT'), qb=client)
        expense_account = Account.get(settings.get('EXPENSE_ACCOUNT'), qb=client)
        asset_account = Account.get(settings.get('ASSET_ACCOUNT'), qb=client)

        item.IncomeAccountRef = income_account.to_ref()
        item.ExpenseAccountRef = expense_account.to_ref()
        item.AssetAccountRef = asset_account.to_ref()

        try:
            item.save(qb=client)
            o_pro.write({'quickbooks_id': item.Id})
            return item
        except QuickbooksException | Exception as e:
            _logger.error('[ERROR] Create Item: ' + e.message)
            return None

    def create_qb_invoice(self, o_inv):
        _logger.info('Create Invoice: ' + o_inv.name + ' - ' + str(o_inv.id))

        client = self.get_client()

        # get invoice
        invoice = Invoice()
        invalid = False

        for inv_line in o_inv.invoice_line_ids:
            line = SalesItemLine()
            line.LineNum = inv_line.sequence or 1
            line.Description = inv_line.name
            line.Amount = inv_line.price_subtotal

            line.SalesItemLineDetail = SalesItemLineDetail()
            line.SalesItemLineDetail.UnitPrice = inv_line.price_unit
            line.SalesItemLineDetail.Qty = inv_line.quantity

            item = self.create_or_update_item(inv_line.product_id)
            if not item:
                invalid = True
                break
            line.SalesItemLineDetail.ItemRef = item.to_ref()

            invoice.Line.append(line)

        if invalid:
            return None

        customer = self.create_or_update_customer(o_inv.partner_id)
        if not customer:
            return None
        invoice.CustomerRef = customer.to_ref()

        invoice.CustomerMemo = CustomerMemo()
        invoice.CustomerMemo.value = o_inv.name

        invoice.DocNumber = o_inv.name

        # push
        try:
            invoice.save(qb=client)
            o_inv.write({'quickbooks_id': invoice.Id})
            return invoice
        except QuickbooksException | Exception as e:
            _logger.error('[ERROR] Create Invoice: ' + e.message)
            return None

    def push_invoices_to_qb(self, limit=20):
        self.refresh()
        o_invs = self.env['account.move'].search([('quickbooks_id', '=', None),('state', '=', 'posted')], limit=limit)
        for o_inv in o_invs:
            if not o_inv.quickbooks_id:
                self.create_qb_invoice(o_inv)
