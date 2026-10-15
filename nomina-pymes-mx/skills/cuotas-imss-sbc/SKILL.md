---
name: cuotas-imss-sbc
description: Calcula cuotas IMSS obrero-patronales 2026 por empleado a partir de su SBC (Salario Base de Cotización), con tope de 25 UMA, cuota fija sobre UMA, excedente de 3 UMA y la cuota patronal progresiva de cesantía y vejez 2026 (reforma de pensiones 2020, sube cada año hasta 2030). Cubre enfermedades y maternidad, invalidez y vida, riesgos de trabajo, guarderías, retiro y CEAV, más la aportación INFONAVIT del 5%. Usar cuando el usuario diga cuotas IMSS, calcular SBC, ramos IMSS, cuota patronal IMSS, cuotas obrero patronales 2026, cesantía y vejez 2026, costo IMSS de un empleado.
allowed-tools: Read, Write
---

# Cuotas IMSS obrero-patronales 2026

## Parámetros 2026

Datos para cálculo: `nomina-pymes-mx/references/cuotas-imss-2026.json` (ramos, prima media RT por clase y `cesantia_y_vejez.tabla_patron_2026`).

- UMA diaria: **$117.31** desde 01-02-2026 (enero 2026 usa $113.14).
- SBC mínimo: salario mínimo 2026 ($315.04 general / $440.87 ZLFN). SBC máximo: **25 UMA = $2,932.75** diarios (Art. 28 LSS).
- Fuente de porcentajes: LSS (Arts. 25, 71-74, 106, 107, 147, 168, 211) y transitorio del decreto DOF 16-12-2020; tabla CEAV 2026 cotejada en IDC (09-02-2026) y El Contribuyente (confianza media-alta: fuente secundaria coincidente).

## Ramos y tasas

| Ramo | Base | Patrón | Trabajador |
|---|---|---|---|
| EyM cuota fija (Art. 106-I) | UMA × días | 20.40% | — |
| EyM excedente de 3 UMA (Art. 106-II) | (SBC − 3 UMA) × días | 1.10% | 0.40% |
| EyM prestaciones en dinero (Art. 107) | SBC | 0.70% | 0.25% |
| EyM gastos médicos pensionados (Art. 25) | SBC | 1.05% | 0.375% |
| Invalidez y vida (Art. 147) | SBC | 1.75% | 0.625% |
| Riesgos de trabajo (Arts. 71-74) | SBC | prima de la empresa | — |
| Guarderías y prestaciones sociales (Art. 211) | SBC | 1.00% | — |
| Retiro (Art. 168-I) | SBC | 2.00% | — |
| Cesantía y vejez (Art. 168-II) | SBC | tabla 2026 (abajo) | 1.125% |
| INFONAVIT (Art. 29 LINFONAVIT) | SBC (tope 25 UMA) | 5.00% | — |

### CEAV patronal 2026 (por SBC en veces UMA)

| SBC | 2026 |
|---|---|
| 1.00 SM | 3.150% |
| 1.01 SM a 1.50 UMA | 3.676% |
| 1.51 a 2.00 UMA | 4.851% |
| 2.01 a 2.50 UMA | 5.556% |
| 2.51 a 3.00 UMA | 6.026% |
| 3.01 a 3.50 UMA | 6.361% |
| 3.51 a 4.00 UMA | 6.613% |
| 4.01 UMA en adelante | 7.513% |

Sube cada 1 de enero hasta 2030 (rango 4.01+ llega a 11.875%). Revisa la tabla cada enero. El IMSS no ha emitido criterio oficial de cómo ubicar el rango; el SUA (v3.6.3+) divide SBC ÷ UMA.

### Riesgos de trabajo

Empresas que se inscriben por primera vez pagan la **prima media de su clase** (Art. 73 LSS): I 0.54355%, II 1.13065%, III 2.59840%, IV 4.65325%, V 7.58875%. Después, la prima se recalcula cada año por siniestralidad (Art. 74; mínimo 0.5%, máximo 15%), se declara en febrero y rige de marzo a febrero.

## Algoritmo

```python
from decimal import Decimal as D
UMA = D("117.31")

def cuotas_imss_mes(sbc: D, dias: int, prima_rt: D, ceav_patron: D) -> dict:
    sbc = min(sbc, 25 * UMA)
    base = sbc * dias
    exc = max(D(0), sbc - 3 * UMA) * dias
    patron = {
        "eym_fija": UMA * dias * D("0.204"), "eym_exc": exc * D("0.011"),
        "eym_dinero": base * D("0.007"), "eym_gmp": base * D("0.0105"),
        "iv": base * D("0.0175"), "rt": base * prima_rt, "guarderias": base * D("0.01"),
        "retiro": base * D("0.02"), "ceav": base * ceav_patron,
    }
    obrero = {
        "eym_exc": exc * D("0.004"), "eym_dinero": base * D("0.0025"),
        "eym_gmp": base * D("0.00375"), "iv": base * D("0.00625"), "ceav": base * D("0.01125"),
    }
    return {"patron": patron, "obrero": obrero, "infonavit_patron": base * D("0.05")}
```

Retiro, CEAV e INFONAVIT se pagan **bimestralmente**; los demás ramos, **mensualmente** (día 17 del mes siguiente, Art. 39 LSS).

## Ejemplo recalculado

Salario diario $600, factor de integración 1.0493 (año 1) → SBC **$629.58**; 30 días; clase I (0.54355%); SBC/UMA = 5.37 → CEAV 7.513%.

| Concepto | Patrón | Obrero |
|---|---|---|
| EyM fija | 717.94 | — |
| EyM excedente | 91.62 | 33.32 |
| EyM dinero | 132.21 | 47.22 |
| EyM GMP | 198.32 | 70.83 |
| IV | 330.53 | 118.05 |
| RT | 102.66 | — |
| Guarderías | 188.87 | — |
| Retiro | 377.75 | — |
| CEAV | 1,419.01 | 212.48 |
| **Total IMSS** | **3,558.92** | **481.89** |
| INFONAVIT 5% | 944.37 | — |

```json
{
  "empleado_id_hash": "...",
  "sbc_diario_mxn": "629.58",
  "dias_cotizados_mes": 30,
  "prima_rt": 0.0054355,
  "ceav_patron_pct": 0.07513,
  "cuotas_obreras_total_mxn": "481.89",
  "cuotas_patronales_total_mxn": "3558.92",
  "infonavit_patronal_mxn": "944.37",
  "costo_total_mes_empleador": "4503.29",
  "vigencia_validada": true
}
```

## ⚠ Validación

- Los montos oficiales son los que calcula el SUA o la emisión del IMSS (EMA/EBA); usa este cálculo para estimar y conciliar.
- Si el MCP `mp_imss_patronal` está disponible (`imss_simulador_costo_patronal`, `imss_sbc_calcular`), su estado es "sin verificar": contrasta con este cálculo.
- Pagar de menos genera cédula de diferencias, actualización, recargos y multa (Art. 304 LSS). Valida con tu contador.
