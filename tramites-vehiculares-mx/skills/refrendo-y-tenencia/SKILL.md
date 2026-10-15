---
name: refrendo-y-tenencia
description: Estima el refrendo anual (control vehicular / derechos de placas) y la tenencia vehicular 2026 por estado, con el subsidio de tenencia donde existe (CDMX y EdoMex hasta $638,000 de valor factura, Querétaro "Cero Tenencia" hasta $800,000). Usa el catálogo verificado de mp_tenencia_mx; si el estado no tiene monto 2026 verificado, lo dice y manda al portal oficial. Genera resumen del costo del año, fecha límite y condiciones del subsidio. Usar cuando el usuario diga refrendo, tenencia, control vehicular, cuánto pago de placas, pago anual del auto, subsidio tenencia, derechos vehiculares. NO usar para multas (multas-deteccion-pago) ni verificación (verificacion-vehicular).
allowed-tools: Read, Write
---

# Refrendo y tenencia anual (2026)

## Conceptos

- **Refrendo / control vehicular**: derecho estatal anual por mantener placas y tarjeta vigentes. Lo cobran todos los estados del catálogo; el nombre y el monto cambian por estado (en NL depende del año modelo).
- **Tenencia**: impuesto estatal sobre la propiedad del vehículo. En 2026 la cobran CDMX, EdoMex y Querétaro, pero con **subsidio del 100%** si el valor factura (con IVA) no pasa el umbral y se cumplen las condiciones. Arriba del umbral se paga la tarifa progresiva del código fiscal estatal.
- CDMX **sí** tiene tenencia: lo que existe desde 2012 es un subsidio condicionado, no una eliminación.

## Datos 2026 (fuente: `mcp-servers/shared/tenencia_mx.py`, revisado 2026-10-14)

| Estado | Tenencia | Umbral subsidio 100% | Refrendo 2026 | Confianza |
|---|---|---|---|---|
| CDMX | Sí | ≤ $638,000 | $760 | media (prensa citando SAF) |
| EdoMex | Sí | ≤ $638,000 (placas 2021+; 50% con placas 2020) | $990 (otras notas: $960) | media |
| Querétaro | Sí ("Cero Tenencia") | ≤ $800,000, refrendo pagado ene–mar, motos excluidas | varía con el valor ($760–$1,300) | media |
| Jalisco | No | — | $1,000 (otra fuente: $1,100) | baja |
| Nuevo León | No | — | depende del año modelo, confirmar en ICVNL | baja |
| Puebla, Morelos | No (sin confirmar) | — | $700 / $814 | baja |
| Hidalgo, Oaxaca, Tlaxcala | No (sin confirmar) | — | sin monto 2026 verificado | baja |

Estados fuera de esta tabla: no hay dato. Di que no está en el catálogo y da el portal de finanzas del estado; no estimes.

**Fecha límite**: el subsidio de CDMX, EdoMex y Querétaro exige pagar en el primer trimestre (límite reportado: 31-mar-2026). Pagar después hace perder el subsidio y genera recargos. Otros estados: confirmar en su portal.

## Flujo

1. Pide estado de registro, valor factura **con IVA**, año modelo y si tiene adeudos de años anteriores.
2. Llama `tenencia_calcular(estado, valor_factura, anio_modelo, anio_actual=2026)` (MCP `mp_tenencia_mx`, cálculo local). Para comparar estados: `tenencia_comparar_estados`.
3. Interpreta la respuesta:
   - `subsidio_100_elegible: true` → tenencia $0 **si** cumple `condiciones_subsidio` (sin adeudos, tarjeta vigente, pago en plazo). Pregúntalo; no lo asumas.
   - `tenencia_mxn: null` y `requiere_calculo_oficial: true` → valor arriba del umbral. No calcules la tarifa progresiva: manda a `portal_url`.
   - `refrendo_mxn: null` → monto 2026 no verificado; dilo.
   - Copia `confianza`, `fuentes` y `advertencias` al resumen.
4. Para el monto exacto y la línea de captura: `cdmx_consultar_tenencia` o `edomex_consultar_tenencia`. Hoy devuelven `requiere_humano: true` (CAPTCHA). En ese caso entrega al usuario `url` y `pasos` del handoff; no prometas el adeudo.

## Ejemplo (CDMX, auto 2023 con factura de $420,000)

- $420,000 ≤ $638,000 → subsidio elegible, tenencia $0 si cumple condiciones.
- Refrendo: $760.
- Total estimado 2026: **$760**, pagando antes del 31-mar-2026.

Mismo auto con factura de $700,000: tenencia = tarifa del Código Fiscal CDMX (no calculada aquí) + $760 de refrendo → `requiere_calculo_oficial`.

## Output

```json
{
  "placa_hash": "...",
  "ejercicio": 2026,
  "entidad": "cdmx",
  "valor_factura_mxn": "420000.00",
  "subsidio_100_elegible": true,
  "condiciones_por_confirmar": ["sin adeudos anteriores", "tarjeta de circulación vigente"],
  "tenencia_mxn": "0.00",
  "refrendo_mxn": "760.00",
  "total_estimado_mxn": "760.00",
  "fecha_limite_subsidio": "2026-03-31",
  "confianza": "media",
  "fuentes": ["..."],
  "requiere_calculo_oficial": false,
  "portal_url": "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Valor factura arriba del umbral | `tenencia_mxn: null` → monto en portal oficial |
| Adeudos de años anteriores | Pierde el subsidio en CDMX/EdoMex/Qro; primero regularizar |
| Vehículo eléctrico o híbrido | Varios estados lo exentan; confirmar en el portal, no asumir |
| Placas de otro estado | Aplican las reglas del estado emisor de las placas |
| Cambio de propietario | Los adeudos siguen al vehículo; revisarlos antes de comprar |
| Año distinto de 2026 | El catálogo es 2026; avisar que los montos cambian cada año |

## Dependencias

- `mp_tenencia_mx`: `tenencia_calcular`, `tenencia_info_estado`, `tenencia_listar_estados`, `tenencia_comparar_estados` (cálculo local; montos de prensa).
- `mp_cdmx_municipal.cdmx_consultar_tenencia`, `mp_edomex_municipal.edomex_consultar_tenencia` (entrega a humano por CAPTCHA).

## Advertencias

- Los montos 2026 vienen de notas de prensa que citan a las secretarías de finanzas (confianza media o baja); no se localizó el acuerdo de subsidio en gaceta. Confirmar en el portal oficial antes de pagar.
- No es asesoría fiscal; el adeudo oficial es el que da la secretaría de finanzas del estado.
