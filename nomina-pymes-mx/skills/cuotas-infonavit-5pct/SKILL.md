---
name: cuotas-infonavit-5pct
description: Aportación patronal INFONAVIT del 5% sobre SBC más descuento al empleado si tiene crédito INFONAVIT vigente. Cobertura del crédito puede ser % del SBC, monto fijo, o salarios mínimos. Útil para empleados con crédito habitacional. Usar cuando el usuario diga INFONAVIT, credito vivienda empleado, descuento INFONAVIT.
allowed-tools: Read, Write
---

# Cuotas INFONAVIT

## Aportación patronal (siempre)

5% sobre SBC mensual — bimestral al INFONAVIT vía SUA.

## Descuento al empleado (si tiene crédito)

3 modalidades posibles:

| Modalidad | Cálculo |
|---|---|
| % SBC | X% del SBC mensual (más común, 25-30%) |
| Cuota fija | Monto MXN fijo mensual |
| Veces SMG | N × Salario Mínimo General mensual |

INFONAVIT informa al patrón vía EMIS (Emisión Mensual) qué descontar a cada trabajador.

## Output

```json
{
  "empleado_id_hash": "...",
  "sbc_mensual_mxn": "18813.60",
  "aportacion_patronal_5pct_mxn": "940.68",
  "tiene_credito_activo": true,
  "modalidad_descuento": "pct_sbc",
  "porcentaje_descuento": 0.27,
  "descuento_mensual_mxn": "5079.67",
  "saldo_credito_pendiente_mxn": "485000.00",
  "vigencia_validada": false
}
```

## Compliance

- EMIS bimestral obligatoria
- Descuento al empleado se aplica en CFDI Nómina con clave específica
- Errar = capital constitutivo INFONAVIT
