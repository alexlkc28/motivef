# -*- coding: utf-8 -*-
from odoo import http

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError

import werkzeug
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
_logger = logging.getLogger(__name__)


class QuickBooksAuthController(http.Controller):
    @http.route('/quickbooks/oauth-login/', auth='user')
    def login(self, **kwargs):
        _logger.info('___________________________________oauth login')

        settings = http.request.env['quickbooks.quickbooks'].get_config()

        auth_client = AuthClient(
            settings.get('CLIENT_ID'),
            settings.get('CLIENT_SECRET'),
            settings.get('REDIRECT_URL'),
            settings.get('ENVIRONMENT'),
        )

        url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
        http.request.session['state'] = auth_client.state_token
        return werkzeug.utils.redirect(url)

    @http.route('/quickbooks/oauth-callback/', auth='user')
    def callback(self, **kwargs):
        _logger.info('___________________________________oauth callback')

        qb_env = http.request.env['quickbooks.quickbooks'].sudo()

        settings = qb_env.get_config()

        auth_client = AuthClient(
            settings.get('CLIENT_ID'),
            settings.get('CLIENT_SECRET'),
            settings.get('REDIRECT_URL'),
            settings.get('ENVIRONMENT'),
            state_token=http.request.session.get('state', None),
        )

        params = http.request.params

        state_tok = params.get('state', None)
        error = params.get('error', None)

        if error:
            return error

        if state_tok is None:
            return 'Bad Request'
        elif state_tok != auth_client.state_token:
            return 'Unauthorized'

        auth_code = params.get('code', None)
        realm_id = params.get('realmId', None)
        http.request.session['realm_id'] = realm_id

        if auth_code is None:
            return 'Bad Request'

        try:
            auth_client.get_bearer_token(auth_code, realm_id=realm_id)

            qb_env.set_config('qk_realm_id', realm_id)
            qb_env.set_config('qk_access_token', auth_client.access_token)
            qb_env.set_config('qk_refresh_token', auth_client.refresh_token)
            qb_env.set_config('qk_id_token', auth_client.id_token)
        except AuthClientError as e:
            # just printing status_code here but it can be used for retry workflows, etc
            _logger.info(e.status_code)
            _logger.info(e.content)
            _logger.info(e.intuit_tid)

            return e.content
        except Exception as e:
            _logger.info(e)
            return str(e)
        return 'Login Success!'
