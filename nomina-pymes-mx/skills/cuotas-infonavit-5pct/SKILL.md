---
name: cuotas-infonavit-5pct
description: Calcula la aportación patronal INFONAVIT del 5% sobre el SBC (tope 25 UMA, pago bimestral vía SUA) y el descuento al trabajador con crédito INFONAVIT vigente según el aviso de retención (porcentaje, cuota fija o factor en VSM/UMI). Útil para empleados con crédito de vivienda. Usar cuando el usuario diga INFONAVIT, aportación INFONAVIT, crédito vivienda empleado, descuento INFONAVIT, aviso de retención, amortización INFONAVIT, EMIS.
allowed-tools: Read, Write
---

# Cuotas INFONAVIT

## Aportación patronal (siempre)

- **5% del SBC** (Art. 29 fr. II Ley INFONAVIT), con tope de **25 UMA** ($2,932.75 diarios en 2026).
- Se paga **bimestral** (día 17 del mes siguiente al bimestre) junto con retiro y CEAV, en el SUA.
- No se descuenta al trabajador.

## Descuento al trabajador (solo con crédito vigente)

El INFONAVIT envía al patrón el **Aviso para retención de descuentos**; el patrón debe aplicarlo a partir del día siguiente de recibirlo. El tipo de descuento sale de ese aviso, no se elige:

| Tipo | Cálculo |
|---|---|
| Porcentaje | % indicado × SBC del periodo |
| Cuota fija | Monto fijo mensual en pesos |
| Factor de descuento | Factor × VSM o UMI (créditos en veces salario mínimo; el factor y el valor de referencia vienen en el aviso) |

Más el seguro de daños de la vivienda cuando el aviso lo indique.
La EMIS (Emisión Mensual Anticipada) del INFONAVIT sirve para conciliar qué descuentos espera el Instituto.
Si el trabajador deja la empresa, presenta el aviso de baja del crédito (suspensión) junto con la baja en el IMSS.

## Output

```json
{
  "empleado_id_hash": "...",
  "sbc_diario_mxn": "629.58",
  "dias_bimestre": 61,
  "aportacion_patronal_5pct_bimestre_mxn": "1920.22",
  "tiene_credito_activo": true,
  "tipo_descuento": "porcentaje",
  "porcentaje_descuento": 0.20,
  "descuento_bimestre_mxn": "7680.88",
  "fuente_descuento": "aviso de retención INFONAVIT",
  "vigencia_validada": false
}
```

Cálculo: 629.58 × 61 = 38,404.38; × 5% = 1,920.22; × 20% = 7,680.88.

## Compliance

- No aplicar o aplicar mal el descuento hace al patrón responsable solidario del monto no retenido, más actualización y recargos.
- Si `mp_infonavit_patronal` está disponible (`infonavit_consultar_creditos_trabajadores`, `infonavit_descargar_emis`, `infonavit_conciliacion_nomina`), su estado es "sin verificar": confirma contra el portal empresarial.
- Reforma a la Ley INFONAVIT (DOF 21-02-2025): no cambió el 5% patronal; revisa reglas nuevas de crédito en el portal del Instituto (verificar).
- Valida con tu contador antes de presentar el SUA.
