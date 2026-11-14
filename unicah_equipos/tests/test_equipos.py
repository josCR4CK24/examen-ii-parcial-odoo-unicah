from odoo import Command
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError, AccessError


@tagged("post_install", "-at_install")
class TestEquipos(TransactionCase):
    def setUp(self):
        super().setUp()
        self.equipo = self.env["unicah.equipo"].create({"name": "Portátil test", "codigo": "TEST-001"})
        self.partner = self.env["res.partner"].create({"name": "Solicitante test"})

    def prestamo(self):
        return self.env["unicah.prestamo"].create({"equipo_id": self.equipo.id, "partner_id": self.partner.id,
            "fecha_inicio": "2026-11-13", "fecha_fin": "2026-11-15"})

    def test_ciclo_y_herencia(self):
        p = self.prestamo()
        self.assertEqual(p.duracion_dias, 3)
        self.assertIn(p, self.partner.prestamo_equipo_ids)
        self.assertTrue(self.equipo.disponible)
        p.action_prestar()
        self.assertFalse(self.equipo.disponible)
        otro = self.prestamo()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            otro.action_prestar()
        p.action_devolver()
        self.assertTrue(self.equipo.disponible)
        self.assertTrue(p.fecha_devolucion)
        otro.action_prestar()
        self.assertFalse(self.equipo.disponible)
        self.assertTrue(any("devuelto" in str(m.body) for m in p.message_ids))

    def test_validaciones(self):
        p = self.prestamo()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            p.fecha_fin = "2026-11-12"
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env["unicah.equipo"].create({"name": "Duplicado", "codigo": self.equipo.codigo})
        with self.assertRaises(UserError), self.cr.savepoint():
            p.action_devolver()
        self.equipo.active = False
        with self.assertRaises(ValidationError), self.cr.savepoint():
            p.action_prestar()

    def test_permisos(self):
        user = self.env["res.users"].create({"name": "Operador test", "login": "test_equipos_user", "group_ids": [Command.set([self.env.ref("base.group_user").id])]})
        equipo = self.env["unicah.equipo"].with_user(user).create({"name": "Equipo operador", "codigo": "TEST-002"})
        equipo.name = "Equipo actualizado"
        with self.assertRaises(AccessError), self.cr.savepoint():
            equipo.unlink()
