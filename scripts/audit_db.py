import psycopg2, json, configparser
config = configparser.ConfigParser()
config.read("C:/OdooFuente/odoo/odoo_pg18.conf")
options = config["options"]
c=psycopg2.connect(host=options['db_host'],user=options['db_user'],password=options['db_password'],dbname='examen_unicah')
r=c.cursor()
for sql in ["select id,name,tipo_cliente,porcentaje,fecha_inicio,fecha_fin,active from tienda_convenio order by id", "select module,name,res_id from ir_model_data where model='tienda.convenio'", "select id,name,numero_cuenta from res_partner where numero_cuenta is not null", "select login from res_users where active=true"]:
 r.execute(sql); print(json.dumps(r.fetchall(),default=str,ensure_ascii=False))
c.close()
