---
name: validador-requisitos-deducibilidad-colegiaturas
description: Valida que un CFDI de colegiatura emitido por la escuela cumpla TODOS los requisitos para ser deducible para el papá/mamá del alumno: complemento IEDU, uso D10, RVOE vigente, datos del alumno + CURP + nivel, forma pago no efectivo. Si falta algo, el padre NO podrá deducir. Usar cuando el usuario diga validar cfdi colegiatura, deducible, complemento IEDU.
allowed-tools: Read, Write
---

# Validador CFDI colegiaturas deducibilidad

## Checklist obligatorio

1. **CFDI tipo I uso D10** (Pagos servicios educativos)
2. **Complemento IEDU** presente con:
   - Nombre del alumno
   - CURP del alumno
   - Nivel educativo (preescolar, primaria, secundaria, bachillerato)
   - Clave RVOE de la escuela vigente
3. **Forma de pago**: 02 (cheque), 03 (transferencia), 04/28 (tarjeta) — NO efectivo (01)
4. **RFC receptor**: padre/madre, no del alumno
5. **Concepto**: incluye palabra "colegiatura" o equivalente
6. **Periodo**: corresponde al ejercicio fiscal a deducir

## Output

```json
{
  "uuid_cfdi": "abc-123",
  "escuela_rfc": "...",
  "tipo": "I",
  "uso_cfdi": "D10",
  "validaciones": {
    "tiene_complemento_iedu": true,
    "rvoe_escuela_vigente": true,
    "nivel_educativo": "primaria",
    "tope_anual_aplicable_mxn": "12900.00",
    "forma_pago_no_efectivo": true,
    "rfc_receptor_correcto": true
  },
  "es_deducible": true,
  "monto_deducible_mxn": "10500.00",
  "advertencias": []
}
```

## Casos edge

- Inscripción (cuota inicial): NO deducible — solo colegiaturas mensuales
- Cursos extras (música, deportes): NO deducible
- Útiles escolares: NO deducible
- Transporte escolar: deducible si es OBLIGATORIO por la escuela
