# Análisis del Excel `3. Copa_SantaFe_2026_Cartera.xlsm`

Punto de partida del sistema. El archivo original **no se modificó**.

## Hojas

| Hoja | Función real | En el aplicativo |
|---|---|---|
| **Datos** | Maestro: quién paga, club, valor pactado, cuotas, descuento, seguimiento, nota | Tabla `equipos` |
| **Registro Facturas** (Tabla1) | Facturas con saldo pendiente, cuotas, links, casillas de pago y estado | Tablas `facturas`, `cuotas`, `pagos` |
| **Pagadas** (Tabla13) | Facturas ya pagadas (se mueven a mano) | Misma tabla `facturas`: «Pagada» pasa a ser un estado calculado |
| **WOMPI** | Descripción y links de pago por cuota | Campo `link_pago` en `cuotas` |
| **Facturar** | Plantilla masiva de importación a **World Office** | Tabla `configuracion` + módulo Plantilla masiva (Fase 4) |
| **Resumen por Club** | Cartera consolidada por factura | Módulo Cartera (Fase 2) |
| **Wo** | Vacía | — |

Macros: `Macro2` y `PDF` solo exportan el Resumen a PDF. No contienen lógica de negocio.

## Flujo actual

1. Se registra el club en **Datos**.
2. Se crea la fila en **Registro Facturas** y se escribe «Facturar» en la columna FACTURAR.
3. **Facturar** filtra esos NIT y arma dos líneas por factura (una por cuota) para World Office.
4. **WOMPI** genera la descripción de cada cuota y guarda el link de pago.
5. Al pagar, se marcan las casillas `$` (cuota 1) y `$2` (cuota 2).
6. ESTADO DE PAGO calcula mora y avisos a 5 días.
7. Pagada la totalidad, la fila se mueve a **Pagadas**.

## Plantilla World Office (hoja Facturar)

57 columnas: 31 `Encab:` y 26 `Detalle:`. Valores que hoy están fijos en fórmulas y que pasaron a la tabla `configuracion`:

| Columna | Valor |
|---|---|
| Encab: Empresa | INDEPENDIENTE SANTA FE S.A. |
| Encab: Tipo Documento | FV |
| Encab: Prefijo | EF |
| Encab: Documento Número | Consecutivo manual (último: 63477) |
| Encab: Fecha / Fecha Entrega | Fecha del día |
| Encab: Tercero Interno | 1026250096 |
| Encab: Tercero Externo | NIT del equipo |
| Encab: Nota | NOTA de la hoja Datos |
| Encab: FormaPago | Credito |
| Detalle: Producto | 41601501 |
| Detalle: Bodega | Principal |
| Detalle: UnidadDeMedida | Und. |
| Detalle: Cantidad | 1 |
| Detalle: IVA | 0 |
| Detalle: Valor Unitario | VALOR TOTAL / 2 |
| Detalle: Descuento | 0 |
| Detalle: Vencimiento | Fecha del día |
| Detalle: Centro costos | 9207 Copa Santa Fe equipos invitados |

Las demás columnas (Personalizados, Sucursal, Clasificación, Bodega externa, etc.) van vacías y deben conservarse en el archivo generado.

## Problemas encontrados

**Lógica**
- VENC. CUOTA 1 y VENC. CUOTA 2 son iguales a la fecha de factura: todas las facturas quedan vencidas desde el primer día.
- Los pagos son casillas verdadero/falso: no hay fecha, valor, referencia ni abonos parciales.
- Valor Unitario fijo en VALOR TOTAL / 2, aunque haya equipos con 1 cuota (Reyes del Fútbol – Madrid).
- La búsqueda de la plantilla empieza en la fila 6: Manaos FC (fila 5) nunca se encuentra.
- Se busca por NIT: si un NIT tiene dos facturas (LGARS, 1022354458) siempre toma la primera.
- Número de documento digitado a mano.

**Fórmulas**
- Rangos fijos `Datos!$B$2:$B$25`: los registros desde la fila 26 no se encuentran.
- Hoja WOMPI con rangos desplazados al arrastrar (C5:C17, C6:C18…): mayoría de `#N/A`.
- Links buscados por nombre de club: fallan con espacios finales («MANAOS FC ») y nombres repetidos (REYES DEL FUTBOL, dos pagadores).
- Pagadas filas 24, 27 y 28: fórmula de estado con `#REF!`.

**Datos por verificar**
- NIT de 10 dígitos que parecen incluir el dígito de verificación: 9008138554 (Kanteranos), 9010549091 (BSA).
- «FV EF63478» sin espacio.
- San Antonio FC sin razón social.
- Academia Bogotana y Warriors: valor 1.500.000 en Datos, factura pagada por 3.000.000.
- Amigos Anarod: dos facturas pagadas de 3.000.000 (FV EF 53008 y FV EF 58426).
- El Excel no tiene responsable, correo, teléfono ni dirección.

## Cifras según el último cálculo guardado en el archivo

- 16 facturas abiertas: $49.590.000 facturado, $39.240.000 de cartera.
- 24 facturas pagadas: $68.910.000.
- Ingresos totales: $79.260.000.
