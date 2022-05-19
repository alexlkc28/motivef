# -*- coding: utf-8 -*-

import logging
import io

from odoo import models, api, _
from PyPDF2 import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


class ABKIRActionReport(models.Model):
    _inherit = 'ir.actions.report'

    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        if self.model == 'sale.order' and res_ids and len(res_ids) == 1:
            so = self.env['sale.order'].browse(res_ids)
            _logger.info(so)
            _logger.info(so.order_line)
            # Add attachment.
            # reader_buffer = io.BytesIO(pdf_content)
            # reader = PdfFileReader(reader_buffer)
            # writer = PdfFileWriter()
            # writer.cloneReaderDocumentRoot(reader)
            # writer.addAttachment('factur-x.xml', xml_content)
            # buffer = io.BytesIO()
            # writer.write(buffer)
            # pdf_content = buffer.getvalue()
            #
            # reader_buffer.close()
            # buffer.close()

        return super(ABKIRActionReport, self)._post_pdf(save_in_attachment, pdf_content, res_ids)
