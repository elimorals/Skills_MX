---
name: estudios-laboratorios
description: Tracking de estudios de laboratorio (química sanguínea, biometría hemática, electrocardiograma, imagenología) con resultados, valores de referencia, comparativa histórica, y alertas si valores fuera de rango. Permite llevar resultados a la próxima cita. Usar cuando el usuario diga mis estudios, resultados laboratorio, glucosa colesterol.
allowed-tools: Read, Write
---

# Estudios laboratorios

## Schema estudio

```python
class EstudioLaboratorio(BaseModel):
    tipo: str  # "quimica_sanguinea_27_elementos"
    fecha: date
    laboratorio: str  # "Salud Digna", "Chopo", "Médica Sur"
    pdf_path: str
    valores: dict[str, ValorEstudio]
    medicamentos_al_momento: list[str]
```

```python
class ValorEstudio(BaseModel):
    parametro: str  # "Glucosa", "Colesterol_total"
    valor: float
    unidad: str
    rango_normal_min: float
    rango_normal_max: float
    interpretacion: Literal["normal", "ligeramente_alto", "alto", "muy_alto", "bajo"]
```

## Output

```
🔬 MIS ESTUDIOS

Último (2026-06-08, Salud Digna):
  Glucosa:        118 mg/dL  [70-100]  ⚠ ligeramente alto
  HbA1c:          7.2%        [<6.5]   ⚠ alto
  Colesterol T:   210 mg/dL   [<200]   ⚠ ligeramente alto
  Triglicéridos:  165 mg/dL   [<150]   ⚠ alto
  Creatinina:     0.9 mg/dL   [0.7-1.3] ✓

📈 Comparativa últimos 12 meses:
  HbA1c: 6.8 → 7.0 → 7.2 (TENDENCIA AL ALZA - revisar tratamiento)

🎯 Para próxima cita endocrinología:
  • Llevar últimos 3 estudios
  • Mencionar tendencia al alza HbA1c
```

## Alertas automáticas

Si parámetro crítico fuera de rango: alerta + sugerir consulta médica.
