---
name: dashboard-ejecutivo-clinica
description: Dashboard ejecutivo para director/administrador de clínica con vista consolidada de todos los médicos, ingresos por especialidad, ocupación de consultorios, top diagnósticos, comisiones pagadas a médicos, ingresos pendientes aseguradoras, KPIs operativos (consultas/día, tasa cancelación, etc.). Usar cuando el usuario diga dashboard clinica, director clinica, kpis clinica.
allowed-tools: Read, Write
---

# Dashboard ejecutivo clínica

## Output

```
🏥 CLÍNICA LA SALUD — Mes Junio 2026

💰 Ingresos:
  Bruto total:        $1,250,000 MXN
  Cobrado:              $980,000 (78%)
  Pendiente asegur.:    $270,000 (45d promedio)

👥 Actividad:
  Consultas totales:    485
  Pacientes únicos:     362
  Primera vez:           87 (24%)

🏆 Top 3 médicos por ingreso:
  1. Dr. Ramírez (Cardio):    $295,000 — comisión 60%
  2. Dra. López (Pediatría):  $182,000 — comisión 65%
  3. Dr. Suárez (Gen):         $156,000 — comisión 55%

🩺 Especialidades top:
  Cardiología:  $325,000 (26%)
  Pediatría:    $245,000 (20%)
  Medicina Gen: $198,000 (16%)
  Dermatología: $172,000 (14%)

📊 Ocupación consultorios:
  Consult. 1:  88% — over-subscribed
  Consult. 2:  72%
  Consult. 3:  45% — sub-utilizado

⚠ Alertas:
  • 12 expedientes con > 30d sin notas seguimiento
  • 3 medicamentos cerca caducidad ($8k pérdida potencial)
  • Aseguradora GNP atrasa pagos > 60d en 8 consultas
```

## KPIs operativos

- Consultas/día por médico (productividad)
- Tasa retención pacientes
- Margen por especialidad
- Días promedio cobro aseguradoras
- Rotación inventario
