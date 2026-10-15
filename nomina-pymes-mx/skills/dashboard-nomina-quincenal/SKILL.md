---
name: dashboard-nomina-quincenal
description: Dashboard quincenal de nómina con resumen de empleados activos, sueldos brutos, retenciones (ISR, IMSS obrero, INFONAVIT, pensión alimenticia), costo patronal (IMSS, INFONAVIT 5%, impuesto sobre nómina estatal), neto a dispersar y alertas (empleados sin RFC, CFDI sin timbrar, vacaciones por vencer, avisos IDSE pendientes). Útil al cierre de cada quincena antes de dispersar pagos. Usar cuando el usuario diga dashboard nómina, resumen de quincena, status de empleados, cierre de nómina, cuánto me cuesta la nómina.
allowed-tools: Read, Write
---

# Dashboard nómina quincenal

Toma los cálculos de `calculo-isr-salarios-art96`, `cuotas-imss-sbc` y `cuotas-infonavit-5pct`. No estimes costos con porcentajes fijos: suma lo calculado.

## Output (ejemplo con cifras cuadradas)

```
📋 NÓMINA — 1.ª quincena de junio 2026 (01-15 jun)

👥 Empleados:
  Activos:                  28
  Bajas mes:                 1 (José M. - 2026-06-10)
  Altas mes:                 2 (Ana T., Carlos R.)

💰 Sueldos brutos:        $385,400
   ISR retenido:          $ 42,180
   IMSS obrero:           $  9,150
   INFONAVIT (descuentos): $  5,830
   Pensión alimenticia:   $  8,200
   Otros descuentos:      $    650
   ─────────────────────────────
   Neto a dispersar:      $320,390

📊 Costo patronal (provisión de la quincena):
   IMSS patronal (sin RT): $ 38,540
   Riesgo de trabajo:     $  4,800
   INFONAVIT 5%:          $ 19,270
   ISN estatal:           $  <isn_calcular>
   ─────────────────────────────
   Total sin ISN:         $ 62,610

🎯 Costo total nómina (sin ISN): $448,010

⚠ Alertas:
  • 2 empleados sin RFC validado — bloquear CFDI
  • 1 aviso IDSE de alta pendiente (vence en 2 días hábiles)
  • Juan P.: 5 días de vacaciones deben otorgarse antes del 2026-12-31
  • Provisión de aguinaldo: 15 días × salario diario / 24 quincenas por empleado
```

Comprobación: 385,400 − (42,180 + 9,150 + 5,830 + 8,200 + 650) = 320,390; 38,540 + 4,800 + 19,270 = 62,610; 385,400 + 62,610 = 448,010.

## Métricas accionables

- **Costo patronal / sueldo bruto**: calcúlalo; en 2026 sube por la cuota patronal de cesantía y vejez (reforma 2020, incrementos anuales hasta 2030) y depende de la prima de RT y del estado (ISN).
- **ISN**: impuesto estatal sobre nóminas; usa `isn_calcular` del MCP `mp_isn_mx` (tasas 2026 con fuente secundaria, confianza media).
- **Rotación**: bajas/altas del mes.
- **Cumplimiento CFDI**: % timbrados antes de pagar.
- **Provisión de aguinaldo y PTU** vs. lo requerido al cierre.

Cifras orientativas; valida con tu contador antes de dispersar.
