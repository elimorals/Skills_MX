---
name: dashboard-consultas-telemedicina
description: Dashboard semanal/mensual del médico que hace consultas remotas. Reporta consultas realizadas vs canceladas vs no-show, ingresos brutos, pacientes nuevos vs seguimiento, retención, top diagnósticos. Diferencia de consultorio presencial es que la franja horaria puede ser más amplia (24/7 si el médico quiere). Usar cuando el usuario diga dashboard telemedicina, status consultas remotas, como va mi mes online.
allowed-tools: Read, Write
---

# Dashboard telemedicina

## Output

```
🌐 TELEMEDICINA — Semana 24-2026

📊 Actividad:
  Consultas programadas:   42
  Realizadas:              35 (83%)
  Canceladas:               5
  No-show:                  2

👥 Pacientes:
  Únicos atendidos:        32
  Primera vez:             10 (31%)
  Seguimiento:             22

💰 Ingresos:
  Bruto:                $52,500 MXN
  Cobrado pre-consulta: $48,000 (91% pre-pago)

🩺 Top diagnósticos:
  1. I10 Hipertensión (8)
  2. F32.1 Episodio depresivo moderado (6)
  3. K58 SII (4)

📍 Distribución geográfica pacientes:
  CDMX: 60% | Guadalajara: 18% | Monterrey: 12% | Otros: 10%

⚠ Alertas:
  • 2 pacientes con expediente incompleto (faltan consentimientos firmados)
```

## Métricas accionables específicas a telemedicina

- **Tasa pre-pago**: telemedicina típicamente requiere pago antes (vs presencial puede ser después)
- **Distribución geográfica**: oportunidad de expandir tarifas regionales
- **Adherencia segunda consulta**: indicador de calidad de primera consulta

## Dependencias

- `mp_facturama_extendido` (CFDIs)
- Tracker local de consultas
