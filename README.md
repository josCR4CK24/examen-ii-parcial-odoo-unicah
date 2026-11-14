# EXAMEN II PARCIAL - Programación de Negocios

**Autor:** José Carlos Cáceres Girón
**Número de cuenta del autor:** 0703200603787
**Plataforma verificada:** Odoo 20.0 / PostgreSQL 18 / Python 3.12
**Repositorio:** https://github.com/josCR4CK24/examen-ii-parcial-odoo-unicah

## Alcance

| Parte | Implementación |
| --- | --- |
| 1 | Pestaña UNICAH en contactos, tipo de cliente, cuenta y carrera con visibilidad condicional. |
| 2 | Modelo tienda.convenio, permisos Odoo 20, datos XML idempotentes y menú Ventas > Configuración > Convenios UNICAH. |
| 3 | Convenio vigente automático y editable, botón Aplicar convenio, descuentos en productos y mensaje en chatter. |
| 4 | Cuenta de exactamente 10 dígitos ASCII, porcentaje > 0 y <= 40, fechas válidas y límite estudiantil de 10 unidades al confirmar. |
| 5 | Ahorro almacenado y recalculado, campo en formulario, columnas y suma al pie, filtro Con convenio y agrupación Convenio. |
| 6 | Módulo independiente unicah_equipos: inventario, préstamos, devolución, disponibilidad calculada, permisos, vistas y herencia de contactos. |

El número de cuenta del autor se reproduce tal como fue proporcionado. Es un dato de portada; la validación de diez dígitos aplica a los contactos estudiantes del escenario del examen. No se cambia esa regla a trece dígitos.

## Estructura

```text
tienda_unicah/
  models/                 # Contactos, convenios y pedidos heredados
  data/convenio_data.xml   # Dos convenios iniciales, adopción sin duplicados
  security/ir.access.csv   # Formato operation/domain de Odoo 20
  views/                  # Formularios, listas, filtros y menú
  migrations/20.0.1.1/     # Migración anterior preservada
  tests/test_tienda.py     # Pruebas transaccionales de las Partes 1 a 5
unicah_equipos/
  models/                 # unicah.equipo, unicah.prestamo, res.partner
  security/ir.access.csv
  views/                  # Listas, formularios, búsqueda y navegación
  tests/test_equipos.py
scripts/                  # Auditoría y preparación reproducible de evidencias
output/pdf/               # Justificación final
docs/                    # Respuestas y matriz de comprobación
evidence/                # Logs reales, datos demostrativos y capturas disponibles
```

## Instalación y actualización segura

Los comandos siguientes se ejecutan desde `C:\OdooFuente\examen_final` en PowerShell. La configuración compartida tiene `db_name = odoo_dev`: **siempre especificar `-d examen_unicah`**. No se debe eliminar ni recrear la base, ni ejecutar una actualización sin ese argumento.

```powershell
$py = 'C:\OdooFuente\odoo\.venv\Scripts\python.exe'
$odoo = 'C:\OdooFuente\odoo\odoo-bin'
$conf = 'C:\OdooFuente\odoo\odoo_pg18.conf'
# Primera instalación en una base de examen ya creada:
& $py $odoo -c $conf -d examen_unicah -i tienda_unicah,unicah_equipos --stop-after-init --no-http --max-cron-threads=0
# Actualizar una instalación existente:
& $py $odoo -c $conf -d examen_unicah -u tienda_unicah,unicah_equipos --stop-after-init --no-http --max-cron-threads=0
# Iniciar el servidor exclusivo del examen:
& $py $odoo -c $conf -d examen_unicah '--db-filter=^examen_unicah$' --http-port=8070 --max-cron-threads=0
```

Abrir http://127.0.0.1:8070/odoo?db=examen_unicah. El repositorio ya está al final del `addons_path` de la configuración existente. No se modificó el código fuente de Odoo ni su configuración compartida.

Para esta ejecución se usó además `--data-dir=C:/OdooFuente/examen_final/.odoo-runtime` para mantener los archivos generados dentro del repositorio (carpeta excluida de Git). Este filestore es independiente del original; al volver al data_dir original, los adjuntos de la ejecución aislada pueden no estar disponibles. Los campos, pedidos y convenios se guardan en PostgreSQL.

## Uso y comprobación

1. Contactos: abrir «Estudiante Evidencia UNICAH», pestaña UNICAH: cuenta `0801200012` y carrera. Abrir «Docente Evidencia UNICAH» para comprobar campos ocultos.
2. Ventas > Configuración > Convenios UNICAH: estudiantes 15 %, docentes 10 %, administrativos 5 %. Los registros originales IDs 1, 2 y 3 se conservaron con fechas 01/11/2026 a 31/12/2026.
3. Activar descuentos en Ventas. Se autorizó y activó el grupo de descuentos por línea para `admin` y `prueba.convenios` en la base de examen. En una cotización del estudiante, agregar sección y dos productos y pulsar Aplicar convenio. Se excluyen secciones y notas; se registra el nombre y porcentaje en chatter.
4. Intentar guardar cuenta `12345678`, descuento 50 y fechas invertidas. Intentar confirmar 12 unidades para estudiante; repetir con docente. Los primeros casos deben impedirse y el docente debe confirmar.
5. En Cotizaciones, comprobar columnas Convenio y Ahorro, suma al pie, filtro Con convenio y agrupación Convenio. Datos de evidencia: 2 libros x 100 + 1 uniforme x 200, descuento 15 %, ahorro 60, neto sin impuestos 340.
6. Equipos UNICAH > Equipos y Préstamos. Entregar un equipo, intentar una segunda entrega del mismo equipo, registrar devolución. El contacto muestra su historial en Equipos UNICAH.

La propuesta automática usa la fecha del pedido y, ante varios convenios vigentes, el más reciente por fecha de inicio y luego menor ID. El botón valida nuevamente tipo, vigencia, estado y existencia de productos. El ahorro sigue literalmente la fórmula del examen: precio x cantidad x descuento / 100, antes de impuestos y para todos los descuentos presentes en las líneas; no es un cálculo fiscal ni una distinción entre descuentos manuales y descuentos del convenio.

## Pruebas

```powershell
& $py $odoo -c $conf -d examen_unicah -u tienda_unicah,unicah_equipos --test-enable --test-tags /tienda_unicah,/unicah_equipos --stop-after-init --no-http --max-cron-threads=0 --data-dir=C:/OdooFuente/examen_final/.odoo-runtime --logfile=C:/OdooFuente/examen_final/evidence/tests_verified.log
```

Las pruebas usan `TransactionCase` y revierten sus registros; no son una recreación de la base. Cubren cuentas, porcentajes, fechas, selección, aplicación, secciones, chatter, cálculo y recálculo, confirmación, filtro y agrupación, permisos, datos XML idempotentes, préstamo, devolución y disponibilidad.

Consultar `evidence/tests_verified.log` y `docs/VERIFICACION.md` para el resultado definitivo. `evidence/tests.log` conserva la primera ejecución fallida; `tests_final.log` registra la corrección intermedia con diez pruebas aprobadas. No se presentan esos intentos fallidos como exitosos.

## Conservación e incidencias

- Se conservó el commit inicial `186c5a1`, los cambios locales de migración y los tres convenios originales.
- La primera carga XML generó dos auxiliares (IDs 4 y 5). Se corrigió el cargador y se archivaron reversiblemente, sin eliminarlos; los XML IDs apuntan a 1 y 2. En la lista normal hay exactamente tres convenios activos. Ver `scripts/reconcile_seed.py` y logs. Ese script es histórico: no es parte del procedimiento habitual de instalación.
- El contacto previo ID 6 tiene cuenta `20260001` (8 dígitos). Se conservó sin alterarlo. La nueva regla bloqueará cambios a su tipo/cuenta si no se corrige; no se inventó su cuenta. La demostración usa un contacto nuevo válido.
- Los primeros tests mostraron avisos WinError 5 al limpiar adjuntos en el filestore original. La ejecución final utiliza el directorio aislado del repositorio y también presenta ese aviso por archivos de solo lectura, sin fallos de pruebas. No se alteraron permisos de Windows.
- Los datos iniciales se definen en XML mediante llamadas a un método privado: si ya existe el tipo, se adopta y se conserva; si falta, se crea. No se sobrescriben fechas, nombres ni porcentajes del trabajo anterior.
- `unicah_equipos` depende solo de `base` y `mail`, no de `tienda_unicah`. Los usuarios internos pueden crear, leer y actualizar; la eliminación queda para administradores del sistema. Los vendedores leen convenios; gerentes de Ventas los administran.
- El módulo de equipos es una versión académica: se propone para otra versión incluir roles específicos de TIC, reservas por franjas, sanciones, notificaciones de vencimiento, firma de recepción y auditoría más estricta de cambios de estado por integraciones.

## Entrega

La justificación está en `output/pdf/justificacion_examen_unicah.pdf`; su contenido editable está en `docs/JUSTIFICACION.md`. Se obtuvieron 21 capturas reales de la base exclusiva; 18 están seleccionadas por parte en `evidence/screenshots.json` e integradas en el PDF. El estado de publicación y cualquier paso manual se documentan en `docs/VERIFICACION.md`.


El usuario inició sesión personalmente para las evidencias. El préstamo ID 7 se entregó y devolvió desde la interfaz. Las cotizaciones S00020 y S00021 comprueban respectivamente el rechazo estudiantil y la confirmación docente de doce unidades. Se copiaron los archivos del filestore original al aislado sin eliminar ni mover los originales; `?debug=assets` permitió cargar los recursos sin la caché previa vacía.

Para ejecutar los scripts de evidencia con acentos correctos desde PowerShell, evitar canalizar directamente su contenido como texto; cargar el archivo UTF-8 dentro del shell de Odoo, por ejemplo:

```powershell
'exec(open("C:/OdooFuente/examen_final/scripts/seed_evidence.py", encoding="utf-8-sig").read())' | & $py $odoo shell -c $conf -d examen_unicah --no-http --max-cron-threads=0 --data-dir=C:/OdooFuente/examen_final/.odoo-runtime
```

`seed_evidence.py` también activa el grupo de descuentos para los dos usuarios expresamente autorizados; revisar esa sección antes de reutilizarlo en otro entorno. `normalize_demo.py` registra la corrección de codificación de los datos propios creados en esta sesión.
