---
name: iva-retenciones-mx
description: Calcula correctamente IVA y retenciones aplicables a operaciones mexicanas. Cubre tasas vigentes (16% general, 8% región fronteriza norte/sur, 0% tasa especial, exento), retenciones de ISR e IVA por régimen del emisor y receptor (servicios profesionales PFAE→PM: ISR 10% + IVA 10.6667%; arrendamiento; servicios de autotransporte; comisiones; honorarios médicos), y régimen simplificado de confianza (RESICO) PF y PM. Usar siempre que el usuario diga IVA, retención, ISR retenido, RESICO, frontera, tasa cero, exento, calcular impuestos de un servicio o factura, deduction, withholding tax, o cuando se va a emitir un CFDI y hay que determinar qué impuestos trasladar/retener. NO usar para impuestos locales (ISN nómina, predial, ISAI) ni para impuestos federales no operativos (DTA aduanal, IEPS de combustibles).
allowed-tools: Read, Write, Edit
---

# IVA y Retenciones México

Este skill aplica las reglas vigentes de IVA y retenciones del ISR/IVA en México. Su objetivo: que ningún CFDI salga con un cálculo incorrecto que después le cause una corrección o multa al usuario.

## Tasas de IVA vigentes

| Tasa | Aplicación |
|---|---|
| **16%** | General — la mayoría de bienes y servicios en territorio nacional |
| **8%** | Región Fronteriza Norte y Sur (decreto vigente; verificar municipios incluidos cada año) |
| **0%** | Exportación de bienes/servicios, alimentos básicos no procesados, medicinas de patente, agua para uso doméstico, libros, etc. |
| **Exento** | Servicios médicos profesionales (NO incluye hospitales), enseñanza pública, intereses bancarios a PF, etc. |

Diferencia crítica entre 0% y exento:
- **Tasa 0%** sí genera IVA acreditable para quien lo paga (aunque sea cero). El emisor sí desglosa el impuesto en el CFDI con valor 0.00.
- **Exento** no genera IVA acreditable. En el CFDI se marca con `TipoFactor = "Exento"` sin TasaOCuota.

## Retenciones de ISR e IVA — los casos más comunes

### Servicios profesionales PF → PM (el caso clásico de freelancer factura a empresa)
- Emisor: Persona Física régimen 612 (PFAE) o 605 (asimilados a salarios, distinto trato)
- Receptor: Persona Moral
- **Retención ISR**: 10% sobre el monto del servicio
- **Retención IVA**: 10.6667% sobre el IVA trasladado (equivale a 2/3 partes del IVA al 16%)

Ejemplo: servicio de $10,000 MXN
```
Subtotal:                  $10,000.00
IVA 16% trasladado:        $ 1,600.00
Retención ISR 10%:        −$ 1,000.00
Retención IVA 10.6667%:   −$ 1,066.67
                          ───────────
Total a pagar al emisor:   $ 9,533.33
```

El emisor entera al SAT los impuestos sobre el bruto ($10,000), no sobre lo cobrado neto.

### RESICO Persona Física (régimen 626 PF)
- No retención de IVA al receptor (pero sí emite IVA al 16%).
- Tasa ISR efectiva muy baja en pagos provisionales (1% a 2.5% sobre ingresos según rango).
- Si el receptor es PM, ESA PM **debe retener 1.25% de ISR sobre el monto del servicio** (regla específica RESICO PF).

### RESICO Persona Moral (régimen 626 PM)
- Tasa ISR efectiva sobre flujo (no devengado).
- Sin retenciones especiales por ser RESICO PM.

### Arrendamiento de inmueble (PF arrendadora → PM arrendataria)
- Retención ISR 10% (igual que servicios)
- Retención IVA 10.6667% (igual)
- Aplica cuando el PF tiene actividad de arrendamiento (régimen 606).

### Autotransporte terrestre de carga (PF → PM)
- Retención ISR 4% sobre el monto del servicio.
- Retención IVA 4% (4/16 partes del IVA).

### Honorarios médicos
- Si receptor es PF con uso D01: el receptor NO retiene (es deducción personal).
- Si receptor es PM: aplica retención profesional estándar (10% ISR + 10.6667% IVA).

### Comisiones mercantiles
- Si comisionista PF: retención 10% ISR + 10.6667% IVA (igual que servicios profesionales).

## Lo que hace este skill

Dado un escenario (emisor, receptor, tipo de operación, monto), devuelve:

```json
{
  "subtotal": 10000.00,
  "impuestos_trasladados": [
    {"tipo": "IVA", "tasa_factor": "Tasa", "tasa": 0.16, "importe": 1600.00}
  ],
  "impuestos_retenidos": [
    {"tipo": "ISR", "tasa": 0.10, "importe": 1000.00, "razon": "Servicios profesionales PF → PM"},
    {"tipo": "IVA", "tasa": 0.106667, "importe": 1066.67, "razon": "Retención IVA 2/3 partes servicios profesionales"}
  ],
  "total_comprobante": 10600.00,
  "neto_a_pagar_emisor": 9533.33,
  "alertas": [
    "El emisor entera al SAT sobre el bruto. Las retenciones las paga el receptor."
  ]
}
```

## Reglas de oro

1. **Las retenciones no reducen el Total del CFDI** — el CFDI tiene Subtotal + IVA = Total. Las retenciones se desglosan en nodo `Impuestos > Retenciones` y se restan al momento del pago efectivo al emisor.

2. **Las retenciones se calculan sobre el bruto, no sobre el IVA o sobre el neto** — error muy común que invalida CFDIs.

3. **No retiene quien quiere — retiene quien la ley obliga**. Una PM no puede "decidir no retener" a su proveedor PFAE. El SAT puede multar al receptor por no retener.

4. **Verificar región fronteriza**: solo aplican IVA 8% los contribuyentes con domicilio en la región fronteriza norte o sur según el decreto vigente. No es opcional ni se aplica por geografía del cliente.

## Casos edge

- **Emisor PF que también factura por sueldos y salarios (605)**: NO retenciones de IVA porque sueldos no causan IVA. ISR ya fue retenido en nómina, no se retiene de nuevo.
- **Operación con extranjero residente**: si hay retención por servicios independientes de extranjero residente en el extranjero, aplica artículo 156 LISR (retención 25% sobre el monto). Ver con cuidado tratados para evitar doble tributación.
- **Mixto**: si una factura mezcla productos (sin retención) y servicios profesionales (con retención), se prorratea por conceptos. El skill debe identificar qué conceptos llevan retención y aplicar solo a esos.

## Integración con `cfdi-emision`

Este skill alimenta el nodo `Impuestos` del payload que pasa a `cfdi-emision`. No emite CFDI por sí solo — calcula los importes y devuelve la estructura lista.

## Referencias

- LISR Título IV (Personas Físicas) — capítulos de actividad empresarial y profesional, arrendamiento, honorarios.
- LIVA Art. 1-A — supuestos de retención.
- Decreto región fronteriza norte (vigente desde 2019, prorrogado) — listado de municipios.
- Resolución Miscelánea Fiscal anual — tasas RESICO actualizadas.

*(Catálogo detallado de tasas por escenario pendiente en `references/matriz-retenciones.md`).*
