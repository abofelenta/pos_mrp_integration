# pos_mrp_integration

Integrates Point of Sale (POS) with Manufacturing (MRP) to automatically create, link and manage Manufacturing Orders (MO / `mrp.production`) from POS sales.

This addon implements model extensions, validations and view improvements so that products sold via POS can trigger Manufacturing Orders when configured to do so.

## Quick summary

- Auto-create `mrp.production` orders from POS sales for products flagged as "Manufacture from POS".
- Link MOs back to the originating `pos.order` and `pos.order.line`.
- Add UI hints (buttons and stats) in POS and MRP views to open related records and see counts.
- Add product flags and validations to ensure BOMs and product types are correct for manufacturing from POS.

## Files in this module

- `__manifest__.py` — module metadata and dependencies (`point_of_sale`, `mrp`).
- `models/pos_order.py` — extends `pos.order` to generate MOs and expose MRP relations.
- `models/mrp_production.py` — extends `mrp.production` with `pos_order_line_id`, `pos_order_id`, and an action to open the POS order.
- `models/product_template.py` — adds `manufacture_from_pos` flag and validation constraints on product templates.
- `models/product.py` — loads additional POS fields for the POS front-end (`manufacture_from_pos`, `bom_count`).
- `views/product_views.xml` — adds the `manufacture_from_pos` checkbox to product template form and tree views.
- `views/pos_order_views.xml` — adds a stat button in the POS order form showing the number of linked MOs and allowing opening them.
- `views/mrp_productions_views.xml` — adds the `pos_order_id` field in the MOs tree view and a button in the MO form to open the linked POS order.

## Models & behavior (details)

1) `pos.order` (models/pos_order.py)

- New fields:
	- `mrp_production_ids` (One2many to `mrp.production`): listing related manufacturing orders for the POS order.
	- `mrp_production_count` (Integer): computed count of related MOs.

- Key behavior:
	- On order payment (`action_pos_order_paid`) the module runs `_generate_mrp_orders` which:
		- Filters order lines where the product has `manufacture_from_pos` enabled.
		- Creates `mrp.production` records (with `pos_order_id`, `pos_order_line_id`, product, qty, origin, etc.).
		- Confirms and assigns the created production orders and attempts to mark them done when components are available.
		- Calls `action_bom_cost` on related products to reflect manufacturing cost in product cost.

	- Constraint `_check_manufacture_products_have_bom` prevents sale of products marked `manufacture_from_pos` if a normal BoM cannot be found for the company/picking type.

2) `product.template` (models/product_template.py)

- New field:
	- `manufacture_from_pos` (Boolean): if checked, selling this product in POS will trigger MO creation.

- Validations (constraints):
	- Ensure at least one valid normal BoM exists for the product when `manufacture_from_pos` is enabled.
	- Restrict `manufacture_from_pos` to consumable products only (product.type == 'consu').
	- Ensure the product is storable when manufacturing from POS is enabled.

3) `product.product` (models/product.py)

- Publishes `manufacture_from_pos` and `bom_count` to the POS front-end via `_load_pos_data_fields`, so the POS UI or config that consumes these fields can behave accordingly.

4) `mrp.production` (models/mrp_production.py)

- New fields:
	- `pos_order_line_id` (Many2one to `pos.order.line`): the originating POS order line (readonly).
	- `pos_order_id` (Many2one related to `pos_order_line_id.order_id`, stored): the parent POS order.

- New method `action_open_pos_order`: returns an action to open the linked `pos.order` form view.

## Views / UI

- `product_views.xml` — Adds `manufacture_from_pos` checkbox to product template form and tree views so administrators can mark products to manufacture from POS.

- `pos_order_views.xml` — Adds a stat button in the POS order form header that shows `mrp_production_count` and opens a window with the related `mrp.production` records (list/form/kanban, read-only create disabled).

- `mrp_productions_views.xml` —
	- Shows `pos_order_id` in the production orders tree to help identify MOs created from POS.
	- Adds an action button in the MO form's button box that displays the linked `pos.order` and opens it when clicked.

## Typical workflow

1. Mark a product as "Manufacture from POS" on its product template.
2. Sell the product in the POS session.
3. When the POS order is validated/paid, `_generate_mrp_orders` will create the corresponding `mrp.production` orders (if not a refund), confirm and attempt to assign/finish them based on component availability.
4. From the POS order you can open related MOs; from an MO you can open the originating POS order using the provided buttons.

## Installation

1. Place the `pos_mrp_integration` folder under your Odoo addons path (it's already in `custom_addons` in this repo).
2. Restart Odoo and update the Apps list.
3. Install the module from Apps.

Requirements: The module depends on `point_of_sale` and `mrp` (declared in `__manifest__.py`).

## Notes for customization and development

- If you want to show different views or add permissions, update or extend the XML view files.
- The module uses `sudo()` when creating MOs for the order's company to avoid access issues during automated creation — consider review if you need stricter access control.
- The product validations will raise `UserError` if product data is invalid; handle these in custom POS flows if needed.

## Testing and verification

- Manual tests to verify the integration:
	- Create a consumable product with a valid BoM and enable "Manufacture from POS".
	- Sell it in POS and pay the order.
	- Confirm that a `mrp.production` record is created and linked to the POS order/line.
	- Use the stat buttons on POS and the button on the MO form to navigate between records.

## Compatibility

- Designed to work with Odoo installations that provide `point_of_sale` and `mrp` apps. Verify compatibility with your exact Odoo minor version; tests were developed for Odoo 14/15/16-style models (adjust as needed).

## License

This module uses the repository's top-level license. See `LICENSE` in the repository root for details.

## Changelog

- 1.0.0 - Added module integration between POS and MRP with product flags, validations, MRP creation flow and UI improvements.
