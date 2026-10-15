---
name: dashboard-tramite-migratorio
description: Dashboard del estatus migratorio actual del extranjero. Muestra documento vigente, fecha de vencimiento, días restantes, ventana de renovación (30 días antes), próximos trámites, alertas activas y costos del año con derechos 2026 de la LFD. Usar cuando el usuario diga status migración, dashboard residencia, cómo va mi visa, cuándo vence mi tarjeta, resumen migratorio.
allowed-tools: Read, Write
---

# Dashboard migratorio

Calcula los días con la fecha de hoy y toma costos de `tramites-residencia-inm` (Art. 8o LFD 2026). No inventes costos: si el trámite no está en esa tabla, márcalo "verificar".

## Output

Ejemplo con fecha de cálculo 2026-10-14:

```
🌎 ESTATUS MIGRATORIO

Nombre: [Hash]
País de origen: USA
Documento vigente: RESIDENTE TEMPORAL
Vigencia: 2026-01-15 al 2027-01-14
Días restantes: 92

📅 Próximos trámites:
  • Renovación temporal — reunir documentos ya; presentar entre 2026-12-15 y 2027-01-14
  • Derechos 2026: $11,140.74 (1 año) · $16,693.36 (2 años) · $21,142.58 (3 años)
    (50% si acredita unidad familiar u oferta de empleo con CIE; confirmar con INM)

🎯 Elegibilidad a permanente:
  Años como temporal: 1 de 4
  Elegible a partir de: 2030-01-15 (o antes por vínculo familiar, Art. 54 LM)

📋 Pendientes:
  • Avisar al INM cambios de domicilio o trabajo (90 días, Art. 63 LM)
  • Pasaporte: vence 2027-06 — renovarlo antes de la renovación migratoria
```
