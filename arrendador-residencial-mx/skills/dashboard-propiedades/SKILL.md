---
name: dashboard-propiedades
description: Muestra el status mensual de todas las propiedades del arrendador residencial (1-10 propiedades típicamente). Reporta por cada propiedad ocupación (rentada/vacante/remodelación), fecha último pago, días de mora si aplica, fecha próxima actualización INPC, y alertas (contrato venciendo en < 60 días, INPC pendiente de aplicar, depósito de garantía sin registrar). Vista útil al inicio del mes y para checkpoints semanales. Usar cuando el usuario diga como van mis rentas, status propiedades, dashboard arrendador, mis propiedades. NO usar para inmobiliarias administradoras (eso es inmobiliaria-mx).
allowed-tools: Read, Write
---

# Dashboard propiedades — arrendador residencial

## Cuándo activar

- "¿cómo van mis rentas este mes?"
- "status de mis propiedades"
- "dame el dashboard"
- Sesión inicial del mes (1-5 del mes)

## Output

### Resumen ejecutivo

```
🏠 Propiedades activas: 4
   ├ Rentadas: 3
   ├ Vacantes: 1 (Polanco — 45 días)
   └ En remodelación: 0

💰 Cobrado mes actual: $12,000 / $42,500 esperado de las 3 rentadas (28%)
📅 Pagos pendientes: 2 propiedades (D+7, D+15)
⚠ Alertas: 1 contrato vence en 45 días
```

### Tabla detallada

| Propiedad | Estado | Renta | Inquilino | Día pago | Status | Días mora |
|---|---|---|---|---|---|---|
| Roma Nte 1A | Rentada | $12,000 | Juan P. | 5 | ✅ Pagado | 0 |
| Roma Nte 1B | Rentada | $14,500 | María L. | 1 | 🟡 Vencido | 7 |
| Polanco | Vacante | $18,000 | — | — | — | — |
| Cdmx Sur | Rentada | $16,000 | Carlos R. | 10 | 🟡 Vencido | 15 |

### Alertas activas

1. 🔴 Cdmx Sur: D+15 sin pago — invocar `cobranza-mensual-renta` nivel 4 (formal)
2. 🟡 Roma Nte 1B: D+7 — invocar nivel 3 (firme)
3. 🟡 Polanco: vacante 45 días — sugerir bajar renta o publicar en más portales (`inm24_buscar_comparables_zona` del MCP `mp_inmuebles24`, estado sin verificar)
4. 📅 Roma Nte 1A: contrato vence 2026-08-15 — iniciar renovación 60 días antes

### Métricas anuales (acumulado)

| Métrica | YTD |
|---|---|
| Ingresos brutos cobrados | $480,000 |
| CFDIs emitidos | 36 |
| Gastos deducibles | $85,000 |
| Vacancia (%) | 8% |

## Data sources

- Tracker local de propiedades: `~/.local/share/plugins-mx/arrendador/<rfc_hash>/propiedades.json`
- Tracker pagos: `~/.local/share/plugins-mx/arrendador/<rfc_hash>/pagos.jsonl`
- `mp_bancos_mx` (cruce de pagos; hoy es un esqueleto sin datos reales → usar estado de cuenta exportado por el usuario)
- `mp_facturama_extendido` (CFDIs emitidos)

## Schema tracker

```json
{
  "propiedad_id": "RN-1A",
  "direccion": "Roma Norte ...",
  "valor_catastral": 2500000,
  "renta_mensual_mxn": "12000.00",
  "renta_actualizacion": "INPC",  // o "fijo_5%"
  "fecha_proxima_actualizacion": "2026-09-01",
  "estado_ocupacion": "rentada",
  "inquilino_id": "INQ-001",
  "fecha_inicio_contrato": "2025-09-01",
  "fecha_fin_contrato": "2026-08-31",
  "deposito_garantia_mxn": "12000.00",
  "dia_cobro_mes": 5
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Propiedad sin inquilino > 60 días | Sugerir bajar renta + `inm24_buscar_comparables_zona` (o `comparador-renta-zona-dinamica`) |
| Renta no actualizada en > 12 meses | Sugerir `actualizacion-renta-anual` (en CDMX con tope = inflación del año anterior) |
| Inquilino paga directo a cuenta sin avisar | Conciliar contra el estado de cuenta del usuario |
| Propiedad heredada mid-ejercicio | Caso fiscal especial — derivar a contador |

## Dependencias

- Tracker local (creado por skills/workflow al onboard propiedad)
- `mp_bancos_mx` (opcional; esqueleto, sin cruce automático real todavía)

## ⚠ Privacy

- Hashear RFC inquilino y números cuenta CLABE en logs
- Output puede mostrar nombres parciales (Juan P. en lugar de Juan Pérez completo)
