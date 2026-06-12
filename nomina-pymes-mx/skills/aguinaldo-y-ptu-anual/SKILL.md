---
name: aguinaldo-y-ptu-anual
description: Calcula aguinaldo (mínimo 15 días Art. 87 LFT) y PTU (10% utilidad fiscal Art. 117 LFT) por empleado. Aguinaldo vence 20 diciembre, PTU dentro de 60 días post declaración anual PM. Genera CFDI Nómina extraordinario con concepto correcto. Usar cuando el usuario diga aguinaldo, prima navideña, PTU, reparto utilidades.
allowed-tools: Read, Write
---

# Aguinaldo + PTU anual

## Aguinaldo (Art. 87 LFT)

### Reglas
- **Mínimo 15 días** de salario por año laborado
- Empresas grandes suelen pagar 20-30 días (CCT)
- Vence **20 diciembre** del año
- Proporcional si menos de 1 año laborado

### Cálculo

```python
def calcular_aguinaldo(sueldo_diario: Decimal, dias_laborados_año: int,
                       dias_minimo_lft: int = 15) -> Decimal:
    return (sueldo_diario * dias_minimo_lft * dias_laborados_año) / 365
```

### Exención fiscal

Hasta 30 UMAs exentas del ISR (Art. 93 fr. XIV LISR). Excedente paga ISR.

## PTU — Participación Trabajadores Utilidades (Art. 117 LFT)

### Reglas
- **10% utilidad fiscal del patrón** del año anterior
- Se reparte entre TODOS los trabajadores activos
- 50% por días laborados + 50% por sueldo (capado a 3 meses salario máximo del CCT o promedio)
- Plazo de pago: **dentro de 60 días post declaración anual PM** (típico mayo-junio del año siguiente)

### Quién NO recibe PTU
- Directores generales / gerentes generales (puede haber tope)
- Profesionistas en honorarios (no son trabajadores)
- Familiares directos del dueño (en PF)

### Exención fiscal
Hasta 15 UMAs exentas del ISR.

## Output

```json
{
  "ejercicio": 2026,
  "concepto": "aguinaldo",
  "empleado_id_hash": "...",
  "dias_laborados_año": 320,
  "dias_aguinaldo_aplicables": 15,
  "sueldo_diario_mxn": "627.12",
  "aguinaldo_bruto_mxn": "8246.32",
  "exencion_uma": "3394.20",
  "aguinaldo_gravable_mxn": "4852.12",
  "isr_a_retener_mxn": "1138.50",
  "aguinaldo_neto_pago_mxn": "7107.82",
  "deadline_pago": "2026-12-20",
  "cfdi_nomina_extraordinario_pendiente": true,
  "vigencia_validada": false
}
```

## ⚠ Errar = multa STPS

- Aguinaldo no pagado: multa 50-2,500 UMAs
- PTU no repartido: STPS investiga + multa
