import json
from pathlib import Path
from odoo import Command
assert env.cr.dbname == 'examen_unicah'
def get_or_create(model, xmlid, vals):
    rec = env.ref('unicah_evidencia.' + xmlid, raise_if_not_found=False)
    if not rec:
        rec = env[model].create(vals)
        env['ir.model.data'].create({'module':'unicah_evidencia','name':xmlid,'model':model,'res_id':rec.id,'noupdate':True})
    return rec
student = get_or_create('res.partner','estudiante',{'name':'Estudiante Evidencia UNICAH','tipo_cliente':'estudiante','numero_cuenta':'0801200012','carrera':'Ingeniería en Sistemas'})
teacher = get_or_create('res.partner','docente',{'name':'Docente Evidencia UNICAH','tipo_cliente':'docente'})
book = get_or_create('product.product','libro',{'name':'Libro universitario - Evidencia','type':'consu','list_price':100})
uniform = get_or_create('product.product','uniforme',{'name':'Uniforme UNICAH - Evidencia','type':'consu','list_price':200})
order = get_or_create('sale.order','cotizacion',{'partner_id':student.id,'date_order':'2026-11-13 18:00:00','order_line':[
    Command.create({'display_type':'line_section','name':'Material universitario'}),
    Command.create({'product_id':book.id,'product_uom_qty':2,'price_unit':100,'tax_ids':[Command.clear()]}),
    Command.create({'product_id':uniform.id,'product_uom_qty':1,'price_unit':200,'tax_ids':[Command.clear()]})]})
if not order.convenio_aplicado: order.action_aplicar_convenio()
equipo = get_or_create('unicah.equipo','equipo',{'name':'Portátil Lenovo - Laboratorio UNICAH','codigo':'UNICAH-TIC-001'})
prestamo = get_or_create('unicah.prestamo','prestamo',{'name':'Préstamo demostrativo UNICAH','equipo_id':equipo.id,'partner_id':student.id,'fecha_inicio':'2026-11-13','fecha_fin':'2026-11-15','observaciones':'Evidencia académica: equipo entregado en buen estado.'})
if prestamo.state == 'borrador': prestamo.action_prestar()
# Autorización expresa del usuario para ambos usuarios en esta conversación.
group=env.ref('sale.group_discount_per_so_line')
for user in env['res.users'].search([('login','in',['admin','prueba.convenios'])]):
    user.write({'group_ids':[Command.link(group.id)]})
result={'student':student.id,'teacher':teacher.id,'order':order.id,'equipo':equipo.id,'prestamo':prestamo.id,'ahorro':order.monto_ahorro,'convenios':env['tienda.convenio'].search([]).read(['name','porcentaje'])}
Path('C:/OdooFuente/examen_final/evidence/demo_records.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
env.cr.commit()
print(json.dumps(result,ensure_ascii=False))
