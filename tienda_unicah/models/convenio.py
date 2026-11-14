from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ConvenioUnicah(models.Model):
    _name = "tienda.convenio"
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

    porcentaje = fields.Float(
        string="Descuento (%)",
        required=True,
        digits=(5, 2),
    )

    fecha_inicio = fields.Date(
        string="Fecha de inicio",
        default=fields.Date.context_today,
        required=True,
    )

    fecha_fin = fields.Date(
        string="Fecha de finalización",
    )

    active = fields.Boolean(
        string="Activo",
        default=True,
    )

    @api.constrains("porcentaje", "fecha_inicio", "fecha_fin")
    def _check_convenio(self):
        for convenio in self:
            if not 0 < convenio.porcentaje <= 40:
                raise ValidationError("El descuento debe ser mayor que 0 y no superar 40 %.")
            if convenio.fecha_fin and convenio.fecha_fin < convenio.fecha_inicio:
                raise ValidationError("La fecha final no puede ser anterior a la inicial.")

    @api.model
    def _cargar_convenio_inicial(self, xmlid, valores):
        """Carga idempotente: conserva los valores de cualquier convenio existente."""
        if self.env.ref("tienda_unicah." + xmlid, raise_if_not_found=False):
            return
        convenio = self.with_context(active_test=False).search([
            ("tipo_cliente", "=", valores["tipo_cliente"])], order="id", limit=1)
        if not convenio:
            convenio = self.create(valores)
        self.env["ir.model.data"].create({"module": "tienda_unicah", "name": xmlid,
            "model": self._name, "res_id": convenio.id, "noupdate": True})
