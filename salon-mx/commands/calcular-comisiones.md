---
description: Calcula comisiones mensuales de todos los estilistas según modelo configurado (fijo, escalonado, mixto, por servicio). Incluye bonos retención y deducciones.
argument-hint: "[mes y año, ej. 'marzo 2026']"
allowed-tools: Read, Write, Edit, Bash
---

# /salon:calcular-comisiones

Calcula comisiones del mes: $ARGUMENTS

## Lo que hace

1. Invoca skill `comisiones-estilistas` para cada estilista activo.
2. Consolida servicios completados del mes (de la bitácora del cierre diario).
3. Aplica modelo de comisión configurado:
   - Fijo lineal
   - Escalonado por volumen
   - Mixto (sueldo base + comisión sobre umbral)
   - Por tipo de servicio
4. Suma bonos por retención (clientes que regresaron en ventana).
5. Resta adelantos, préstamos, ISR, IMSS si aplica.
6. Genera reporte por estilista + total a pagar.

## Output esperado

```
✓ Comisiones marzo 2026

Modelo activo: escalonado por volumen mensual

Por estilista:
┌─────────┬───────────┬─────────┬───────────┬──────────┐
│Estilista│ Brutos    │ % aplic │ Comisión  │ Pago net │
├─────────┼───────────┼─────────┼───────────┼──────────┤
│ Carla   │ $98,500   │ 38%     │ $37,430   │ $35,200  │
│ Ana     │ $65,200   │ 38%     │ $24,776   │ $23,150  │
│ Sofía   │ $42,800   │ 32%     │ $13,696   │ $12,400  │
│ Pedro   │ $28,900   │ 25%     │ $7,225    │ $6,750   │
└─────────┴───────────┴─────────┴───────────┴──────────┘

Total a pagar: $77,500 MXN
Bonos retención del mes: $4,800
Productos vendidos (comisión retail): $1,150

Alertas:
  • Carla cerca de superar $100k → siguiente nivel comisión 42%
  • Pedro debajo de umbral por 2do mes → revisar productividad
```
