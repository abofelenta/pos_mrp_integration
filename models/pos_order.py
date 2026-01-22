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
    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()
        self._generate_mrp_orders()
        return res

    # generating Manufacturing Orders
    def _generate_mrp_orders(self):
        for order in self.filtered(lambda o: not o.is_refund):
            company = order.company_id
            picking_type_id = order.picking_type_id.warehouse_id.manu_type_id.id
            mrp_orders_to_create = [
                {
                    "product_id": line.product_id.id,
                    "product_qty": line.qty,
                    "product_uom_id": line.product_uom_id.id,
                    "pos_order_id": order.id,
                    "pos_order_line_id": line.id,
                    "origin": order.name,
                    "company_id": company.id,
                    "picking_type_id": picking_type_id,
                }
                for line in order.lines.filtered(
                    lambda i: i.product_id.manufacture_from_pos
                )
            ]
            production_orders = (
                self.env["mrp.production"]
                .with_company(company)
                .sudo()
                .create(mrp_orders_to_create)
            )

            # confirm production orders 
            production_orders.action_confirm()
            production_orders.action_assign()


