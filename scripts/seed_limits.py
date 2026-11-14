from odoo import Command
assert env.cr.dbname == 'examen_unicah'
for suffix, partner_ref in [('estudiante_12','estudiante'),('docente_12','docente')]:
    rec=env.ref('unicah_evidencia.'+suffix,raise_if_not_found=False)
    if not rec:
        rec=env['sale.order'].create({'partner_id':env.ref('unicah_evidencia.'+partner_ref).id,'date_order':'2026-11-13 18:00:00','order_line':[Command.create({'product_id':env.ref('unicah_evidencia.libro').id,'price_unit':100,'product_uom_qty':12,'tax_ids':[Command.clear()]})]})
        env['ir.model.data'].create({'module':'unicah_evidencia','name':suffix,'model':'sale.order','res_id':rec.id,'noupdate':True})
    print(suffix,rec.id)
env.cr.commit()
