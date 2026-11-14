# Verificación real

- Odoo local: 20.0, comprobado en release.py, arranque y carga de módulos.
- Base objetivo: examen_unicah, pasada explícitamente en todos los comandos Odoo.
- Servidor: puerto 8070; configuración odoo_pg18.conf; filtro ^examen_unicah$.
- HTTP de login: 200 comprobado el 13/11/2026 (hora de Honduras).
- Pruebas definitivas: **11 pruebas, 0 fallos, 0 errores**, evidence/tests_verified.log.
- Primera ejecución: tres fallos de diez, conservada en evidence/tests.log. Se corrigieron carga inicial y aislamiento de pruebas.
- Aviso de entorno: WinError 5 al limpiar archivos de solo lectura de adjuntos; aparece también en ejecución definitiva, sin fallos en tests. No se cambió el código de Odoo.
- IDs originales de convenios: 1 estudiante 15 %, 2 docente 10 %, 3 administrativo 5 %. Activos, valores y fechas conservados. Auxiliares 4 y 5 archivados reversiblemente.
- Datos de evidencia en demo_records.json: estudiante 33, docente 34, pedido 13, equipo 11, préstamo 7; ahorro calculado 60.
- No se creó ni recreó ninguna base y no se ejecutaron actualizaciones sobre odoo_dev.

## Matriz de pruebas

| Prueba | Alcance | Resultado |
| --- | --- | --- |
| test_cuenta | Longitud, vacío, letras, Unicode y modificación | Aprobada |
| test_porcentaje_y_fechas | 0, negativos, >40, límite 40 y fechas invertidas | Aprobada |
| test_aplicar_y_ahorro | Dos productos, sección, chatter y recálculos | Aprobada |
| test_vigencia_y_estado | Archivado, expirado, sin convenio y venta confirmada | Aprobada |
| test_limite_y_super | Estudiante 12 rechazado, docente 12 y estudiante 10 confirmados | Aprobada |
| test_seleccion_y_filtros | Cambio de cliente, búsqueda y agrupación con suma | Aprobada |
| test_permisos (tienda) | Vendedor lectura, gerente escritura | Aprobada |
| test_datos_iniciales_idempotentes | Dos cargas sin nuevos registros ni cambios de valores | Aprobada |
| test_ciclo_y_herencia | Entrega, doble préstamo bloqueado, devolución, disponibilidad e historial | Aprobada |
| test_validaciones | Fechas, inventario duplicado, estado y equipo archivado | Aprobada |
| test_permisos (equipos) | Usuario interno crea y escribe; no elimina | Aprobada |

## Límites de la evidencia

Los logs anteriores son ejecuciones reales. Se obtuvieron 21 capturas reales de la interfaz autenticada; evidence/screenshots.json identifica las 18 seleccionadas para el PDF. La cuenta del autor tiene trece dígitos porque así fue facilitada; las cuentas del modelo del examen siguen la regla expresa de diez.


## Comprobaciones manuales ejecutadas

- Parte 1: estudiante con cuenta y carrera visibles; docente con ambos campos ocultos.
- Parte 2: lista de tres convenios activos; menú localizado bajo Sales > Configuration > Convenios UNICAH.
- Parte 3: convenio propuesto automáticamente en S00020; botón Aplicar convenio ejecutado, descuento 15 % y mensaje de chatter observados. S00013 conserva sección y dos productos al 15 %, ahorro 60 y neto 340.
- Parte 4: se intentaron guardar cuenta de 8 dígitos, porcentaje 50 y fechas invertidas; los tres errores aparecieron y se descartaron las ediciones. S00020 (estudiante, 12 unidades) no confirmó; S00021 (docente, 12 unidades) pasó a Sales Order.
- Parte 5: se quitó My Quotations (los pedidos de demostración se crearon desde shell con OdooBot), se activaron Con convenio y agrupación Convenio; se observó el grupo y su total al pie. Se ocultaron temporalmente columnas opcionales estándar para una lectura clara en la ventana estrecha. No se utilizaron los datos de ejemplo REF000x que Odoo dibuja cuando una lista está vacía.
- Parte 6: se observó préstamo Prestado, duración 3, equipo ocupado e historial en contacto. Se ejecutó Registrar devolución y se observó Devuelto con fecha real. El doble préstamo y las fechas inválidas se probaron mediante TransactionCase, no manualmente.
- Datos adicionales reales: S00020 ID 20 y S00021 ID 21. Préstamo ID 7 terminó devuelto. S00020 se mantiene como cotización con 12 unidades para demostrar el error.
- El usuario inició sesión personalmente; no se almacenaron contraseñas en el repositorio.
- Se copiaron los archivos del filestore original al aislado sin mover ni borrar originales. Se cargó debug=assets para regenerar los recursos de interfaz que el navegador había almacenado vacíos antes de esa copia.

## Git y entrega

Repositorio público verificado mediante GitHub CLI. Commits 186c5a1, 951a8a9 y 2110943 publicados en master. La documentación, logs y PDF se incorporan en un commit adicional de entrega. El comando de publicación es git push origin master, sin force.
