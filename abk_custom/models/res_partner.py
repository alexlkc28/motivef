# -*- coding: utf-8 -*-

from odoo import models, api, _, fields

import logging

_logger = logging.getLogger(__name__)


class AbkResPartner(models.Model):
    _inherit = 'res.partner'
