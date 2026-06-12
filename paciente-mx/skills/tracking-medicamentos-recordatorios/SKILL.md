---
name: tracking-medicamentos-recordatorios
description: Tracking de medicamentos crónicos del paciente con recordatorios automáticos (alarmas WhatsApp/notificación móvil), adherencia (% tomados vs prescritos), alertas reabastecimiento (cuando quedan < 5 días), interacciones básicas. Útil para pacientes crónicos + adultos mayores. Usar cuando el usuario diga mis medicamentos, recordatorios medicina, tomar pastilla.
allowed-tools: Read, Write
---

# Tracking medicamentos

## Schema medicamento

```python
class Medicamento(BaseModel):
    nombre_generico: str
    nombre_comercial: str | None
    dosis: str  # "50mg"
    via: Literal["oral", "topica", "inyectable", "inhalada"]
    frecuencia: str  # "1 c/24h", "1 c/12h", etc.
    horarios_recordatorio: list[time]
    indicado_por: str  # médico
    diagnostico_cie10: str
    stock_actual_dias: int
    medicamento_controlado: bool
```

## Adherencia

Por cada medicamento:
- Tomas registradas vs esperadas en N días
- % adherencia (objetivo: 90%+)
- Si < 80%: alerta al paciente + sugerir hablar con médico

## Output

```
💊 MIS MEDICAMENTOS

🟢 Tomado hoy (3/4):
  ✓ 07:00 - Losartán 50mg
  ✓ 08:00 - Metformina 850mg
  ✓ 19:00 - Metformina 850mg
  ⏰ 22:00 - Atorvastatina 20mg (pendiente)

📊 Adherencia últimos 30 días: 91% ✅

⚠ Reabastecimiento:
  • Atorvastatina: quedan 3 días — comprar AHORA
  • Losartán: quedan 12 días — comprar en 1 semana
```
