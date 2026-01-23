from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacture_from_pos = fields.Boolean(
        string="Manufacture from POS",
        help="If enabled, selling this product in POS will create a Manufacturing Order"
    )

    # 1. BoM Validation
    @api.constrains("manufacture_from_pos", "bom_ids", "is_kits")
    def _check_manufacture_from_pos_bom(self):
        """
        Ensure product has at least one valid Manufacturing BoM.
        """
        for tmpl in self.filtered("manufacture_from_pos"):
            boms = (
                self.env["mrp.bom"]
                ._bom_find(
                    tmpl.product_variant_ids,
                    company_id=tmpl.company_id.id,
                    bom_type="normal",
                ).values()
            )
            if not boms:
                raise UserError(
                    _(
                        "Product '%(name)s' must have a valid Manufacturing BoM.\n"
                        "Company: %(company)s",
                        name=tmpl.display_name,
                        company=tmpl.company_id.name or "All",
                    )
                )

    # 2. Product Type Validation

    @api.constrains("manufacture_from_pos", "type")
    def _check_manufacture_from_product_type(self):
        """
        Ensure only allowed product types can use Manufacture from POS.
        """
        invalid_products = self.filtered(
            lambda p: p.manufacture_from_pos and p.type != "consu"
        )
        if invalid_products:
            raise UserError(
                _(
                    "Manufacturing from POS is only supported for "
                    "Consumable products.\n"
                    "Invalid products: %(products)s",
                    products=", ".join(invalid_products.mapped("display_name")),
                )
            )

    # 3. Storable Validation
    @api.constrains("manufacture_from_pos", "is_storable")
    def _check_manufacture_from_pos_storable(self):
        """
        Ensure product is storable (required for stock & valuation).
        """
        invalid_products = self.filtered(
            lambda p: p.manufacture_from_pos and not p.is_storable
        )
        if invalid_products:
            raise UserError(
                _(
                    "Manufacturing from POS requires storable products.\n"
                    "Invalid products: %(products)s",
                    products=", ".join(invalid_products.mapped("display_name")),
                )
            )