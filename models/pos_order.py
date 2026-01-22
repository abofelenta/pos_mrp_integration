from odoo import models, api,_,fields
from odoo.exceptions import UserError,ValidationError
from collections import defaultdict

class PosOrder(models.Model):
    _inherit = "pos.order"

   