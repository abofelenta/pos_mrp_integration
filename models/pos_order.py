from odoo import models, api,_,fields
from odoo.exceptions import UserError,ValidationError
from collections import defaultdict

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.constrains("lines")
    def _check_manufacture_products_have_bom(self):
        for order in self:
            products = order.lines.mapped("product_id").filtered("manufacture_from_pos")
            if not products:
                continue
            boms=self.env["mrp.bom"]._bom_find(
                products,
                picking_type=order.picking_type_id,
                company_id=order.company_id.id,
                bom_type="normal",
            )

            products_not_boms=products.filtered(
                lambda p: not boms.get(p)
            )
            if products_not_boms:
                raise ValidationError(
                       _("Product %(products)s has no Bill of Materials and cannot be sold. for company %(company)s:",
                         company=order.company_id.name,products=", ".join(products_not_boms.mapped("display_name")),
                ))
    