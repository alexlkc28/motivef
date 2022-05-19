# -*- coding: utf-8 -*-

import logging

from odoo import models, api, _

_logger = logging.getLogger(__name__)


class ABKIRActionReport(models.Model):
    _inherit = 'ir.actions.report'

    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        _logger.info(save_in_attachment)
        _logger.info(pdf_content)
        _logger.info(res_ids)
        result = super(ABKIRActionReport, self)._post_pdf(save_in_attachment, pdf_content, res_ids)
        return result
