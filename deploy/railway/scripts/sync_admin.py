"""Ejecutar con odoo shell. Sincronización explícita y atómica del administrador existente."""
import os
import re
from odoo.exceptions import AccessDenied

assert env.cr.dbname == 'unicah_railway', 'Base no autorizada para sincronización'
revision = os.environ.get('ODOO_ADMIN_CREDENTIAL_REVISION', '')
parameters = env['ir.config_parameter'].sudo()
marker = 'ventas_unicah.admin_credential_revision'
if revision:
    if not re.fullmatch(r'[a-f0-9]{32}', revision):
        raise RuntimeError('Revisión de credenciales inválida')
    # Un bloqueo transaccional evita dos aplicaciones simultáneas de la misma revisión.
    env.cr.execute("SELECT pg_advisory_xact_lock(hashtext('unicah_admin_credential_sync'))")
    admin = env.ref('base.user_admin').sudo()
    login = os.environ.get('ODOO_ADMIN_LOGIN', '')
    password = os.environ.get('ODOO_ADMIN_PASSWORD', '')
    if not admin.exists() or not admin.active:
        raise RuntimeError('El administrador existente está ausente o inactivo; no se creará ni reactivará automáticamente')
    print(f'ADMIN_CREDENTIAL_SYNC target: database={env.cr.dbname} uid={admin.id} '
          f'active={admin.active} login_matches_environment={admin.login == login}', flush=True)
    if parameters.get_str(marker) != revision:
        if not login or login.strip() != login or any(c in login for c in '\r\n'):
            raise RuntimeError('Nombre de acceso administrativo inválido')
        if len(password) < 32 or password.strip() != password or password.lower() in ('admin', 'password'):
            raise RuntimeError('Se requiere una contraseña administrativa aleatoria de al menos 32 caracteres')
        if env['res.users'].sudo().with_context(active_test=False).search_count([('login', '=', login), ('id', '!=', admin.id)]):
            raise RuntimeError('El nombre de acceso ya pertenece a otro usuario; no se modificó')
        admin.write({'login': login, 'password': password})
        credential = {'type': 'password', 'login': login, 'password': password}
        try:
            auth = env['res.users'].authenticate(credential, {'interactive': True})
        except AccessDenied:
            raise RuntimeError('Odoo rechazó las nuevas credenciales administrativas') from None
        if auth['uid'] != admin.id:
            raise RuntimeError('Odoo autenticó un usuario distinto del administrador esperado')
        parameters.set_str(marker, revision)
        env.cr.commit()
        print('ADMIN_CREDENTIAL_SYNC applied: administrador existente actualizado y verificado; secretos omitidos.')
    else:
        env.cr.rollback()
        print('ADMIN_CREDENTIAL_SYNC unchanged: revisión ya aplicada; contraseña conservada.')
else:
    env.cr.rollback()
    print('ADMIN_CREDENTIAL_SYNC skipped: no se solicitó una revisión explícita.')
