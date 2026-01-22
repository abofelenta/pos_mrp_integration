# from odoo import http


# class PosMrpIntegration(http.Controller):
#     @http.route('/pos_mrp_integration/pos_mrp_integration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_mrp_integration/pos_mrp_integration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_mrp_integration.listing', {
#             'root': '/pos_mrp_integration/pos_mrp_integration',
#             'objects': http.request.env['pos_mrp_integration.pos_mrp_integration'].search([]),
#         })

#     @http.route('/pos_mrp_integration/pos_mrp_integration/objects/<model("pos_mrp_integration.pos_mrp_integration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_mrp_integration.object', {
#             'object': obj
#         })

