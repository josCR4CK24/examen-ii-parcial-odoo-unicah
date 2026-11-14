from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re

TIPOS_CLIENTE = [
    ("estudiante", "Estudiante"),
    ("docente", "Docente"),
    ("administrativo", "Administrativo"),
    ("externo", "Externo"),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    tipo_cliente = fields.Selection(
        TIPOS_CLIENTE,
        string="Tipo de cliente",
        default="externo",
    )

    numero_cuenta = fields.Char(
        string="Número de cuenta",
        copy=False,
    )

    carrera = fields.Char(
        string="Carrera",
    )

    @api.constrains("tipo_cliente", "numero_cuenta")
    def _check_numero_cuenta(self):
        for partner in self:
            if partner.tipo_cliente == "estudiante" and not re.fullmatch(r"[0-9]{10}", partner.numero_cuenta or ""):
                raise ValidationError("La cuenta estudiantil debe contener exactamente 10 dígitos numéricos.")
