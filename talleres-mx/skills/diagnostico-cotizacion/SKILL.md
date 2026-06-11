---
name: diagnostico-cotizacion
description: Flow estructurado para diagnóstico de vehículos y generación de cotización clara con desglose de mano de obra (horas y tarifa), refacciones (con marca, número de parte, precio), insumos (filtros, líquidos, juntas), tiempo estimado de entrega y vigencia. Documenta el diagnóstico con fotos/video del problema, identifica trabajos relacionados que conviene hacer simultaneamente (ahorro de mano de obra), y proyecta vida útil de componentes que podrían fallar pronto. Estandariza presentación al cliente para evitar disputa por ambigüedad. Usar cuando el usuario diga diagnóstico, cotización taller, cotizar reparación, cotizar auto, presupuesto mecánico, vehicle quote, service estimate. NO usar para cotizaciones de venta de auto usado (otra cosa) ni para cotizaciones de seguros (otra cosa).
allowed-tools: Read, Write, Edit
---

# Diagnóstico y cotización de servicios automotrices

El flujo que resuelve el problema #1 del taller mexicano promedio: la cotización ambigua que termina en disputa con el cliente.

## Estructura del diagnóstico

```markdown
# Diagnóstico Vehicular

**Folio**: DIAG-XXXX
**Fecha**: DD/MM/AAAA
**Taller**: [Nombre]
**Mecánico diagnosticador**: [Nombre]

## Datos del vehículo
- Marca: [marca]
- Modelo: [modelo]
- Año: [año]
- Versión / sub-modelo: [versión]
- VIN: [opcional pero recomendado para refacciones]
- Placas: [placas]
- Kilometraje al ingreso: [km]
- Color: [color]

## Datos del propietario
- Nombre: [nombre]
- Teléfono / WhatsApp: [número]
- Email: [opcional, para CFDI]
- ¿Requiere CFDI?: sí/no
  - Si sí: RFC, razón social, régimen, CP, uso CFDI

## Reporte de síntomas (lo que reporta el cliente)
[Transcripción de lo que el cliente describió. Verbatim si es posible.]
Ejemplo: "Cuando freno fuerte chilla. Cuando voy en bajada se siente que vibra."

## Diagnóstico técnico (lo que encontró el mecánico)
### Hallazgos
1. **Sistema [nombre]**: [descripción del estado]
   - Pieza específica: [...]
   - Estado: [bueno / desgastado / dañado / falla]
   - Causa probable: [...]

2. **Sistema [nombre]**: ...

### Fotos / video adjuntas
- [archivo 1]: descripción
- [archivo 2]: descripción
[Subir a la conversación con cliente]

### Pruebas realizadas
- [Prueba 1]: resultado
- [Prueba 2]: resultado

## Cotización propuesta

### Trabajos urgentes (de seguridad o que detienen el auto)
| # | Trabajo | Refacción | Marca/Parte # | Mano de obra | Precio refacción | Subtotal |
|---|---|---|---|---|---|---|
| 1 | Cambio balatas delanteras | Balata delantera | Brembo PD7589 | $450 | $1,200 | $1,650 |
| 2 | Cambio rotores | Rotor par delantero | Brembo 08.5181.21 | $300 | $2,400 | $2,700 |

Subtotal trabajos urgentes: $X,XXX

### Trabajos recomendados (no urgentes pero conveniente hacer ahora)
| # | Trabajo | Razón | Subtotal |
|---|---|---|---|
| 3 | Cambio filtro de aire | Vencido por km | $250 |
| 4 | Cambio aceite y filtro motor | Próximo a vencer | $800 |

Subtotal recomendados: $X,XXX

### Trabajos opcionales (mejora o estética)
| # | Trabajo | Razón | Subtotal |
|---|---|---|---|
| 5 | Lavado y pulido faros | Estética + visibilidad | $400 |

Subtotal opcionales: $XXX

### Resumen económico
- Mano de obra total: $X,XXX
- Refacciones e insumos: $X,XXX
- **Subtotal**: $X,XXX MXN
- **IVA 16%**: $X,XXX MXN
- **Total con IVA**: $X,XXX MXN

Sin IVA (si cliente no requiere CFDI): $X,XXX MXN

## Plazos
- Tiempo estimado de mano de obra: [horas]
- Tiempo de entrega: [día / horas hábiles desde aprobación]
- Si requiere ordenar refacción no disponible: [agregar 1-3 días según pieza]

## Condiciones
- Vigencia de cotización: 7 días calendario
- Cambios al diagnóstico tras desarme pueden generar costos adicionales que se notificarán al cliente para autorización adicional
- Garantía: 30 días mano de obra, 90 días refacciones nuevas (PROFECO mínimo)
- Forma de pago: efectivo, transferencia, tarjeta. CFDI emitido contra pago.

## Autorización

Para autorizar los trabajos, responder por WhatsApp/email con qué trabajos aprueba:
- "Apruebo urgentes" (trabajos 1, 2)
- "Apruebo urgentes y recomendados" (1-4)
- "Apruebo todo" (1-5)
- "Solo trabajos urgentes" (1, 2)
- "No autorizo, recojo el auto" — el cliente puede retirar el vehículo previo pago del costo del diagnóstico ($XXX MXN)
```

## Reglas de buena cotización

### 1. Desglosar SIEMPRE: mano de obra vs refacción
El cliente debe ver qué paga por trabajo del mecánico y qué por las piezas. La opacidad genera desconfianza.

### 2. Identificar urgencia
**Urgente**: el auto no puede salir así, riesgo de seguridad o daño mayor.
**Recomendado**: se puede esperar, pero conviene hacerlo ahora (kilometraje, sinergia de mano de obra).
**Opcional**: mejora estética o de confort sin urgencia.

Esta categorización permite al cliente decidir sin sentir presión por todo.

### 3. Marca y número de parte de la refacción
Si dices "balata genérica", el cliente sospecha. Si dices "Brembo PD7589, parte original equivalente", hay sustento.

Permitir al cliente elegir gama:
- Original (más caro, garantizado)
- OEM equivalente (calidad similar, marca distinta)
- Genérico (más barato, garantía menor)

Cada uno con precio claro.

### 4. Sinergia de mano de obra
Si para cambiar la balata hay que quitar la rueda y el cliente también necesita rotación de llantas, mencionar que la mano de obra de la rotación se reduce porque ya está desarmado. Esto fomenta venta cruzada honesta.

### 5. Foto/video del problema
**OBLIGATORIO en cualquier trabajo > $5,000 MXN**. Reduce disputas dramáticamente.
- Foto del estado del componente desgastado.
- Si es ruido/vibración, video corto durante prueba.
- Foto de kilometraje en tablero al ingreso.

### 6. Costo del diagnóstico
Si el cliente no aprueba ningún trabajo, debe cubrir el costo del diagnóstico (típico $200-500 según el tiempo invertido). Esto se declara desde el inicio para evitar conflicto.

## Catálogo común de servicios + precios referencia (CDMX, ajustar región)

| Servicio | Tiempo MO | Tarifa MO típica | Refacciones |
|---|---|---|---|
| Cambio aceite + filtro | 0.5h | $250-400 | $400-1,200 según aceite |
| Cambio balatas delanteras | 1h | $400-600 | $800-2,500 |
| Cambio rotores delanteros (par) | 1.5h | $500-800 | $1,800-4,500 |
| Afinación menor | 2h | $800-1,500 | $600-1,500 |
| Afinación mayor | 4h | $1,800-3,000 | $1,500-3,500 |
| Servicio de frenos completo | 3h | $1,200-2,000 | $2,500-6,500 |
| Cambio embrague | 6-8h | $3,000-5,000 | $4,500-12,000 |
| Cambio amortiguadores (4) | 2.5h | $1,200-2,000 | $3,000-9,000 |
| Diagnóstico OBD2 + reporte | 0.5h | $200-500 | — |

Tarifa horaria mecánica común: $400-700/h taller independiente, $800-1,500/h agencia.

## Salida esperada

Cuando el usuario hace nuevo diagnóstico:

1. Captura datos del vehículo y propietario.
2. Captura síntomas del cliente verbatim.
3. Estructura el diagnóstico técnico con hallazgos categorizados.
4. Genera cotización con trabajos urgentes/recomendados/opcionales y desglose.
5. Genera resumen para enviar por WhatsApp con foto/video del problema.
6. Guarda en `diagnosticos/[fecha]-[VIN-o-placas]/diagnostico.md`.

## Integración

- `autorizacion-cliente-wa`: el cliente responde por WA aprobando trabajos específicos.
- `orden-trabajo`: una vez autorizado, se convierte en OT formal con firma.
- `cfdi-emision`: al cierre, se emite CFDI por los trabajos efectivamente realizados.
- `garantia-servicio`: la garantía aplica a partir del cierre de la OT.
- `mxn-formato`: para todos los importes.
