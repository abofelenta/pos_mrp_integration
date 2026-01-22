{
    "name": "POS MRP Integration",
    "version": "1.0",
    "category": "Manufacturing",
    "summary": "Automatically create Manufacturing Orders from POS sales",
    "depends": ["point_of_sale", "mrp"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
    ],
    "installable": True,
    "application": False,
}
