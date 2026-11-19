
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .res_partner import CANALES_VENTA


MONTO_APROBACION = 50000


class SaleOrder(models.Model):
    _inherit = "sale.order"

    canal_venta = fields.Selection(
        CANALES_VENTA,
        string="Canal de venta",
        compute="_compute_canal_venta",
        store=True,
        readonly=False,
    )

    total_unidades = fields.Float(
        string="Total de unidades",
        compute="_compute_total_unidades",
        store=True,
    )

    requiere_aprobacion = fields.Boolean(
        string="Requiere aprobación",
        compute="_compute_requiere_aprobacion",
        store=True,
    )

    aprobado_por = fields.Many2one(
        "res.users",
        string="Aprobado por",
        readonly=True,
        copy=False,
    )

    aprobado_total = fields.Monetary(
        string="Total aprobado", readonly=True, copy=False, currency_field="currency_id",
    )

    pendiente_aprobacion = fields.Boolean(
        compute="_compute_pendiente_aprobacion",
    )

    @api.depends("partner_id")
    def _compute_canal_venta(self):
        for order in self:
            order.canal_venta = order.partner_id.canal_preferido

    @api.depends("order_line.product_uom_qty")
    def _compute_total_unidades(self):
        for order in self:
            order.total_unidades = sum(
                order.order_line.mapped("product_uom_qty")
            )

    @api.depends("amount_total")
    def _compute_requiere_aprobacion(self):
        for order in self:
            order.requiere_aprobacion = (
                order.amount_total > MONTO_APROBACION
            )

    @api.depends("requiere_aprobacion", "aprobado_por", "aprobado_total", "amount_total", "state")
    def _compute_pendiente_aprobacion(self):
        for order in self:
            order.pendiente_aprobacion = (
                order.requiere_aprobacion
                and not order._aprobacion_vigente()
                and order.state in ("draft", "sent")
            )

    def _aprobacion_vigente(self):
        self.ensure_one()
        return bool(self.aprobado_por and self.currency_id.compare_amounts(
            self.aprobado_total, self.amount_total) == 0)

    def _check_campos_aprobacion(self, values):
        if {"aprobado_por", "aprobado_total"}.intersection(values):
            if not self.env.user.has_group("sales_team.group_sale_manager"):
                raise AccessError("Solo un administrador de ventas puede registrar aprobaciones.")
            if values.get("aprobado_por") and values["aprobado_por"] != self.env.uid:
                raise AccessError("La aprobación debe registrar al usuario que la realiza.")

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            self._check_campos_aprobacion(values)
        return super().create(vals_list)

    def write(self, values):
        self._check_campos_aprobacion(values)
        return super().write(values)

    def action_aprobar(self):
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            raise AccessError(
                "Solo un administrador de ventas puede aprobar pedidos."
            )
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError("Solo se pueden aprobar cotizaciones en borrador o enviadas.")
            order.write({"aprobado_por": self.env.user.id, "aprobado_total": order.amount_total})
            order.message_post(body="Pedido aprobado por un administrador de ventas.")

    def action_confirm(self):
        for order in self:
            if order.requiere_aprobacion and not order._aprobacion_vigente():
                raise UserError(
                    f"El pedido {order.name} supera {MONTO_APROBACION:,} y debe ser "
                    "aprobado por un administrador de ventas antes de confirmarse."
                )
        return super().action_confirm()
