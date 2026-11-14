# Justificación del Examen II Parcial

José Carlos Cáceres Girón
Cuenta del autor: 0703200603787
Programación de Negocios - Odoo 20.0
Fecha de trabajo: 13 de noviembre de 2026, America/Tegucigalpa

## Parte 1. Datos universitarios del cliente

Se extiende res.partner con tipo_cliente (estudiante, docente, administrativo y externo), numero_cuenta y carrera. La vista heredada de base.view_partner_form agrega la pestaña UNICAH. Cuenta y carrera se ocultan cuando el contacto no es estudiante; la cuenta es requerida para estudiantes. Se demuestra con la cuenta de ejemplo 0801200012 y un contacto docente. La cuenta de la portada pertenece al autor y se conserva tal como fue proporcionada; no modifica la regla de diez dígitos del ejercicio.

## Parte 2. Modelo de convenios

Se crea tienda.convenio con nombre, tipo de cliente, porcentaje, fecha inicial, fecha final opcional y activo. Tiene listas, formulario, acción y menú Ventas > Configuración > Convenios UNICAH. Los vendedores tienen lectura y los gerentes de Ventas CRUD. Odoo 20 utiliza ir.access.csv con las columnas model_id, group_id/id, operation y domain; se verificó contra el código local y mediante la carga efectiva del módulo.

¿Qué diferencia hay entre _name y _inherit? _name identifica un modelo nuevo, con su propia identidad ORM. _inherit sin _name amplía un modelo existente. Por eso tienda.convenio declara _name y las extensiones de res.partner y sale.order declaran _inherit. También se usa herencia de vistas para incorporar controles sin copiar formularios completos.

¿Por qué tienda.convenio necesita ir.access.csv y res.partner no? El modelo nuevo no trae permisos previos; sin permisos, los usuarios normales no pueden usarlo. res.partner ya tiene los permisos del módulo base, que se mantienen al añadir campos. Eso no impide establecer restricciones adicionales si el caso lo necesita. No se otorga acceso de convenios a usuarios públicos o portal.

La carga XML contiene los dos convenios exigidos. Para proteger el trabajo anterior, llama un método privado que adopta el convenio existente por tipo y registra su identificador XML; solo crea cuando falta. Los IDs originales 1, 2 y 3 conservan estudiantes 15 %, docentes 10 % y administrativos 5 %, así como sus fechas y nombres. Se verificó la idempotencia mediante una prueba específica.

## Parte 3. Convenio en el pedido

El pedido muestra el tipo del contacto, convenio propuesto y estado de aplicación. La propuesta se calcula por cliente y fecha del pedido, filtrando convenios activos y vigentes. Si coinciden varios, se elige el de inicio más reciente y luego menor ID, para que la selección sea determinista. El botón permite únicamente cotizaciones en borrador o enviadas, valida nuevamente vigencia y tipo, copia el porcentaje a las líneas de producto y registra nombre y porcentaje en chatter.

¿Qué aportan store=True y readonly=False? store=True persiste el convenio calculado en la base y permite búsquedas, agrupación y uso eficiente en listas. readonly=False permite al vendedor elegir manualmente otro convenio compatible antes de aplicarlo. Cambiar las dependencias recalcula la propuesta; el botón vuelve a comprobar que el convenio sea válido.

¿Por qué se excluyen líneas con display_type? Representan secciones o notas, no productos con cantidades e importes comerciales. Aplicarles un descuento no corresponde a la operación y puede interferir con la presentación del pedido. La prueba verifica que la sección permanece con descuento cero.

La cotización demostrativa contiene una sección, dos libros a 100 y un uniforme a 200. El convenio estudiantil aplica 15 % a las dos líneas de producto. Se obtiene un ahorro de 60 y un neto antes de impuestos de 340 sobre una base de 400. Los descuentos por línea se habilitaron para admin y prueba.convenios con autorización expresa del usuario.

## Parte 4. Validaciones

La cuenta de un estudiante debe coincidir con [0-9]{10}: exactamente diez dígitos ASCII, sin espacios, letras ni dígitos Unicode alternativos. El porcentaje debe ser mayor que cero y no superar cuarenta. Una fecha final no puede ser anterior a la inicial. Al confirmar un pedido estudiantil se suman las cantidades de producto y se rechaza un total superior a diez, con un mensaje que indica límite y cantidad solicitada. Los docentes no están sujetos a ese límite.

¿Por qué hace falta validación Python si la vista ya tiene required? La vista protege solo esa interfaz. Importaciones, llamadas ORM, RPC u otras vistas pueden escribir los mismos datos. Además required no garantiza longitud ni contenido numérico. api.constrains aplica la regla de negocio en el servidor al crear o modificar los campos declarados. Los datos históricos no se reescriben automáticamente: el contacto previo con cuenta de ocho dígitos se conserva y se identifica como pendiente de corrección por su propietario.

¿Qué pasaría si action_confirm no llamara a super()? Se interrumpiría la lógica estándar de confirmación de Ventas y la cadena de herencia: el pedido podría no pasar a venta ni ejecutar las extensiones instaladas. El método valida primero y luego retorna super().action_confirm(). La prueba comprueba tanto el rechazo de doce unidades estudiantiles como la confirmación efectiva de doce unidades docentes y diez estudiantiles.

## Parte 5. Ahorro por convenio

monto_ahorro es un Monetary calculado y almacenado con la moneda del pedido. La fórmula es la suma de precio unitario x cantidad x descuento / 100, excluyendo secciones y notas. Sigue exactamente el alcance del examen: ahorro antes de impuestos basado en los descuentos de las líneas. No separa el origen manual del descuento. Se muestra debajo del convenio cuando es positivo, como columna en listas y con suma al pie. Se agrega el filtro Con convenio y la agrupación por convenio.

¿Qué campos puso en api.depends y qué pasaría si faltara uno? order_line.price_unit, order_line.product_uom_qty, order_line.discount y order_line.display_type. Son todos los datos que determinan la fórmula o la inclusión de la línea. Si falta uno, cambiarlo puede dejar un valor almacenado obsoleto hasta que otra dependencia provoque el recálculo. Las dependencias relacionales cubren también agregar o quitar líneas. Las pruebas modifican precio, cantidad y descuento, eliminan una línea y comprueban cada resultado. También verifican búsqueda por convenio aplicado y agregación ORM por convenio.

## Parte 6. Propuesta: préstamo y control de equipos tecnológicos

¿Qué problema resuelve y quién lo usaría? Los laboratorios y la unidad de tecnología suelen registrar préstamos en papel u hojas de cálculo: es difícil saber quién tiene un portátil, cuándo debe devolverlo y si ya fue entregado a otra persona. unicah_equipos centraliza inventario, responsable, solicitante, fechas e historial. Lo utilizarían encargados de laboratorio y soporte TIC; los contactos representan a estudiantes, docentes u otros solicitantes.

¿Por qué conviene Odoo? Reutiliza contactos, usuarios, permisos, formularios, búsquedas y el chatter. El inventario y el historial comparten datos con otros procesos universitarios, evitando hojas duplicadas. El módulo es independiente: depende de base y mail, sin requerir tienda_unicah ni la aplicación de Ventas.

Diseño de modelos y campos. unicah.equipo contiene nombre, código de inventario, categoría, activo, préstamos One2many y disponibilidad Boolean calculada y almacenada. unicah.prestamo contiene referencia, equipo Many2one, solicitante Many2one a res.partner, responsable Many2one a res.users, fecha de entrega, devolución prevista, devolución real, duración Integer calculada, estado y observaciones. La duración incluye ambos extremos: del 13 al 15 son tres días. Se hereda res.partner para mostrar su historial en una pestaña Equipos UNICAH; ambos modelos nuevos incorporan chatter mediante mail.thread y actividades.

Reglas de negocio. El código de inventario no se repite; la devolución prevista no precede a la entrega; no se puede entregar un equipo archivado ni uno que ya tenga un préstamo activo. La entrega bloquea la fila del equipo en PostgreSQL para serializar operaciones concurrentes. Los botones permiten entregar desde borrador y devolver desde prestado. Devolver registra la fecha real y libera la disponibilidad. Los usuarios internos tienen creación, lectura y escritura; la eliminación está reservada a administradores del sistema. Hay vistas de lista y formulario, búsqueda, acciones y menús para ambos modelos.

¿Qué mejoraría en una segunda versión? Roles específicos de solicitante y encargado TIC, reservas con franjas de tiempo, multas y notificaciones de vencimiento, firma de recepción, adjuntos de estado físico, informes de utilización y restricciones de transiciones también para integraciones externas. Para un despliegue institucional se revisarían permisos por campus y pruebas de concurrencia con varias conexiones.

## Verificación y trazabilidad

La ejecución definitiva registra 11 pruebas funcionales, 0 fallos y 0 errores en evidence/tests_verified.log. Incluye ocho pruebas de tienda y tres de equipos; los contadores de estadísticas de Odoo también incluyen preparación de clases y no sustituyen el total final. La primera ejecución falló y se conserva en evidence/tests.log; la corrección intermedia pasó diez pruebas. No se declara que esas once pruebas sean comprobaciones manuales de interfaz: son pruebas ORM transaccionales sobre Odoo 20 real.

Las actualizaciones se dirigieron explícitamente a examen_unicah, sin eliminar ni recrear la base ni actualizar odoo_dev. No se modificó el código fuente de Odoo. Se preservó la migración anterior y el commit inicial 186c5a1. Durante la primera carga aparecieron dos convenios auxiliares; se archivaron sin eliminación, se repararon los XML IDs y se corrigió el cargador. Permanecen tres convenios activos originales. Los avisos WinError 5 de limpieza de archivos de adjuntos se deben a archivos temporales de solo lectura en Windows; persisten incluso con data_dir aislado, no causan fallos de la suite y no se modificaron permisos ni fuentes de Odoo para ocultarlos.


## Comprobación manual y evidencias

El usuario inició sesión personalmente en Odoo y se obtuvieron 21 capturas reales. El manifiesto evidence/screenshots.json selecciona 18 para esta entrega. Se observaron los campos condicionales del contacto, los tres convenios activos, la propuesta y aplicación desde el botón, las líneas con descuento y el chatter. La interfaz rechazó la cuenta de ocho dígitos, el porcentaje 50, las fechas invertidas y la confirmación estudiantil de doce unidades; se descartaron las modificaciones inválidas. El docente de S00021 confirmó doce unidades. La lista mostró filtro Con convenio, agrupación por Convenio y ahorro agregado. El equipo de prueba pasó de Prestado a Devuelto al ejecutar Registrar devolución. El doble préstamo se comprobó mediante pruebas ORM, sin atribuirlo a una prueba manual que no se realizó.
