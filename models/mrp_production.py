from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    pos_order_id = fields.Many2one(
        "pos.order",
        string="POS Order Reference",
        related="pos_order_line_id.order_id",
        readonly=True,
        store=True,
        copy=False,
    )
    
    pos_order_line_id = fields.Many2one(
        "pos.order.line",
        "POS Order Line",
        readonly=True,
        copy=False,
        help="The POS Order Line that generated this Manufacturing Order",
    )
    def action_open_pos_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "pos.order",
            "res_id": self.pos_order_id.id,
            "view_mode": "form",
            "target": "current",
        }
