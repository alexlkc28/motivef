# -*- coding: utf-8 -*-

import logging
import io
import base64

from odoo import models, api, _
from PyPDF2 import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


class ABKIRActionReport(models.Model):
    _inherit = 'ir.actions.report'

    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        if self.model == 'sale.order' and res_ids and len(res_ids) == 1:
            reader_buffer = io.BytesIO(pdf_content)
            reader = PdfFileReader(reader_buffer)

            writer = PdfFileWriter()
            writer.appendPagesFromReader(reader)

            so = self.env['sale.order'].browse(res_ids)
            for line in so.order_line:
                pdf_file = line.product_id.product_tmpl_id.product_specification
                if pdf_file:
                    file_reader = PdfFileReader(io.BytesIO(base64.b64decode(pdf_file)), strict=False,
                                                overwriteWarnings=False)
                    for page_num in range(0, file_reader.getNumPages()):
                        page_obj = file_reader.getPage(page_num)
                        writer.addPage(page_obj)

            buffer = io.BytesIO()
            writer.write(buffer)
            pdf_content = buffer.getvalue()

            reader_buffer.close()
            buffer.close()

        return super(ABKIRActionReport, self)._post_pdf(save_in_attachment, pdf_content=pdf_content, res_ids=res_ids)
