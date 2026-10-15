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
| **8%** | Región Fronteriza Norte y Sur: estímulo (crédito del 50% del IVA), no tasa de ley. Decreto DOF 31-dic-2025 lo prorroga **solo hasta el 31-dic-2026**; requiere aviso/padrón de beneficiarios del SAT y domicilio del emisor en la región |
| **0%** | Art. 2-A LIVA: exportación de bienes/servicios (Art. 29), animales y vegetales no industrializados, alimentos (salvo excepciones), medicinas de patente, agua para uso doméstico, libros/periódicos/revistas, etc. |
| **Exento** | Servicios médicos profesionales (NO incluye hospitales), enseñanza pública y de particulares con RVOE (Art. 15 fr. IV LIVA), intereses bancarios a PF, etc. |

Diferencia crítica entre 0% y exento:
- **Tasa 0%** sí genera IVA acreditable para quien lo paga (aunque sea cero). El emisor sí desglosa el impuesto en el CFDI con valor 0.00.
- **Exento** no genera IVA acreditable. En el CFDI se marca con `TipoFactor = "Exento"` sin TasaOCuota.

## Retenciones de ISR e IVA — los casos más comunes

### Servicios profesionales PF → PM (el caso clásico de freelancer factura a empresa)
- Emisor: Persona Física régimen 612 (PFAE) o 605 (asimilados a salarios, distinto trato)
- Receptor: Persona Moral
- **Retención ISR**: 10% sobre el monto del servicio
- **Retención IVA**: 2/3 partes del IVA trasladado = 10.6667% **sobre el monto del servicio** (no sobre el IVA). TasaOCuota en CFDI: `0.106667`. Con IVA fronterizo 8%: 5.3333% (`0.053333`).

Ejemplo: servicio de $10,000 MXN
```
Subtotal:                  $10,000.00
IVA 16% trasladado:        $ 1,600.00
Retención ISR 10%:        −$ 1,000.00
Retención IVA 10.6667%:   −$ 1,066.67
                          ───────────
Total del CFDI:            $ 9,533.33   ← atributo Total (Anexo 20) = lo que cobra el emisor
```

El emisor acumula el ingreso por el bruto ($10,000); el receptor entera las retenciones al SAT.

### RESICO Persona Física (régimen 626 PF)
- Sí traslada IVA (16% u 8%): RESICO no cambia la Ley del IVA.
- ISR propio: 1.00% a 2.50% sobre ingresos cobrados según rango (Art. 113-E LISR).
- Si el receptor es PM, la PM **retiene 1.25% de ISR** (Art. 113-J LISR) **y también 2/3 del IVA** si es servicio profesional, arrendamiento o comisión (Art. 1-A fr. II a) LIVA). Error común: creer que RESICO elimina la retención de IVA.

### RESICO Persona Moral (régimen 626 PM)
- Tasa ISR efectiva sobre flujo (no devengado).
- Sin retenciones especiales por ser RESICO PM.

### Arrendamiento de inmueble (PF arrendadora → PM arrendataria)
- Retención ISR 10% (Art. 116 LISR)
- Retención IVA 10.6667% (2/3, Art. 1-A fr. II a) LIVA)
- Aplica cuando el PF tiene actividad de arrendamiento (régimen 606). Casa habitación: IVA exento (Art. 20 fr. II LIVA), sin retención de IVA.

### Autotransporte terrestre de bienes (→ PM)
- Retención IVA 4% del valor del servicio (Art. 1-A fr. II c) LIVA, Art. 3 fr. II RLIVA). Aplica aunque el transportista sea PF **o PM**.
- Retención ISR: la LISR no la prevé para transportista PF 612. Si el transportista es RESICO PF: 1.25% (Art. 113-J).

### Honorarios médicos
- Servicio médico de PF con título: IVA exento (Art. 15 fr. XIV LIVA) → no hay IVA que retener.
- Si receptor es PF con uso D01: el receptor NO retiene (es deducción personal).
- Si receptor es PM: solo retención ISR 10% (Art. 106 LISR); **no** retención de IVA.

### Comisiones mercantiles
- Si comisionista PF → PM: retención IVA 2/3 (Art. 1-A fr. II a) LIVA). ISR: el Art. 106 LISR solo obliga a retener por servicios profesionales; la comisión mercantil es actividad empresarial → sin retención de ISR salvo que el comisionista sea RESICO PF (1.25%).

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
  "total_comprobante": 9533.33,
  "neto_a_pagar_emisor": 9533.33,
  "alertas": [
    "El receptor entera las retenciones al SAT; el emisor acumula el ingreso bruto."
  ]
}
```

Script determinista: `python3 scripts/calcular_iva_retenciones.py --json --emisor 612 --receptor 601 --monto 10000`.

## Reglas de oro

1. **Las retenciones SÍ reducen el Total del CFDI.** Anexo 20 CFDI 4.0, atributo `Total` = SubTotal − Descuento + impuestos trasladados − impuestos retenidos. Un CFDI con Total = SubTotal + IVA y retenciones desglosadas es rechazado por el PAC.

2. **Las retenciones se calculan sobre el monto del concepto (base), no sobre el IVA ni sobre el neto.** Importe = Base × TasaOCuota redondeado a 2 decimales (el Anexo 20 tolera ±1 centavo por redondeo; nunca agregar un concepto "redondeo").

3. **No retiene quien quiere — retiene quien la ley obliga**. Una PM no puede "decidir no retener" a su proveedor PFAE. El SAT puede multar al receptor por no retener.

4. **Verificar región fronteriza**: solo aplican IVA 8% los contribuyentes inscritos en el padrón de beneficiarios del decreto, con domicilio en la región fronteriza norte o sur, y para operaciones entregadas/prestadas en esa región. No se aplica por geografía del cliente. La retención 2/3 baja a 5.3333%.

## Casos edge

- **Sueldos y salarios / asimilados (605)**: no son servicio independiente, no causan IVA ni se facturan con CFDI de Ingreso; van en CFDI de Nómina con retención ISR por tarifa (Art. 96 LISR).
- **Operación con extranjero residente**: si hay retención por servicios independientes de extranjero residente en el extranjero, aplica artículo 156 LISR (retención 25% sobre el monto). Ver con cuidado tratados para evitar doble tributación.
- **Mixto**: si una factura mezcla productos (sin retención) y servicios profesionales (con retención), se prorratea por conceptos. El skill debe identificar qué conceptos llevan retención y aplicar solo a esos.

## Integración con `cfdi-emision`

Este skill alimenta el nodo `Impuestos` del payload que pasa a `cfdi-emision`. No emite CFDI por sí solo — calcula los importes y devuelve la estructura lista.

## Referencias

- LISR Título IV (Personas Físicas) — capítulos de actividad empresarial y profesional, arrendamiento, honorarios.
- LIVA Art. 1-A — supuestos de retención.
- Decretos de estímulos región fronteriza norte y sur (DOF 31-dic-2025, prórroga hasta 31-dic-2026) — listado de municipios.
- LISR Art. 113-E (tasas RESICO PF) y 113-J (retención 1.25%).
- Anexo 20 CFDI 4.0 (atributo `Total`, límites de redondeo de `Importe`).
- `references/matriz-retenciones.md` — escenarios por emisor × receptor × giro

## ⚠ Datos que requieren verificación vigente antes de producción

Revisado contra LISR, LIVA, RLIVA y Anexo 20 vigentes en oct-2026. **NO usar para declaraciones reales sin validar con fuente oficial vigente o contador certificado**:

1. **Tasas RESICO PF** (1.00%, 1.10%, 1.50%, 2.00%, 2.50% hasta $3.5M anuales): están en el Art. 113-E LISR (no en la RMF); cambian solo por reforma a la ley.

2. **Tasas RESICO PM**: tasa general 30% sobre flujo (Título VII Cap. XII LISR); este skill no las detalla.

3. **Retención REPSE 6% IVA** (Art. 1-A fr. IV LIVA): vigente desde 2021.

4. **Decreto región fronteriza norte y sur**: la prórroga actual vence el 31-dic-2026. Para 2027 verificar nuevo decreto en DOF.

5. **Retenciones tradicionales** (10% ISR + 10.6667% IVA para servicios profesionales PF→PM): Art. 106 LISR y Art. 1-A LIVA sin reforma en 2026.

6. **Autotransporte**: retención IVA 4% (Art. 1-A fr. II c) LIVA); sin retención ISR en LISR para PF 612.

7. **Tope efectivo deducibilidad** ($2,000 MXN): aplica para deducción de gastos en efectivo, confirmar vigente.

**Antes de exponer a cliente**: hacer cálculo de prueba en una declaración real y comparar contra el resultado del SAT vía portal.
