from odoo import fields, models


class ConvenioUnicah(models.Model):
    _name = "tienda.unicah.convenio"
    _description = "Convenio de descuento UNICAH"
    _order = "name"

    name = fields.Char(
        string="Nombre del convenio",
        required=True,
    )

    tipo_cliente = fields.Selection(
        [
            ("estudiante", "Estudiante"),
            ("docente", "Docente"),
            ("administrativo", "Administrativo"),
            ("externo", "Externo"),
        ],
        string="Tipo de cliente",
        required=True,
    )

    porcentaje_descuento = fields.Float(
        string="Descuento (%)",
        required=True,
        digits=(5, 2),
    )

    fecha_inicio = fields.Date(
        string="Fecha de inicio",
        required=True,
    )

    fecha_fin = fields.Date(
        string="Fecha de finalización",
        required=True,
    )

    activo = fields.Boolean(
        string="Activo",
        default=True,
    )
