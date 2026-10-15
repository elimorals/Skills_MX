---
name: dashboard-consultorio-mes
description: Dashboard mensual para médico especialista con consultorio. Reporta consultas realizadas vs canceladas vs no-show, ingresos brutos vs cobrados (incluye pendientes aseguradoras), pacientes nuevos, retención de pacientes, top diagnósticos del mes, recetas emitidas, y comparativa con meses previos. Usar cuando el usuario diga dashboard consultorio, como va mi mes, estadisticas pacientes, ingresos medico.
allowed-tools: Read, Write
---

# Dashboard mes consultorio

## Output

```
🏥 CONSULTORIO — Junio 2026

📊 Actividad:
  Consultas programadas:  185
  Realizadas:             156 (84%)
  Canceladas:              20 (11%)
  No-show:                  9 (5%)

👥 Pacientes:
  Total atendidos:        156
  Primera vez:             32 (21%)
  Seguimiento:            124 (79%)
  Tasa retención (vs mes pasado): 68%

💰 Ingresos:
  Bruto del mes:          $215,400
  Cobrado:                $182,300 (85%)
  Pendiente aseguradoras:  $33,100 (promedio 45d pago)

🩺 Top diagnósticos:
  1. I10 Hipertensión (32 consultas)
  2. E11.9 Diabetes T2 (28)
  3. K21.9 ERGE (19)

📋 Recetas emitidas:        198 (1.27 por consulta)
   • con psicotrópico (LGS Art. 245 fr. III, receta retenida): 12

📈 vs mes pasado:
  Ingresos: +8%
  Consultas: +5%
  Retención: -3% (alerta)
```

## Métricas accionables

- Tasa no-show > 10% → ajustar política recordatorios
- Tasa cancelación > 15% → revisar tiempo de agenda
- Tasa retención < 60% → revisar experiencia paciente
- Pendiente aseguradoras > 30% del mes → seguimiento cobranza

## Dependencias

- Tracker local consultas + expedientes
- `mp_facturama_extendido` → `facturama_buscar_cfdis` (CFDIs emitidos; requiere credenciales del PAC)
- `mp_bancos_mx` → `bancos_listar_movimientos` (cruce de pagos). Estado "sin verificar" y los bancos bloquean scraping: si falla o pide login, pedir al usuario su estado de cuenta en CSV/PDF

Ingresos en el dashboard sin IVA (consulta de médico PF = exenta, Art. 15 fr. XIV LIVA).
