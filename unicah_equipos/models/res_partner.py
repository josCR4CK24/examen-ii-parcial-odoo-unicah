from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    prestamo_equipo_ids = fields.One2many("unicah.prestamo", "partner_id", string="Préstamos de equipos")
