---
name: baja-empleado-imss
description: Baja de empleado del IMSS con aviso IDSE oportuno (5 días hábiles post última fecha laboral, Art. 37 LSS). Cubre cálculo de finiquito (partes proporcionales aguinaldo + vacaciones + prima vacacional pendiente) o liquidación si despido (90 días + 20 días por año + 12 días por año al SBC tope). Usar cuando el usuario diga baja empleado, despido, renuncia, terminacion laboral, finiquito.
allowed-tools: Read, Write
---

# Baja empleado IMSS

## Tipos de terminación

### A. Renuncia voluntaria
- **Finiquito**: partes proporcionales (aguinaldo + vacaciones + prima vacacional)
- NO indemnización
- Aviso IDSE: 5 días hábiles
- Carta renuncia firmada por trabajador (recomendado)

### B. Despido justificado (Art. 47 LFT)
- **Finiquito** sólo
- NO indemnización
- Documentar causal estrictamente (no llegar a tiempo NO es causal típica)
- Aviso IDSE: 5 días hábiles

### C. Despido injustificado / sin causa
- **Liquidación**: 3 meses (90 días) + 20 días por año laborado + finiquito
- Si > 1 año: prima de antigüedad = 12 días × SBC × años (al tope 2 UMAs)
- Aviso IDSE: 5 días hábiles
- Demanda probable del trabajador

### D. Mutuo acuerdo
- Lo que negocien (típico: liquidación pero menor a injustificado)
- Convenio firmado en STPS para protección del patrón

### E. Defunción
- Beneficiarios reciben finiquito + indemnización seguro de vida (si aplica)
- Trámites especiales IMSS

## Algoritmo finiquito

```python
def calcular_finiquito(empleado: Empleado, fecha_baja: date) -> dict:
    sueldo_diario = empleado.sueldo_diario_mxn
    dias_laborados_año_curso = (fecha_baja - inicio_año(fecha_baja)).days

    aguinaldo_proporcional = (sueldo_diario * 15 * dias_laborados_año_curso) / 365
    vacaciones_pendientes = empleado.dias_vacaciones_no_disfrutados * sueldo_diario
    prima_vacacional_25 = vacaciones_pendientes * Decimal("0.25")
    salarios_devengados = sueldo_diario * empleado.dias_pendientes_quincena

    return {
        "aguinaldo_proporcional": str(aguinaldo_proporcional),
        "vacaciones_pendientes": str(vacaciones_pendientes),
        "prima_vacacional": str(prima_vacacional_25),
        "salarios_devengados": str(salarios_devengados),
        "total_finiquito": str(sum([
            aguinaldo_proporcional, vacaciones_pendientes,
            prima_vacacional_25, salarios_devengados
        ]))
    }
```

## Output

```json
{
  "empleado_id_hash": "...",
  "fecha_baja": "2026-06-15",
  "tipo": "renuncia_voluntaria",
  "antiguedad_anos": 2.5,
  "finiquito_mxn": "32450.00",
  "indemnizacion_mxn": "0.00",
  "prima_antiguedad_mxn": "0.00",  // solo si > 1 año Y aplica
  "total_a_pagar_mxn": "32450.00",
  "aviso_idse_pendiente": true,
  "deadline_idse": "2026-06-22",
  "cfdi_nomina_finiquito_pendiente": true
}
```

## ⚠ Documentos obligatorios

- Carta renuncia firmada (caso A)
- Convenio STPS (caso D)
- Acta defunción (caso E)
- Recibo finiquito firmado por trabajador
- CFDI Nómina con concepto "Finiquito" o "Liquidación"
