# Se ejecuta dentro de odoo shell; nunca toca las bases locales.
import json
assert env.cr.dbname == 'unicah_railway'
env.cr.execute('SELECT current_database(), current_user, rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname=current_user')
row=env.cr.fetchone()
print('UNIC AH_RUNTIME'.replace(' ', '') + ' ' + json.dumps({'database':row[0],'role':row[1],
    'superuser':row[2],'createdb':row[3],'createrole':row[4],
    'module':env['ir.module.module'].search([('name','=','ventas_unicah')]).state,
    'fields':all(f in env['sale.order']._fields for f in ['canal_venta','total_unidades','requiere_aprobacion','aprobado_por'])}))
env.cr.rollback()
