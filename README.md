# Examen II Parcial – Programación de Negocios

**Universidad:** Universidad Católica de Honduras (UNICAH)  
**Estudiante:** José Carlos Cáceres Girón  
**Número de cuenta:** 0703200603787  
**Asignatura:** Programación de Negocios  
**Tecnología principal:** Odoo 20.0

## Descripción

Este proyecto corresponde al segundo examen parcial de Programación de Negocios. Consiste en el desarrollo de módulos personalizados para Odoo 20, utilizando Python, PostgreSQL y archivos XML.

El proyecto está dividido en dos módulos: `tienda_unicah`, que gestiona convenios de descuento para clientes de la tienda universitaria, y `unicah_equipos`, que permite administrar préstamos de equipos tecnológicos.

## Funcionalidades desarrolladas

### Módulo tienda_unicah

- **Parte 1:** Registro del tipo de cliente, número de cuenta y carrera en los contactos.
- **Parte 2:** Creación de convenios de descuento para estudiantes, docentes y personal administrativo.
- **Parte 3:** Aplicación de convenios en cotizaciones, con descuentos por producto y registro en el historial.
- **Parte 4:** Validación de números de cuenta, porcentajes, fechas y cantidades permitidas.
- **Parte 5:** Cálculo del ahorro obtenido mediante los descuentos, con filtros y agrupaciones en Ventas.

### Módulo unicah_equipos

**Parte 6:** Se desarrolló un módulo para registrar equipos tecnológicos y controlar sus préstamos.

Permite registrar los datos del equipo, asignar un solicitante y responsable, establecer fechas de entrega y devolución, consultar la disponibilidad y mantener un historial de préstamos.

## Tecnologías utilizadas

- Odoo 20.0
- Python 3.12
- PostgreSQL 18
- XML
- Visual Studio Code
- Git y GitHub

## Instalación y ejecución

El proyecto utiliza la base de datos `examen_unicah`. Los módulos se encuentran dentro de la carpeta `examen_final`.

Desde PowerShell, con Odoo y sus dependencias previamente instaladas, se pueden actualizar los módulos mediante:

```powershell
cd C:\OdooFuente\odoo
.\.venv\Scripts\Activate.ps1

python odoo-bin -c odoo_pg18.conf -d examen_unicah -u tienda_unicah,unicah_equipos --stop-after-init --no-http
```

Para iniciar Odoo:

```powershell
python odoo-bin -c odoo_pg18.conf -d examen_unicah --db-filter=^examen_unicah$ --http-port=8070
```

Acceder desde el navegador a:

http://127.0.0.1:8070

## Pruebas realizadas

Se realizaron 11 pruebas funcionales, completadas sin fallos ni errores en la ejecución final.

También se comprobó desde la interfaz el registro de contactos, la aplicación de descuentos, las validaciones de datos y el proceso de préstamo y devolución de equipos.

Las capturas y explicaciones del funcionamiento se incluyen en el PDF de justificación entregado para el examen.

## Autor

**José Carlos Cáceres Girón**  
**Cuenta:** 0703200603787  
**UNICAH – III Período Académico 2026**
