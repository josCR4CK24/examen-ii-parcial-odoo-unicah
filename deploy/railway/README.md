# Despliegue de Ventas UNICAH en Railway

El contexto de compilación es este directorio, `deploy/railway/`. El Dockerfile fija la imagen oficial de Odoo 20 por digest e incluye el módulo `ventas_unicah`. El módulo depende de `sale_management` y registra quién aprobó cada cotización y por qué importe. Cuando cambia el importe, el pedido debe aprobarse de nuevo si sigue por encima del umbral de 50 000.

## Configuración del servicio

Usar un servicio Odoo y un servicio PostgreSQL en la misma red privada de Railway. Configurar los ajustes de `service-settings.json` en el servicio Odoo. El Dockerfile debe quedar en la raíz del contexto y el dominio público debe apuntar al puerto 8069. El healthcheck usa `/web/health`.

Montar el volumen Odoo en `/var/lib/odoo` para conservar el filestore. Conservar el volumen PostgreSQL en su ruta de datos. Al reutilizar un entorno existente, conservar la base y ambos volúmenes. El contexto Docker contiene el código y no contiene los datos de la aplicación.

| Variable | Configuración |
| --- | --- |
| `PGHOST` | Referencia al dominio privado del servicio PostgreSQL |
| `PGPORT` | `5432` |
| `PGDATABASE` | `unicah_railway` |
| `PGUSER` | `odoo_app`, propietario de la base, sin privilegios de superusuario ni de creación de roles o bases |
| `PGPASSWORD` | Credencial del rol configurada en el gestor de variables |
| `PORT` | `8069` |
| `ODOO_MASTER_PASSWORD` | Clave maestra de gestión de bases, configurada como variable privada |
| `ODOO_ADMIN_LOGIN` | Login del administrador existente |
| `ODOO_ADMIN_PASSWORD` | Contraseña aleatoria de al menos 32 caracteres, configurada como variable privada |
| `ODOO_ADMIN_CREDENTIAL_REVISION` | Revisión de 32 caracteres hexadecimales en minúsculas |
| `ODOO_RUN_TESTS` | Usar `0` en producción |
| `ODOO_VERIFY_RUNTIME` | Usar `1` para registrar el diagnóstico de base, rol y módulo al arrancar |

El arranque crea la configuración privada de Odoo, exige TLS para PostgreSQL, restringe la selección de base a `unicah_railway` y prepara el módulo si todavía no está instalado. Una revisión nueva de credenciales actualiza el administrador existente por ORM, autentica con el mecanismo de Odoo y guarda la revisión en la misma transacción. Un reinicio con la misma revisión conserva la contraseña. Para solicitar una rotación, preparar juntos la contraseña y un identificador de revisión nuevo en las variables privadas del servicio.

## Pruebas en un entorno aislado

Ejecutar la suite del módulo solo con una base desechable y ajena a producción. Con Odoo y PostgreSQL ya configurados en ese entorno, agregar `deploy/railway/addons` al `addons_path` de la configuración de pruebas y ejecutar:

```sh
odoo -c /ruta/a/odoo-pruebas.conf -d odoo_pruebas_aislada -i ventas_unicah --without-demo=all --test-enable --test-tags /ventas_unicah --stop-after-init --no-http --max-cron-threads=0
```

La suite cubre campos y canales, vistas y agrupación, umbral de aprobación, confirmación, protección de escritura y vigencia del importe aprobado. Para comprobar un entorno ya publicado, verificar el formulario de login, la creación de una sesión y el acceso a `/odoo`. Mantener localmente los logs, capturas y resultados que incluyan datos de operación.
