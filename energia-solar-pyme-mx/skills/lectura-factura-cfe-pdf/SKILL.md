---
name: lectura-factura-cfe-pdf
description: Lee el recibo o factura CFE en PDF (o foto) de un usuario con paneles solares interconectados (medidor bidireccional) y extrae a JSON los datos clave - RPU, tarifa, periodo, kWh recibidos de la red, kWh entregados a la red, saldo de kWh a favor, demanda máxima y cargo por demanda, factor de potencia, DAP, IVA y total. Marca los campos que no encuentre en lugar de inventarlos. Usar cuando el usuario diga lectura factura cfe pdf, leer recibo CFE, extraer datos del recibo de luz, recibo bidireccional, recibo con paneles solares, parsear factura CFE.
allowed-tools: Read, Write
---

# Lectura de factura CFE (PDF) — medidor bidireccional

## Campos a extraer

| Campo | Dónde suele estar | Notas |
|---|---|---|
| `rpu` | Encabezado | Dato sensible: guardar hasheado en logs |
| `tarifa` | Encabezado | 1–1F, DAC, PDBT, GDBT, GDMTO, GDMTH |
| `periodo` | Encabezado | Mensual (comercial) o bimestral (doméstico) |
| `kwh_recibidos` | Lecturas del medidor | Energía tomada de la red |
| `kwh_entregados` | Lecturas del medidor | Energía inyectada por los paneles |
| `kwh_neto` / `kwh_saldo_a_favor` | Resumen de energía | Según esquema del contrato |
| `demanda_max_kw`, `cargo_demanda_mxn` | Solo tarifas con demanda (GDMTO, GDMTH, GDBT) | En GDMTH, por periodo base/intermedio/punta |
| `factor_potencia_pct` | Tarifas de media tensión | < 90% genera cargo; > 90% bonificación |
| `dap_mxn` | Desglose | Derecho de alumbrado público, cobrado por cuenta del municipio |
| `subtotal_mxn`, `iva_mxn`, `total_mxn`, `fecha_limite_pago` | Pie | |

## Flujo

1. Lee el PDF con Read (o la foto). Si es imagen de mala calidad, pide otra.
2. Extrae solo lo que está impreso. Campo ausente = `null` con nota; nunca lo estimes.
3. Valida coherencia:
   - Lectura actual − lectura anterior = kWh del periodo (por cada canal).
   - Subtotal + IVA (+ DAP, que suele sumarse después del IVA y sin IVA) = total (± $1 por redondeo).
   - IVA = 16% del subtotal de energía y demanda (8% si el recibo aplica el estímulo de región fronteriza).
4. Si algo no cuadra, pasa el JSON a `validacion-factura-cfe`.

El formato del recibo cambia según tarifa y región; no hay un parser oficial. Si el diseño es distinto al esperado, dilo y extrae lo que puedas identificar con certeza.

## Output

```json
{
  "rpu_hash": "...",
  "tarifa": "GDMTH",
  "periodo": "2026-09",
  "kwh_recibidos": {"base": 4200, "intermedio": 9800, "punta": 1300},
  "kwh_entregados": 3100,
  "kwh_saldo_a_favor": null,
  "demanda_max_kw": {"base": 60, "intermedio": 85, "punta": 70},
  "factor_potencia_pct": 88.4,
  "dap_mxn": 412.50,
  "subtotal_mxn": 48250.00,
  "iva_mxn": 7720.00,
  "total_mxn": 56382.50,
  "fecha_limite_pago": "2026-10-20",
  "campos_no_encontrados": ["kwh_saldo_a_favor"],
  "coherencia": {"subtotal_iva_dap_igual_total": true}
}
```

Ejemplo: 48,250 × 16% = 7,720; 48,250 + 7,720 + 412.50 (DAP) = 56,382.50.

## Dependencias

- `mp_cfe_facturacion.cfe_descargar_factura_mes` puede bajar el PDF (sin verificar; el portal de CFE usa CAPTCHA y sesión, así que normalmente el usuario lo descarga).
- Siguientes pasos: `credito-kwh-tracking`, `validacion-factura-cfe`, `optimizacion-tarifa-gdmth`.
