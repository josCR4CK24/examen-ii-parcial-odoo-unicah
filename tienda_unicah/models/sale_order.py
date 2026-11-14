from markupsafe import Markup
from odoo import api, fields, models
from odoo.exceptions import UserError

LIMITE_UNIDADES_ESTUDIANTE = 10


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tipo_cliente = fields.Selection(related="partner_id.tipo_cliente", string="Tipo de cliente")
    convenio_id = fields.Many2one("tienda.convenio", string="Convenio", compute="_compute_convenio_id",
        store=True, readonly=False, domain="[('tipo_cliente', '=', tipo_cliente)]")
    convenio_aplicado = fields.Boolean(string="Convenio aplicado", readonly=True, copy=False)
    monto_ahorro = fields.Monetary(string="Ahorro por convenio", compute="_compute_monto_ahorro",
        store=True, currency_field="currency_id")

    @api.depends("partner_id", "partner_id.tipo_cliente", "date_order")
    def _compute_convenio_id(self):
        for order in self:
            fecha = (order.date_order or fields.Datetime.now()).date()
            order.convenio_id = self.env["tienda.convenio"].search([
                ("tipo_cliente", "=", order.partner_id.tipo_cliente), ("fecha_inicio", "<=", fecha),
                "|", ("fecha_fin", "=", False), ("fecha_fin", ">=", fecha)],
                order="fecha_inicio desc, id", limit=1) if order.partner_id else False
            order.convenio_aplicado = False

    def action_aplicar_convenio(self):
        for order in self:
            if order.state not in ("draft", "sent"):
                raise UserError("Solo se puede aplicar un convenio a una cotización.")
            convenio = order.convenio_id
            if not convenio:
                raise UserError("El pedido no tiene un convenio asignado.")
            fecha = (order.date_order or fields.Datetime.now()).date()
            if (not convenio.active or convenio.tipo_cliente != order.tipo_cliente
                or convenio.fecha_inicio > fecha or (convenio.fecha_fin and convenio.fecha_fin < fecha)):
                raise UserError("El convenio debe estar activo, vigente y corresponder al tipo de cliente.")
            lineas = order.order_line.filtered(lambda line: not line.display_type and line.product_id)
            if not lineas:
                raise UserError("Agregue al menos un producto antes de aplicar el convenio.")
            lineas.write({"discount": convenio.porcentaje})
            order.convenio_aplicado = True
            order.message_post(body=Markup("Se aplicó el %s con %s %% de descuento.") %
                (convenio.name, f"{convenio.porcentaje:g}"))
        return True

    def action_confirm(self):
        for order in self:
            if order.tipo_cliente == "estudiante":
                total = sum(order.order_line.filtered(lambda line: not line.display_type).mapped("product_uom_qty"))
                if total > LIMITE_UNIDADES_ESTUDIANTE:
                    raise UserError(f"El límite para estudiantes es {LIMITE_UNIDADES_ESTUDIANTE} unidades; el pedido tiene {total:g}.")
        return super().action_confirm()

    @api.depends("order_line.price_unit", "order_line.product_uom_qty", "order_line.discount", "order_line.display_type")
    def _compute_monto_ahorro(self):
        for order in self:
            order.monto_ahorro = sum(line.price_unit * line.product_uom_qty * line.discount / 100
                for line in order.order_line if not line.display_type)
