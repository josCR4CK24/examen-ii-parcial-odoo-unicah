from datetime import date
from odoo import Command
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError, AccessError


@tagged("post_install", "-at_install")
class TestTienda(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["tienda.convenio"].search([]).write({"active": False})
        cls.estudiante = cls.env["res.partner"].create({"name": "Estudiante test", "tipo_cliente": "estudiante", "numero_cuenta": "0801200012"})
        cls.docente = cls.env["res.partner"].create({"name": "Docente test", "tipo_cliente": "docente"})
        cls.producto = cls.env["product.product"].create({"name": "Libro test", "type": "consu", "list_price": 100})
        cls.convenio = cls.env["tienda.convenio"].create({"name": "Convenio test", "tipo_cliente": "estudiante", "porcentaje": 15, "fecha_inicio": "2026-01-01"})

    def pedido(self, partner=None, qty=2):
        return self.env["sale.order"].create({"partner_id": (partner or self.estudiante).id, "date_order": "2026-06-01 12:00:00",
            "order_line": [Command.create({"display_type": "line_section", "name": "Libros"}),
                Command.create({"product_id": self.producto.id, "product_uom_qty": qty, "price_unit": 100, "tax_ids": [Command.clear()]}),
                Command.create({"product_id": self.producto.id, "product_uom_qty": 1, "price_unit": 200, "tax_ids": [Command.clear()]})]})

    def test_cuenta(self):
        for cuenta in ["12345678", "", "abcdefghij", "１２３４５６７８９０", "12345678901"]:
            with self.assertRaises(ValidationError), self.cr.savepoint():
                self.env["res.partner"].create({"name": "Inválido", "tipo_cliente": "estudiante", "numero_cuenta": cuenta})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.estudiante.numero_cuenta = "123"
        self.docente.numero_cuenta = "libre"

    def test_porcentaje_y_fechas(self):
        for porcentaje in [0, -1, 40.01, 50]:
            with self.assertRaises(ValidationError), self.cr.savepoint():
                self.convenio.porcentaje = porcentaje
        self.convenio.porcentaje = 40
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.convenio.write({"fecha_inicio": "2026-12-01", "fecha_fin": "2026-01-01"})

    def test_aplicar_y_ahorro(self):
        order = self.pedido()
        self.assertEqual(order.convenio_id, self.convenio)
        order.action_aplicar_convenio()
        self.assertTrue(order.convenio_aplicado)
        self.assertEqual(order.order_line.filtered("display_type").discount, 0)
        self.assertEqual(order.order_line.filtered(lambda l: not l.display_type).mapped("discount"), [15, 15])
        self.assertAlmostEqual(order.monto_ahorro, 60)
        self.assertTrue(any("Convenio test" in str(m.body) for m in order.message_ids))
        line = order.order_line.filtered(lambda l: not l.display_type)[0]
        line.price_unit = 200
        self.assertAlmostEqual(order.monto_ahorro, 90)
        line.product_uom_qty = 3
        self.assertAlmostEqual(order.monto_ahorro, 120)
        line.discount = 10
        self.assertAlmostEqual(order.monto_ahorro, 90)
        line.unlink()
        self.assertAlmostEqual(order.monto_ahorro, 30)

    def test_vigencia_y_estado(self):
        order = self.pedido()
        self.convenio.active = False
        with self.assertRaises(UserError), self.cr.savepoint():
            order.action_aplicar_convenio()
        self.convenio.active = True
        self.convenio.fecha_fin = date(2026, 5, 1)
        with self.assertRaises(UserError), self.cr.savepoint():
            order.action_aplicar_convenio()
        order.date_order = "2026-07-01 12:00:00"
        self.assertFalse(order.convenio_id)
        with self.assertRaises(UserError), self.cr.savepoint():
            order.action_aplicar_convenio()
        order.action_confirm()
        with self.assertRaises(UserError), self.cr.savepoint():
            order.action_aplicar_convenio()

    def test_limite_y_super(self):
        order = self.pedido(qty=11)
        with self.assertRaisesRegex(UserError, "10.*12"), self.cr.savepoint():
            order.action_confirm()
        self.assertEqual(order.state, "draft")
        docente = self.pedido(self.docente, qty=11)
        docente.action_confirm()
        self.assertEqual(docente.state, "sale")
        valido = self.pedido(qty=9)
        valido.action_confirm()
        self.assertEqual(valido.state, "sale")

    def test_seleccion_y_filtros(self):
        order = self.pedido()
        order.partner_id = self.docente
        self.assertFalse(order.convenio_id)
        order.partner_id = self.estudiante
        self.assertEqual(order.convenio_id, self.convenio)
        order.action_aplicar_convenio()
        self.assertIn(order, self.env["sale.order"].search([("convenio_aplicado", "=", True)]))
        groups = self.env["sale.order"]._read_group([("id", "=", order.id)], ["convenio_id"], ["monto_ahorro:sum"])
        self.assertEqual(groups[0][0], self.convenio)
        self.assertAlmostEqual(groups[0][1], 60)

    def test_permisos(self):
        user = self.env["res.users"].create({"name": "Vendedor test", "login": "test_unicah_sales", "group_ids": [Command.set([self.env.ref("sales_team.group_sale_salesman").id])]})
        self.assertEqual(self.convenio.with_user(user).porcentaje, 15)
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.convenio.with_user(user).porcentaje = 20
        user.group_ids = [Command.set([self.env.ref("sales_team.group_sale_manager").id])]
        self.convenio.with_user(user).porcentaje = 20
        self.assertEqual(self.convenio.porcentaje, 20)

    def test_datos_iniciales_idempotentes(self):
        model = self.env["tienda.convenio"]
        original = self.env.ref("tienda_unicah.convenio_estudiantes")
        values = original.read(["name", "porcentaje", "fecha_inicio", "fecha_fin", "active"])
        count = model.with_context(active_test=False).search_count([])
        for _ in range(2):
            model._cargar_convenio_inicial("convenio_estudiantes", {"name": "No debe sobrescribir", "tipo_cliente": "estudiante", "porcentaje": 20, "fecha_inicio": "2026-01-01"})
        self.assertEqual(model.with_context(active_test=False).search_count([]), count)
        self.assertEqual(original.read(["name", "porcentaje", "fecha_inicio", "fecha_fin", "active"]), values)
