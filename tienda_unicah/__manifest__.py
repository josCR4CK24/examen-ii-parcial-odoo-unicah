{
    "name": "Tienda UNICAH",
    "version": "20.0.1.2",
    "summary": "Convenios de descuento para la tienda universitaria",
    "category": "Sales/Sales",
    "author": "José Carlos Cáceres Girón",
    "depends": ["sale_management"],
    "data": [
        "security/ir.access.csv",
        "data/convenio_data.xml",
        "views/res_partner_views.xml",
        "views/convenio_views.xml",
        "views/sale_order_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
