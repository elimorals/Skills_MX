---
name: calculador-ish-por-estado
description: Calcula el ISH (Impuesto Sobre Hospedaje) estatal de una propiedad Airbnb/Vrbo/Booking según la entidad donde está el inmueble (tasas 2026 de 2% a 6%; varias entidades tienen tasa distinta para casas y departamentos vía plataforma). Distingue cuándo la plataforma ya cobra y entera el ISH por ti y cuándo debes declararlo tú (reservas directas o estados sin convenio). Distinto a fiscal-host-art113a, que cubre el lado federal (ISR/IVA). Usar cuando el usuario diga ISH, impuesto hospedaje, impuesto sobre hospedaje, hospedaje estatal, impuesto estatal airbnb, cuánto ISH pago.
allowed-tools: Read, Write
---

# Calculador ISH por estado

Fuente de tasas: el catálogo del repo `mcp-servers/shared/ish_mx.py` (tools `ish_calcular` / `ish_info_estado` del MCP `mp_ish_mx`). **No copies tasas a mano**: consulta el catálogo, que trae tasa, fuentes y nivel de confianza por estado. Las tasas 2026 están verificadas solo contra fuentes secundarias (confianza media; algunas en conflicto).

## Tasas 2026 de referencia (extracto de `ish_mx.py`, revisado 2026-10-14)

| Estado | Tasa general | Casas/deptos vía plataforma | Confianza |
|---|---|---|---|
| CDMX | 3.5% | 5% | media |
| Quintana Roo | 5% | 6% | media |
| Yucatán | 4.5% (baja en 2026) | — | media |
| Jalisco | 4% | — (Airbnb reporta 5%) | baja |
| Baja California Sur | 4% | — | media |
| Estado de México | 4% | — (subsidio 50% a estancias > 15 días) | media |
| Sinaloa | 3% | — | media |
| Veracruz | 2% | — (3% a plataformas aprobado, vigencia dudosa) | baja |

## Paso 1 — ¿La plataforma ya lo cobra?

Airbnb cobra el ISH al huésped y lo entera al estado en 19 entidades, entre ellas CDMX, Quintana Roo, Jalisco, Yucatán, BCS, Estado de México, Nayarit, Nuevo León, Oaxaca, Puebla y Querétaro (fuente: https://es-l.airbnb.com/help/article/2288, consultada 2026-10-14). Para Vrbo/Booking revisa su centro de ayuda.

- **La plataforma lo cobra** → no lo pagas tú sobre esas reservas; verifica que aparezca en el desglose de la reserva. Confirma con la tesorería estatal si igual te exige registro o declaración.
- **Reserva directa o estado sin convenio** → tú lo cobras al huésped y lo enteras al estado.

## Paso 2 — Calcular

Base: el monto del hospedaje **antes de IVA** (Airbnb incluye la tarifa de limpieza en la base). `ish = base × tasa`.

Ejemplo: reserva directa en CDMX (sin plataforma, tasa general 3.5%; vía plataforma sería 5%):
- Base $40,700 × 3.5% = **$1,424.50**

## Output

```json
{
  "estado": "cdmx",
  "canal": "reserva_directa",
  "tasa_aplicable": 0.035,
  "base_hospedaje_sin_iva_mxn": "40700.00",
  "ish_a_pagar_mxn": "1424.50",
  "lo_entera_la_plataforma": false,
  "plazo_pago": "verificar en la tesorería estatal (CDMX: declaración mensual)",
  "portal_pago": "https://www.finanzas.cdmx.gob.mx",
  "confianza_tasa": "media",
  "vigencia_validada": false
}
```

## ⚠ Compliance

- Tasas, bases y plazos cambian por ley estatal cada año: confirma con la tesorería estatal antes de declarar.
- Valida con un contador local; este cálculo no sustituye la revisión profesional.
