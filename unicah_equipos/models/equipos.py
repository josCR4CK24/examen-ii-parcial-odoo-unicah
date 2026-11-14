from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class Equipo(models.Model):
    _name = "unicah.equipo"
    _description = "Equipo tecnológico universitario"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Equipo", required=True, tracking=True)
    codigo = fields.Char(string="Código de inventario", required=True, copy=False)
    categoria = fields.Selection([("portatil", "Portátil"), ("proyector", "Proyector"),
        ("tableta", "Tableta")], required=True, default="portatil")
    active = fields.Boolean(default=True)
    prestamo_ids = fields.One2many("unicah.prestamo", "equipo_id", string="Préstamos")
    disponible = fields.Boolean(string="Disponible", compute="_compute_disponible", store=True)

    @api.depends("prestamo_ids.state")
    def _compute_disponible(self):
        for equipo in self:
            equipo.disponible = not any(p.state == "prestado" for p in equipo.prestamo_ids)

    @api.constrains("codigo")
    def _check_codigo(self):
        for equipo in self:
            if self.with_context(active_test=False).search_count([("codigo", "=", equipo.codigo), ("id", "!=", equipo.id)]):
                raise ValidationError("El código de inventario ya existe.")


class Prestamo(models.Model):
    _name = "unicah.prestamo"
    _description = "Préstamo de equipo tecnológico"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "fecha_inicio desc, id desc"

    name = fields.Char(string="Referencia", required=True, default="Préstamo de equipo")
    equipo_id = fields.Many2one("unicah.equipo", string="Equipo", required=True, ondelete="restrict", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Solicitante", required=True, ondelete="restrict", tracking=True)
    responsable_id = fields.Many2one("res.users", string="Responsable", required=True, default=lambda self: self.env.user)
    fecha_inicio = fields.Date(string="Fecha de entrega", required=True, default=fields.Date.context_today)
    fecha_fin = fields.Date(string="Devolución prevista", required=True)
    fecha_devolucion = fields.Date(string="Devolución real", readonly=True)
    duracion_dias = fields.Integer(string="Duración (días)", compute="_compute_duracion", store=True)
    state = fields.Selection([("borrador", "Borrador"), ("prestado", "Prestado"),
        ("devuelto", "Devuelto")], string="Estado", default="borrador", required=True, tracking=True, copy=False)
    observaciones = fields.Text()

    @api.depends("fecha_inicio", "fecha_fin")
    def _compute_duracion(self):
        for p in self:
            p.duracion_dias = (p.fecha_fin - p.fecha_inicio).days + 1 if p.fecha_fin and p.fecha_inicio else 0

    @api.constrains("fecha_inicio", "fecha_fin", "equipo_id", "state")
    def _check_prestamo(self):
        for p in self:
            if p.fecha_fin < p.fecha_inicio:
                raise ValidationError("La devolución prevista no puede ser anterior a la entrega.")
            if p.state == "prestado":
                # Serializa la entrega del mismo equipo frente a solicitudes simultáneas.
                self.env.cr.execute("SELECT id FROM unicah_equipo WHERE id = %s FOR UPDATE", [p.equipo_id.id])
                if not p.equipo_id.active:
                    raise ValidationError("No se puede prestar un equipo archivado.")
                if self.search_count([("equipo_id", "=", p.equipo_id.id), ("state", "=", "prestado"), ("id", "!=", p.id)]):
                    raise ValidationError("El equipo ya tiene un préstamo activo.")

    def action_prestar(self):
        if any(p.state != "borrador" for p in self):
            raise UserError("Solo se pueden entregar préstamos en borrador.")
        self.write({"state": "prestado"})
        for p in self:
            p.message_post(body="Equipo entregado al solicitante.")
        return True

    def action_devolver(self):
        if any(p.state != "prestado" for p in self):
            raise UserError("Solo se pueden devolver equipos prestados.")
        self.write({"state": "devuelto", "fecha_devolucion": fields.Date.context_today(self)})
        for p in self:
            p.message_post(body="Equipo devuelto y disponible para otro préstamo.")
        return True
