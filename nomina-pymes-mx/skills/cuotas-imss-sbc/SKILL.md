---
name: cuotas-imss-sbc
description: Calcula cuotas IMSS obrero-patronales por empleado en base a su SBC (Salario Base de Cotización). Cubre los 5 ramos: enfermedades y maternidad, invalidez y vida, riesgos de trabajo, guarderías, retiro+cesantía+vejez. Suma cuotas obreras (retenidas al trabajador) + cuotas patronales (gasto del patrón). Usar cuando el usuario diga cuotas IMSS, calcular SBC, ramos IMSS, patronal IMSS.
allowed-tools: Read, Write
---

# Cuotas IMSS obrero-patronales

## Ramos (Art. 11 LSS)

| Ramo | Cuota obrero | Cuota patrón | Notas |
|---|---|---|---|
| Enfermedades y maternidad — especie | 0.25% SBC | 20.4% SBC fijo + 1.10% excedente UMA | Más complejo |
| Enfermedades y maternidad — dinero | 0.25% SBC | 0.70% SBC | |
| Invalidez y vida | 0.625% SBC | 1.75% SBC | |
| Riesgos de trabajo | 0% | 0.50% - 7.58% según clase | Varía por industria |
| Guarderías y prestaciones sociales | 0% | 1.00% SBC | |
| Retiro | 0% | 2.00% SBC | A AFORE trabajador |
| Cesantía y vejez | 1.125% SBC | 3.15% SBC | A AFORE trabajador |
| **INFONAVIT** | 0% | 5.00% SBC | Aparte de IMSS |

## Clases riesgo trabajo

| Clase | Pct patrón |
|---|---|
| I (oficina) | 0.50% |
| II | 1.13% |
| III | 2.59% |
| IV (construcción) | 4.65% |
| V (alto riesgo: minería, química) | 7.58% |

## Algoritmo

```python
def calcular_cuotas_imss_mes(sbc_diario: Decimal, dias_cotizados: int, clase_riesgo: int) -> dict:
    sbc_mensual = sbc_diario * dias_cotizados

    # Ramos cuotas fijas (no dependen excedente UMA)
    cuotas = {
        "enfermedades_dinero_obrero": sbc_mensual * Decimal("0.0025"),
        "enfermedades_dinero_patron": sbc_mensual * Decimal("0.0070"),
        "invalidez_y_vida_obrero": sbc_mensual * Decimal("0.00625"),
        "invalidez_y_vida_patron": sbc_mensual * Decimal("0.01750"),
        "riesgos_trabajo_patron": sbc_mensual * RIESGO_CLASE[clase_riesgo],
        "guarderias_patron": sbc_mensual * Decimal("0.0100"),
        "retiro_patron": sbc_mensual * Decimal("0.0200"),
        "cesantia_obrero": sbc_mensual * Decimal("0.01125"),
        "cesantia_patron": sbc_mensual * Decimal("0.03150"),
        "infonavit_patron": sbc_mensual * Decimal("0.0500"),
    }

    # Enfermedades especie es más complejo (excedente UMA)
    uma_diario = Decimal("113.14")
    cuota_fija_especie = uma_diario * dias_cotizados * Decimal("0.2040")
    excedente = max(0, sbc_mensual - (3 * uma_diario * dias_cotizados))
    cuotas["enfermedades_especie_patron"] = cuota_fija_especie + (excedente * Decimal("0.0110"))

    return {
        "cuotas_obreras_total_mxn": str(sum([v for k, v in cuotas.items() if "obrero" in k])),
        "cuotas_patronales_total_mxn": str(sum([v for k, v in cuotas.items() if "patron" in k])),
        "desglose": {k: str(v) for k, v in cuotas.items()},
        "vigencia_validada": False
    }
```

## Output

```json
{
  "empleado_id_hash": "...",
  "sbc_diario_mxn": "627.12",
  "dias_cotizados_mes": 30,
  "clase_riesgo": 1,
  "cuotas_obreras_total_mxn": "656.55",
  "cuotas_patronales_total_mxn": "2876.30",
  "infonavit_patronal_mxn": "940.68",
  "costo_total_mes_empleador": "3816.98",
  "vigencia_validada": false
}
```

## ⚠ Cuotas cambian anualmente

- UMA actualizada cada febrero (INEGI)
- Cuotas IMSS publicadas DOF enero
- Validar contra LSS vigente
