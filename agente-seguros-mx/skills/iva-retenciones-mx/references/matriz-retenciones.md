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
| RESICO PF (626) | PM (601) | 16% | 1.25% | 10.6667% (2/3) | ISR reducido (Art. 113-J LISR); el IVA 2/3 se retiene igual (Art. 1-A LIVA) |
| RESICO PF (626) | PF | 16% | 0 | 0 | |
| RESICO PM (626) | PM (601) | 16% | 0 | 0 | RESICO PM no genera retención adicional |
| PM (601) | PM (601) | 16% | 0 | 0 | PM no retiene a PM por servicios |

## 2. Arrendamiento de inmueble

| Emisor (arrendador) | Receptor (arrendatario) | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF Régimen 606 | PM | 16% | 10% | 10.6667% | Igual que profesional, sobre la renta sin IVA |
| PF Régimen 606 | PF (uso casa habitación) | Exento | 0 | 0 | Vivienda exenta IVA |
| PF Régimen 606 | PF (uso comercial) | 16% | 0 | 0 | PF a PF sin retención |
| RESICO PF | PM | 16% | 1.25% | 10.6667% | Art. 113-J LISR + Art. 1-A fr. II a) LIVA |
| PM | PM | 16% | 0 | 0 | |

## 3. Servicios de autotransporte terrestre de carga

| Emisor | Receptor | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF transportista (612) | PM | 16% | 0 | 4% del valor | Art. 1-A fr. II c) LIVA; la LISR no prevé retención ISR |
| RESICO PF transportista | PM | 16% | 1.25% | 4% del valor | Art. 113-J LISR |
| PM transportista (coordinado 624) | PM | 16% | 0 | 4% del valor | La retención IVA 4% aplica también si el prestador es PM |
| PFAE | PF | 16% | 0 | 0 | |

## 4. Honorarios de salud (medicina, odontología, veterinaria, psicología, nutrición)

Art. 15 fr. XIV LIVA: exentos los servicios profesionales de medicina que requieran **título de médico** y los preste una **persona física**. El Art. 41 RLIVA incluye médicos, cirujanos dentistas y médicos veterinarios.

| Emisor | Receptor | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF médico, cirujano dentista o MVZ | PF (uso D01) | Exento | 0 | 0 | Exención Art. 15 fr. XIV LIVA |
| PF médico, cirujano dentista o MVZ | PM | Exento | 10% | 0 | ISR sí se retiene; IVA exento no se retiene |
| PF psicólogo o nutriólogo | PF | 16% | 0 | 0 | No requiere título de médico: no aplica la exención (confianza media; confirmar con contador) |
| PF psicólogo o nutriólogo | PM | 16% | 10% | 10.6667% | Honorarios: retención ISR 10% e IVA 2/3 |
| PM clínica/hospital | PF | 16% | 0 | 0 | Servicios hospitalarios sí causan IVA |
| PM clínica/hospital | PM | 16% | 0 | 0 | |

**Nota crítica**: la exención es para el profesional persona física con título de médico. Si el servicio lo presta una PM (clínica, hospital, S.A.), causa IVA al 16%.

## 5. Comisiones mercantiles

| Emisor (comisionista) | Receptor | IVA | Retención ISR | Retención IVA | Notas |
|---|---|---|---|---|---|
| PF (PFAE 612) | PM | 16% | 0 | 10.6667% | IVA 2/3 (Art. 1-A fr. II a) LIVA); Art. 106 LISR solo obliga a retener ISR por servicios profesionales |
| RESICO PF | PM | 16% | 1.25% | 10.6667% | |
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
| AC autorizada SAT | PF o PM | No objeto (no es tasa 0%) | 0 | El donativo no es acto gravado: ObjetoImp `01`, sin nodo IVA. UsoCFDI del donante D04. AC en listado de donatarias autorizadas |

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

1. **Las retenciones SÍ reducen el Total del CFDI.** Anexo 20: Total = SubTotal − Descuento + Trasladados − Retenidos. El cliente paga el Total y entera las retenciones al SAT.

2. **Solo retiene quien la ley obliga.** No es opcional. Una PM que omite retener a su proveedor PFAE puede ser multada.

3. **RESICO PF es 1.25% de ISR (no 10%), pero el IVA 2/3 se retiene igual.** Confirmar régimen antes de calcular.

4. **Verificar región fronteriza para IVA 8%.** Solo si el emisor está en el padrón del decreto vigente (prórroga hasta 31-dic-2026). La retención 2/3 baja a 5.3333%.

5. **Si la operación es a tasa 0%, el nodo IVA sí existe en el CFDI.** Con valor 0.00. No confundir con exento.

## Bibliografía

- LISR Art. 106 (servicios profesionales), 116 (arrendamiento), 113-J (RESICO PF 1.25%)
- LIVA Art. 1-A; RLIVA Art. 3 (2/3 y 4%)
- Anexo 20 CFDI 4.0 (atributo Total)
- Decretos región fronteriza norte y sur (DOF 31-dic-2025, hasta 31-dic-2026)
- Reforma subcontratación 2021 (REPSE)
