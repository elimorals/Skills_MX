---
name: fiscal-host-art113a
description: Cálculo fiscal del host de Airbnb/Vrbo/Booking persona física bajo Art. 113-A fr. II LISR (régimen 625 de plataformas tecnológicas). La plataforma retiene 4% de ISR sobre el hospedaje sin IVA y 50% del IVA (8%) si tienes RFC; sin RFC retiene 20% ISR y 100% IVA. Con ingresos anuales ≤ $300,000 puedes optar por que las retenciones sean pago definitivo (Art. 113-B LISR y 18-M LIVA). Además cubre el ISH estatal: en muchas entidades la plataforma lo cobra y entera; en reservas directas lo declaras tú. Usar cuando el usuario diga calcular impuestos airbnb, ISR host, ISH hospedaje, retenciones airbnb, régimen plataformas, 113-A.
allowed-tools: Read, Write
---

# Fiscal Airbnb host — Art. 113-A LISR + ISH

## Componente federal

| Concepto | Con RFC | Sin RFC | Base legal |
|---|---|---|---|
| Retención ISR | 4% del hospedaje sin IVA | 20% | Art. 113-A fr. II y 113-C LISR |
| Retención IVA | 50% del IVA trasladado (= 8% del precio) | 100% | Art. 18-M LIVA |

Verificado: la tasa de 4% para hospedaje sigue vigente en 2026 (texto del 113-A en mley.mx y guía SAT de plataformas; ninguna reforma 2026 la modificó). Fuente: https://www.sat.gob.mx/minisitio/PlataformasTecnologicas/PersonasFisicas/documentos/DisposicionesFiscales_aplicables_a_PF.pdf

La plataforma emite cada mes un **CFDI de retenciones** a tu RFC; esa es la fuente de los montos retenidos.

### ¿Pago provisional o definitivo?

- **Ingresos anuales ≤ $300,000** (incluyendo cobros directos a huéspedes) y sin otras actividades salvo sueldos o intereses: puedes optar por que la retención de ISR y la de IVA sean **pago definitivo** (Art. 113-B LISR, Art. 18-M LIVA). Ya no presentas declaración mensual por esos ingresos; los cobros directos se pagan con la misma tasa.
- **Sin la opción o con ingresos > $300,000**: la retención es pago provisional. Declaras mensual (día 17) el ISR y el IVA, acreditas lo retenido y presentas anual. Si tributas en otro régimen (612 o RESICO 626), confirma con tu contador cómo acreditar las retenciones según la RMF 2026 (**verificar**).

## Componente estatal (ISH)

- Airbnb cobra y entera el ISH en 19 entidades, entre ellas CDMX (5% casas/deptos), Quintana Roo (6%), Jalisco y Yucatán (fuente: https://es-l.airbnb.com/help/article/2288). En esas reservas **no** lo pagas tú.
- Reservas directas o estados sin convenio: tú lo cobras y lo enteras. Tasas: skill `calculador-ish-por-estado` / `mcp-servers/shared/ish_mx.py`.

## Algoritmo

```python
from decimal import Decimal as D

def calcular_fiscal_host_mes(hospedaje_sin_iva: D, tiene_rfc: bool,
                             plataforma_entera_ish: bool, tasa_ish: D,
                             opcion_definitivo: bool) -> dict:
    iva_trasladado = hospedaje_sin_iva * D("0.16")
    isr_ret = hospedaje_sin_iva * (D("0.04") if tiene_rfc else D("0.20"))
    iva_ret = iva_trasladado * (D("0.5") if tiene_rfc else D("1"))
    iva_pendiente = D("0") if (opcion_definitivo or not tiene_rfc) else iva_trasladado - iva_ret
    ish_a_cargo_host = D("0") if plataforma_entera_ish else hospedaje_sin_iva * tasa_ish
    return {
        "isr_retenido": isr_ret, "iva_retenido": iva_ret,
        "iva_por_enterar_host": iva_pendiente,
        "ish_a_cargo_host": ish_a_cargo_host,
        "declaracion_mensual_requerida": not opcion_definitivo,
    }
```

## Output (CDMX, con RFC, opción de pago definitivo, todo vía Airbnb)

```json
{
  "rfc_hash": "...",
  "mes": "2026-06",
  "estado": "cdmx",
  "regimen": "625",
  "hospedaje_sin_iva_mxn": "40700.00",
  "iva_trasladado_mxn": "6512.00",
  "isr_retenido_plataforma_mxn": "1628.00",
  "iva_retenido_plataforma_mxn": "3256.00",
  "iva_por_enterar_host_mxn": "0.00",
  "ish_cdmx_5_pct_mxn": "2035.00",
  "ish_lo_entera": "airbnb",
  "opcion_pago_definitivo": true,
  "obligacion_declaracion_mensual": false,
  "vigencia_validada": false
}
```

Si no ejerces la opción de pago definitivo, `iva_por_enterar_host_mxn` = 6,512 − 3,256 = $3,256 (antes de acreditar el IVA de tus gastos).

## Casos edge

| Caso | Acción |
|---|---|
| Ingresos anuales > $300,000 | Pierdes la opción de pago definitivo: declaraciones mensuales y anual |
| Propiedades en varios estados | ISH por estado; revisa en cuáles lo entera la plataforma |
| Huésped pide CFDI de una reserva directa | CFDI tipo I con IVA 16%; uso `G03` si lo deducirá, `S01` si no |
| Varias plataformas (Vrbo + Booking) | Cada una retiene por separado; suma ingresos para el tope de $300,000 |

## ⚠ Compliance

- El ISH y sus tasas cambian por ley estatal: valida cada año.
- `vigencia_validada: false`: un contador debe revisar antes de declarar.
