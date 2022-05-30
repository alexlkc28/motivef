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
import re
import base64
import hmac
import hashlib
import binascii

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
            'VERIFY_WEBHOOK_TOKEN': param.get_param('qbi.qk_webhook_token') or None,
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
        except:
            _logger.info('Refresh token error')

        _logger.info(auth_client)

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
            refresh_token=settings.get('REFRESH_TOKEN'),
        )

        return QuickBooks(
            auth_client=auth_client,
            refresh_token=settings.get('REFRESH_TOKEN'),
            company_id=settings.get('REALM_ID'),
        )

    def special_char(self, string):
        return re.sub('[^A-z0-9() -]', '', string).replace(" ", " ")

    def validate_signature_header(self, request_body, signature):
        settings = self.get_config()
        verifier_token = settings.get('VERIFY_WEBHOOK_TOKEN')
        # per quickbooks documentation
        # 1st step:
        #     hash the notification payload (request_body) with HMAC_SHA256_ALGORITHM
        #     using <verifier token> as the key
        request_body = request_body.encode()
        hmac_hex_digest = hmac.new(
            verifier_token,
            request_body,
            hashlib.sha256
        ).hexdigest()
        # 2nd step:
        #     convert the intuit-signature header from base-64 to base-16
        decoded_hex_signature = base64.b64decode(
            signature
        ).hex()
        # 3rd step
        # compare values from step 1 and 2
        return hmac_hex_digest == decoded_hex_signature

    def get_invoices(self, options=None):
        try:
            return Invoice.all(qb=self.get_client())
        except AuthorizationException as e:
            self.refresh()
            return Invoice.all(qb=self.get_client())
        except QuickbooksException as e:
            _logger.error(e.message)

    def create_or_update_customer(self, res_partner):
        _logger.info('Create Customer: ' + res_partner.name + ' - ' + str(res_partner.id))

        if res_partner.quickbooks_id:
            try:
                return Customer.get(res_partner.quickbooks_id, qb=self.get_client())
            except AuthorizationException as e:
                self.refresh()
                return Customer.get(res_partner.quickbooks_id, qb=self.get_client())

        # check Name
        cust_name = self.special_char(str(res_partner.display_name))
        try:
            customers = Customer.filter(DisplayName=cust_name, qb=self.get_client())
        except AuthorizationException as e:
            self.refresh()
            customers = Customer.filter(DisplayName=cust_name, qb=self.get_client())

        for customer in customers:
            res_partner.write({'quickbooks_id': customer.Id})
            return customer

        customer = Customer()

        if res_partner.x_studio_last_name:
            customer.Title = res_partner.x_studio_last_name
        else:
            word_list = res_partner.name.split()
            customer.Title = word_list[-1]

        if res_partner.x_studio_first_name:
            customer.GivenName = res_partner.x_studio_first_name

        if res_partner.x_studio_last_name:
            customer.FamilyName = res_partner.x_studio_last_name
        else:
            customer.FamilyName = res_partner.name

        if res_partner.x_studio_preferred_name:
            customer.FullyQualifiedName = res_partner.x_studio_preferred_name

        if res_partner.x_studio_related_company_chinese:
            customer.CompanyName = res_partner.x_studio_related_company_chinese

        customer.MiddleName = ''
        customer.Suffix = res_partner.title.name
        customer.DisplayName = cust_name

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
            customer.save(qb=self.get_client())
            res_partner.write({'quickbooks_id': customer.Id})
            return customer
        except AuthorizationException as e:
            self.refresh()
            customer.save(qb=self.get_client())
            res_partner.write({'quickbooks_id': customer.Id})
            return customer
        except QuickbooksException as e:
            _logger.error('[ERROR] Create Customer: ' + e.message + ' --> ' + e.detail)
            return None

    def create_or_update_item(self, o_pro):
        _logger.info('Create Item: ' + str(o_pro.name) + ' ' + str(o_pro.id))

        if o_pro.quickbooks_id:
            try:
                return Item.get(o_pro.quickbooks_id, qb=self.get_client())
            except AuthorizationException as e:
                self.refresh()
                return Item.get(o_pro.quickbooks_id, qb=self.get_client())

        # check name
        pro_name = self.special_char(str(o_pro.name))
        try:
            items = Item.filter(Name=pro_name, qb=self.get_client())
        except AuthorizationException as e:
            self.refresh()
            items = Item.filter(Name=pro_name, qb=self.get_client())

        if items:
            for item in items:
                o_pro.write({'quickbooks_id': str(item.Id)})
                return item

        item = Item()

        str_format = 'Odoo' + "{0:09d}"
        sku = str_format.format(int(o_pro.id))

        item.Name = pro_name
        item.Type = "Inventory"
        item.TrackQtyOnHand = False
        item.QtyOnHand = 10000
        item.Sku = sku

        today = date.today()
        item.InvStartDate = today.strftime("%Y-%m-%d")

        settings = self.get_config()
        if not settings.get('INCOME_ACCOUNT') or not settings.get('EXPENSE_ACCOUNT') or not settings.get(
                'ASSET_ACCOUNT'):
            return None

        income_account = Account.get(settings.get('INCOME_ACCOUNT'), qb=self.get_client())
        expense_account = Account.get(settings.get('EXPENSE_ACCOUNT'), qb=self.get_client())
        asset_account = Account.get(settings.get('ASSET_ACCOUNT'), qb=self.get_client())

        item.IncomeAccountRef = income_account.to_ref()
        item.ExpenseAccountRef = expense_account.to_ref()
        item.AssetAccountRef = asset_account.to_ref()

        try:
            item.save(qb=self.get_client())
            o_pro.write({'quickbooks_id': item.Id})
            return item
        except AuthorizationException as e:
            self.refresh()
            item.save(qb=self.get_client())
            o_pro.write({'quickbooks_id': item.Id})
            return item
        except QuickbooksException as e:
            _logger.error('[ERROR] Create Item: ' + e.message + ' --> ' + e.detail)
            return None

    def create_qb_invoice(self, o_inv):
        _logger.info('Create Invoice: ' + o_inv.name + ' - ' + str(o_inv.id))

        # get invoice
        invoice = Invoice()
        invalid = False

        for inv_line in o_inv.invoice_line_ids:
            if inv_line.product_id and inv_line.product_id.id:
                line = SalesItemLine()
                line.LineNum = inv_line.sequence
                line.Description = inv_line.name
                line.Amount = inv_line.price_subtotal

                line.SalesItemLineDetail = SalesItemLineDetail()
                line.SalesItemLineDetail.UnitPrice = inv_line.price_subtotal / inv_line.quantity
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
            invoice.save(qb=self.get_client())
            o_inv.write({'quickbooks_id': invoice.Id})
            return invoice
        except AuthorizationException as e:
            self.refresh()
            invoice.save(qb=self.get_client())
            o_inv.write({'quickbooks_id': invoice.Id})
            return invoice
        except QuickbooksException as e:
            _logger.error('[ERROR] Create Invoice: ' + e.message + ' --> ' + e.detail)
            return None

    def push_invoices_to_qb(self, limit=20):
        o_invs = self.env['account.move'].search([('quickbooks_id', '=', None),('state', '=', 'posted')], limit=limit)
        for o_inv in o_invs:
            if not o_inv.quickbooks_id:
                self.create_qb_invoice(o_inv)

    def update_o_invoice(self, data):
        _logger.info(data)
