# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class AbkResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_address_format(self):
        return "%(street)s, %(street2)s %(city)s %(state_code)s %(zip)s, %(country_name)s"
