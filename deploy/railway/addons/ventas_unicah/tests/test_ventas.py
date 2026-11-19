from odoo import Command
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestVentasUnicah(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Cliente de prueba Railway', 'canal_preferido': 'web'})
        cls.product = cls.env['product.product'].create({'name': 'Equipo académico prueba', 'type': 'consu'})
        cls.seller = cls.env['res.users'].create({'name': 'Vendedor prueba', 'login': 'railway_test_seller',
            'group_ids': [Command.set([cls.env.ref('sales_team.group_sale_salesman_all_leads').id])]})
        cls.manager = cls.env['res.users'].create({'name': 'Gerente prueba', 'login': 'railway_test_manager',
            'group_ids': [Command.set([cls.env.ref('sales_team.group_sale_manager').id])]})

    def order(self, amount=60000):
        return self.env['sale.order'].create({'partner_id': self.partner.id,
            'order_line': [Command.create({'product_id': self.product.id, 'product_uom_qty': 2,
                'price_unit': amount / 2, 'tax_ids': [Command.clear()]})]})

    def test_campos_y_canales(self):
        for canal in ['tienda', 'telefono', 'web', 'distribuidor']:
            self.partner.canal_preferido = canal
            order = self.order()
            self.assertEqual(order.canal_venta, canal)
            self.assertEqual(order.total_unidades, 2)
            order.canal_venta = 'telefono'
            self.assertEqual(order.canal_venta, 'telefono')
            order.order_line.product_uom_qty = 3
            self.assertEqual(order.total_unidades, 3)

    def test_umbral(self):
        self.assertFalse(self.order(50000).requiere_aprobacion)
        self.assertTrue(self.order(50000.01).requiere_aprobacion)
        small = self.order(49999)
        small.with_user(self.seller).action_confirm()
        self.assertEqual(small.state, 'sale')

    def test_bloqueo_y_aprobacion(self):
        order = self.order()
        self.assertTrue(order.pendiente_aprobacion)
        with self.assertRaises(UserError), self.cr.savepoint():
            order.with_user(self.seller).action_confirm()
        with self.assertRaises(AccessError), self.cr.savepoint():
            order.with_user(self.seller).action_aprobar()
        order.with_user(self.manager).action_aprobar()
        self.assertEqual(order.aprobado_por, self.manager)
        self.assertFalse(order.pendiente_aprobacion)
        order.with_user(self.seller).action_confirm()
        self.assertEqual(order.state, 'sale')

    def test_no_eludir_aprobacion_por_orm(self):
        order = self.order()
        with self.assertRaises(AccessError), self.cr.savepoint():
            order.with_user(self.seller).write({'aprobado_por': self.manager.id})

    def test_no_reutilizar_aprobacion_si_cambia_total(self):
        order = self.order()
        order.with_user(self.manager).action_aprobar()
        order.order_line.price_unit = 40000
        self.assertTrue(order.pendiente_aprobacion)
        with self.assertRaises(UserError), self.cr.savepoint():
            order.with_user(self.seller).action_confirm()

    def test_filtros_y_agrupacion(self):
        order = self.order()
        self.assertIn(order, self.env['sale.order'].search([('requiere_aprobacion', '=', True)]))
        groups = self.env['sale.order']._read_group([('id', '=', order.id)], ['canal_venta'], ['total_unidades:sum'])
        self.assertEqual(groups, [('web', 2.0)])
