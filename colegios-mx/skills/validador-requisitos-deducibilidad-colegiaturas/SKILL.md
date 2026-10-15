---
name: validador-requisitos-deducibilidad-colegiaturas
description: Valida que un CFDI de colegiatura emitido por la escuela cumpla los requisitos para que el papá o la mamá aplique el estímulo por colegiaturas (Decreto DOF 26-12-2013, arts. 1.8 a 1.10): complemento concepto IEDU con nombre y CURP del alumno, nivel educativo y CCT/RVOE; UsoCFDI D10; forma de pago no efectivo; colegiatura separada de inscripción y otras cuotas; tope anual por nivel. Si falta algo, el padre NO podrá deducir. Usar cuando el usuario diga validar CFDI colegiatura, ¿es deducible mi colegiatura?, revisar factura del colegio, complemento IEDU, D10.
allowed-tools: Read, Write
---

# Validador de CFDI de colegiaturas

## Checklist obligatorio

1. **CFDI tipo I con UsoCFDI D10** (Pagos por servicios educativos).
2. **Complemento IEDU** (`iedu:instEducativas` v1.0) dentro del concepto de colegiatura, con:
   - `nombreAlumno`
   - `CURP` del alumno
   - `nivelEducativo`: Preescolar, Primaria, Secundaria, Profesional técnico o Bachillerato o su equivalente
   - `autRVOE`: CCT o RVOE de la escuela (verificar que esté vigente para ese nivel)
3. **Forma de pago**: 02 cheque nominativo, 03 transferencia, 04/28/29 tarjeta — NO 01 efectivo.
4. **RFC receptor**: el padre, madre o tutor que paga, no el alumno.
5. **Concepto**: colegiatura identificada y separada de inscripción, reinscripción, materiales u otras cuotas (esas no son deducibles).
6. **Periodo**: pagado en el ejercicio que se declara.
7. **Beneficiario**: el alumno es el contribuyente, su cónyuge/concubino o un ascendiente/descendiente en línea recta sin ingresos ≥ 1 UMA anual ($42,818.15 en 2026).

## Tope anual por alumno

Preescolar $14,200 · Primaria $12,900 · Secundaria $19,900 · Profesional técnico $17,100 · Bachillerato $24,500. El monto deducible es el menor entre lo pagado en el año y el tope.

## Output

```json
{
  "uuid_cfdi": "abc-123",
  "escuela_rfc": "...",
  "tipo": "I",
  "uso_cfdi": "D10",
  "validaciones": {
    "tiene_complemento_iedu": true,
    "complemento_en_concepto": true,
    "rvoe_escuela_vigente": true,
    "nivel_educativo": "Primaria",
    "tope_anual_aplicable_mxn": "12900.00",
    "forma_pago_no_efectivo": true,
    "rfc_receptor_correcto": true,
    "conceptos_no_deducibles_separados": true
  },
  "es_deducible": true,
  "pagado_en_ejercicio_mxn": "10500.00",
  "monto_deducible_mxn": "10500.00",
  "advertencias": []
}
```

Con $10,500 pagados en primaria el deducible es $10,500 (menor que el tope de $12,900).

## Casos edge

- Inscripción o reinscripción: NO deducible.
- Cursos extra (música, deportes), útiles, uniformes: NO deducibles.
- Transporte escolar: no entra en este estímulo; es deducible por Art. 151 fr. VII LISR solo si es obligatorio, y debe venir separado en el CFDI.
- Universidad: no deducible.

> Orientación general; la deducción la confirma el contador del contribuyente.
