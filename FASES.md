# Fases del proyecto

## Fase 1 — terminada

**Construido**
- Proyecto Django listo para GitHub, con pruebas automáticas (11) que corren en cada cambio.
- Base de datos con todas las tablas y relaciones (ver MODELO_DATOS.md), incluidas las de fases siguientes para no rehacer la estructura.
- Ingreso con usuario y contraseña.
- Inicio: equipos registrados, activos, por facturar, facturas generadas, cartera total, total recaudado, accesos rápidos y últimos movimientos.
- Equipos: lista con buscador (club, razón social, NIT, responsable, correo), filtros por estado y seguimiento, paginación, saldo pendiente por equipo.
- Crear, editar, consultar, activar y desactivar equipos. Sin eliminación.
- Ficha del equipo: facturación, contacto, cartera, facturas, pagos e historial.
- Validaciones: documento solo numérico, equipo duplicado, descuento mayor que el valor, aviso de NIT con posible dígito de verificación pegado.
- Auditoría de creación, edición y activación de equipos.
- Configuración de World Office editable en Administración, con los valores tomados de la hoja Facturar.

**No incluido a propósito**
- La importación del Excel es Fase 3. Mientras tanto, los equipos se registran desde el formulario.

## Decisiones pendientes antes de la Fase 2

1. **Plazo real de cada cuota.** El Excel vence ambas cuotas el mismo día de la factura. Se configura en Administración → Configuración (días cuota 1 y cuota 2).
2. Regla de «Pago parcial» frente a «Pendiente»: propuesta = parcial si hay algún pago y saldo > 0.
3. Confirmar los valores a verificar listados en ANALISIS_EXCEL.md (NIT con DV, Academia Bogotana, Warriors, Anarod).

## Fase 2 — Facturación y cartera

- Registrar factura asociada a un equipo, con generación automática de sus cuotas.
- Estados calculados por factura: Al día, Por vencer, Vencida, Pago parcial, Pagada.
- Días de mora y rangos: 0, 1–30, 31–60, 61–90, 91–120, más de 120.
- Módulo Cartera con filtros y buscador (quién debe, cuánto, qué factura, desde cuándo).
- Registrar pago por cuota; saldo y estado se actualizan solos.
- Tarjetas de cartera vencida, por vencer y facturas pendientes en el inicio.

## Fase 3 — Importación y exportación

- Importar el Excel: leer hojas, vista previa, nuevos / existentes / con errores, confirmar.
- Casillas `$` y `$2` marcadas → pagos con referencia «Importado del Excel».
- Exportar equipos, facturación y cartera a Excel y CSV.

## Fase 4 — Plantilla masiva World Office

- Selección, validación y generación del archivo con las 57 columnas de la hoja Facturar.
- Consecutivo automático y registro de cada plantilla generada.

## Fase 5 — Mejoras

- Roles y permisos (consulta, tesorería, administrador), auditoría completa y dashboard avanzado.
