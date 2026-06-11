# Matriz de retenciones — escenarios por emisor × receptor × tipo de operación

Esta matriz cubre los escenarios más frecuentes. **Las retenciones se calculan sobre el monto del concepto (bruto), nunca sobre el IVA ni sobre el subtotal después de retenciones.**

## Convenciones
- `PF` = Persona Física
- `PM` = Persona Moral
- `RESICO PF` = Régimen 626 PF
- `RESICO PM` = Régimen 626 PM
- `PFAE` = Régimen 612 (Personas Físicas con Actividad Empresarial y Profesional)
- "Retención IVA 2/3" = 10.6667% sobre el monto del concepto (equivale a 2/3 partes del IVA al 16%)

## 1. Servicios profesionales (consultoría, diseño, programación, asesoría, etc.)

| Emisor | Receptor | IVA trasladado | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PFAE (612) | PM (601) | 16% | 10% | 10.6667% (2/3) | El clásico freelancer→empresa |
| PFAE (612) | PF | 16% | 0 | 0 | PF no retiene a PF |
| RESICO PF (626) | PM (601) | 16% | 1.25% | 0 | Régimen especial, retención reducida ISR |
| RESICO PF (626) | PF | 16% | 0 | 0 | |
| RESICO PM (626) | PM (601) | 16% | 0 | 0 | RESICO PM no genera retención adicional |
| PM (601) | PM (601) | 16% | 0 | 0 | PM no retiene a PM por servicios |

## 2. Arrendamiento de inmueble

| Emisor (arrendador) | Receptor (arrendatario) | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF Régimen 606 | PM | 16% | 10% | 10.6667% | Igual que profesional, sobre la renta sin IVA |
| PF Régimen 606 | PF (uso casa habitación) | Exento | 0 | 0 | Vivienda exenta IVA |
| PF Régimen 606 | PF (uso comercial) | 16% | 0 | 0 | PF a PF sin retención |
| RESICO PF | PM | 16% | 1.25% | 0 | |
| PM | PM | 16% | 0 | 0 | |

## 3. Servicios de autotransporte terrestre de carga

| Emisor | Receptor | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF transportista | PM | 16% | 4% | 4% (4/16 partes) | Régimen 612 |
| PM transportista (coordinado 624) | PM | 16% | 0 | 0 | Coordinados con régimen especial |
| PFAE | PF | 16% | 0 | 0 | |

## 4. Honorarios médicos profesionales (medicina, odontología, psicología, nutrición)

| Emisor | Receptor | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF médico profesional | PF (uso D01) | Exento | 0 | 0 | Servicios médicos PF son exentos de IVA |
| PF médico profesional | PM | Exento | 10% | 0 | ISR sí se retiene, IVA exento no se retiene |
| PM clínica/hospital | PF | 16% | 0 | 0 | Servicios hospitalarios sí causan IVA |
| PM clínica/hospital | PM | 16% | 0 | 0 | |

**Nota crítica**: solo el servicio del médico individual está exento. Si es a través de hospital/clínica como PM, causa IVA al 16%.

## 5. Comisiones mercantiles

| Emisor (comisionista) | Receptor | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF (PFAE 612) | PM | 16% | 10% | 10.6667% | Igual que servicios profesionales |
| RESICO PF | PM | 16% | 1.25% | 0 | |
| PM | PM | 16% | 0 | 0 | |

## 6. Servicios de outsourcing especializado (REPSE)

Desde la reforma de subcontratación (2021), los servicios especializados deben:
- Estar registrados en REPSE (Registro de Prestadoras de Servicios u Obras Especializadas)
- El receptor debe verificar el registro vigente

| Emisor (con REPSE) | Receptor | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PM con REPSE | PM | 16% | 0 | 6% del valor del servicio | Retención IVA 6% Art. 1-A Frac. IV LIVA |

Si el emisor NO tiene REPSE vigente: el receptor no puede acreditar el IVA ni deducir el ISR del gasto. Riesgo grande.

## 7. Donativos

| Emisor (donatario, AC autorizada) | Receptor (donante) | IVA | Retención | Notas |
|---|---|---|---|---|
| AC autorizada SAT | PF o PM | 0% (sin IVA) | 0 | UsoCFDI D04. AC debe estar en listado de donatarias autorizadas |

## 8. Operaciones a tasa 0% (exportación, alimentos básicos, medicinas patente, etc.)

| Emisor | Receptor | IVA | Retención | Notas |
|---|---|---|---|---|
| Cualquiera | Cualquiera | 0% | 0 | TipoFactor "Tasa", TasaOCuota "0.000000" |

El emisor sí acumula IVA acreditable de sus gastos. Diferencia con exento (no acumula).

## 9. Operaciones con extranjeros residentes en el extranjero

Si un freelancer/empresa mexicana presta servicios a una empresa extranjera **y el servicio se aprovecha en el extranjero**: exportación de servicios a tasa 0%.

Si un extranjero presta servicios a alguien en MX y los aprovecha en MX: retención por Art. 156 LISR (varía por tratado para evitar doble tributación).

## 10. Sueldos y Salarios (PF régimen 605)

No es CFDI tipo I sino tipo N (Nómina) con complemento Nómina 1.2. No causa IVA (es relación laboral, no servicio independiente). El patrón retiene ISR mensual según tarifa.

## Reglas de oro

1. **Las retenciones reducen el cobro al emisor, no el Total del CFDI.** El CFDI muestra Subtotal, IVA, Retenciones desglosadas, Total. El cliente paga Total − Retenciones; entera las retenciones al SAT directamente.

2. **Solo retiene quien la ley obliga.** No es opcional. Una PM que omite retener a su proveedor PFAE puede ser multada.

3. **RESICO PF es 1.25% (no 10%).** Error común aplicar la retención normal de 10% a un RESICO PF. Confirmar régimen antes de calcular.

4. **Verificar región fronteriza para IVA 8%.** Solo si el emisor tiene domicilio fiscal en municipios del decreto fronterizo vigente. No es por geografía del cliente.

5. **Si la operación es a tasa 0%, el nodo IVA sí existe en el CFDI.** Con valor 0.00. No confundir con exento.

## Bibliografía

- LISR Art. 106, 116, 142 (retenciones)
- LIVA Art. 1-A (supuestos de retención)
- Resolución Miscelánea Fiscal (tasas RESICO vigentes)
- Decreto región fronteriza norte y sur (vigente)
- Reforma subcontratación 2021 (REPSE)
