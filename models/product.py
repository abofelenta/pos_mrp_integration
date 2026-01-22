from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacture_from_pos = fields.Boolean(
        string="Manufacture from POS",
        help="If enabled, selling this product in POS will create a Manufacturing Order"
    )