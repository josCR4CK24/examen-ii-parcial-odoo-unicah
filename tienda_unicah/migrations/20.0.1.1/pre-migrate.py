from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(
        cr,
        "tienda.unicah.convenio",
        "tienda.convenio",
    )

    util.rename_field(
        cr,
        "tienda.convenio",
        "porcentaje_descuento",
        "porcentaje",
    )

    util.rename_field(
        cr,
        "tienda.convenio",
        "activo",
        "active",
    )
