"""Arranque Railway: configuración privada, inicialización única y ejecución sin root."""
import configparser
import os
from pathlib import Path
import pwd
import re
import subprocess
import sys
import time
import psycopg2


def require(name):
    value = os.environ.get(name)
    if not value or '\n' in value or '\r' in value:
        raise SystemExit(f'Variable obligatoria ausente o inválida: {name}')
    return value


def main():
    host = require('PGHOST')
    database = require('PGDATABASE')
    user = require('PGUSER')
    if not host.endswith('.railway.internal') or database != 'unicah_railway' or user != 'odoo_app':
        raise SystemExit('Destino rechazado: solo se admite la base exclusiva de Railway y odoo_app.')
    password = require('PGPASSWORD')
    master = require('ODOO_MASTER_PASSWORD')
    port = int(os.environ.get('PORT', '8069'))
    if not 1 <= port <= 65535:
        raise SystemExit('PORT fuera de rango')
    data = Path('/var/lib/odoo')
    config_dir = Path('/run/odoo')
    account = pwd.getpwnam('odoo')
    data.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.geteuid() == 0:
        # Solo los puntos de montaje: no se recorren ni reemplazan archivos existentes.
        for directory in [data, config_dir]:
            os.chown(directory, account.pw_uid, account.pw_gid)
        os.setgroups([])
        os.setgid(account.pw_gid)
        os.setuid(account.pw_uid)
    os.umask(0o077)
    config = configparser.ConfigParser(interpolation=None)
    config['options'] = {
        'addons_path': '/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons',
        'data_dir': str(data), 'admin_passwd': master,
        'db_host': host, 'db_port': os.environ.get('PGPORT', '5432'),
        'db_user': user, 'db_password': password, 'db_name': database,
        'dbfilter': '^' + re.escape(database) + '$', 'db_sslmode': 'require',
        'list_db': 'False', 'proxy_mode': 'True',
        'http_interface': '0.0.0.0', 'http_port': str(port),
        'workers': '0', 'max_cron_threads': '1', 'db_maxconn': '16',
        'limit_time_real': '180', 'without_demo': 'True', 'log_level': 'info',
    }
    config_path = config_dir / 'odoo.conf'
    with config_path.open('w') as stream:
        config.write(stream)
    conn = None
    for attempt in range(30):
        try:
            conn = psycopg2.connect(host=host, port=config['options']['db_port'], user=user,
                password=password, dbname=database, sslmode='require', connect_timeout=5)
            break
        except psycopg2.OperationalError as error:
            if attempt == 0:
                print('Diagnóstico PostgreSQL: ' + str(error).replace(password, '[REDACTED]'), flush=True)
            print(f'Esperando PostgreSQL: intento {attempt + 1}/30', flush=True)
            time.sleep(2)
    if conn is None:
        raise SystemExit('PostgreSQL no disponible; no se inició Odoo.')
    with conn, conn.cursor() as cursor:
        cursor.execute('SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname=current_user')
        if any(cursor.fetchone()):
            raise SystemExit('La cuenta de aplicación tiene privilegios administrativos: arranque rechazado.')
        cursor.execute("SELECT to_regclass('public.ir_module_module')")
        fresh = cursor.fetchone()[0] is None
        installed = False
        if not fresh:
            cursor.execute("SELECT state FROM ir_module_module WHERE name='ventas_unicah'")
            installed = cursor.fetchone() == ('installed',)
    conn.close()
    common = ['odoo', '-c', str(config_path), '-d', database]
    subprocess.run(['odoo', '--version'], check=True)
    if fresh or not installed:
        print('Inicializando base exclusiva de Railway e instalando ventas_unicah.', flush=True)
        install = common + ['-i', 'ventas_unicah', '--stop-after-init', '--no-http', '--max-cron-threads=0']
        subprocess.run(install, check=True)
    # La revisión explícita permite recuperar bases existentes y evita rotaciones en cada reinicio.
    if fresh and not os.environ.get('ODOO_ADMIN_CREDENTIAL_REVISION'):
        raise SystemExit('La inicialización nueva requiere una revisión explícita de credenciales.')
    subprocess.run(['odoo', 'shell', '-c', str(config_path), '-d', database,
        '--no-http', '--max-cron-threads=0'], input=Path('/opt/unicah/sync_admin.py').read_text(),
        text=True, check=True)
    if os.environ.get('ODOO_RUN_TESTS') == '1':
        subprocess.run(common + ['-u', 'ventas_unicah', '--stop-after-init', '--no-http',
            '--max-cron-threads=0', '--test-enable', '--test-tags', '/ventas_unicah'], check=True)
    if os.environ.get('ODOO_VERIFY_RUNTIME') == '1':
        subprocess.run(['odoo', 'shell', '-c', str(config_path), '-d', database,
            '--no-http', '--max-cron-threads=0'], input=Path('/opt/unicah/verify_runtime.py').read_text(),
            text=True, check=True)
    print('Odoo listo: rol sin privilegios administrativos, filestore persistente y puerto Railway.', flush=True)
    os.execvp('odoo', common)


if __name__ == '__main__':
    main()
