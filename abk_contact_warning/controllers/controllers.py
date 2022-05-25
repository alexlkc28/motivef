# -*- coding: utf-8 -*-
# from odoo import http


# class AbkContactWarning(http.Controller):
#     @http.route('/abk_contact_warning/abk_contact_warning', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/abk_contact_warning/abk_contact_warning/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('abk_contact_warning.listing', {
#             'root': '/abk_contact_warning/abk_contact_warning',
#             'objects': http.request.env['abk_contact_warning.abk_contact_warning'].search([]),
#         })

#     @http.route('/abk_contact_warning/abk_contact_warning/objects/<model("abk_contact_warning.abk_contact_warning"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('abk_contact_warning.object', {
#             'object': obj
#         })
