---
description: Corre la cobranza escalonada multinivel de toda la cartera vencida (D+3 WA suave → D+30 carta formal → D+45 escalación legal). Despacha el subagent workflow-cobranza-multinivel.
argument-hint: "[opcional: cliente específico o filtros como --dias-min=15]"
allowed-tools: Read, Write, Edit, Bash, Task
---

# /freelancers:cobranza-mensual

Procesa toda la cartera vencida en una pasada con escalación automática: $ARGUMENTS

## Lo que hace

1. **Inventaria** todos los CFDIs PPD sin pago conciliado en los últimos 90 días.
2. **Verifica status** de cada CFDI contra SAT (no cancelados).
3. **Asigna nivel** según días vencidos:
   - Nivel 1 (D+4-7): recordatorio suave por WhatsApp
   - Nivel 2 (D+8-14): recordatorio formal por WhatsApp + email
   - Nivel 3 (D+15-29): marca para llamada del usuario + mensaje firme
   - Nivel 4 (D+30-44): genera carta formal de requerimiento (PDF)
   - Nivel 5 (D+45+): alerta crítica + sugerencia legal
4. **Ejecuta** las acciones automáticas (templates aprobados WhatsApp + emails).
5. **Genera bitácora** consolidada de toda la corrida.

## Cómo lo ejecuta

Despacha al subagent `workflow-cobranza-multinivel` (en `freelancers-mx/agents/`) para procesar N facturas sin inflar el contexto.

## Cuándo usar

- Semanal: corrida automática
- Cierre de mes: revisión completa antes de declaración
- Después de procesar pagos del mes: identificar quién falta
- Cuando entra un cliente moroso nuevo

## Output esperado

```
Cartera vencida: 23 CFDIs ($487,500 MXN)
  Nivel 1: 5 (WhatsApp suave enviado)
  Nivel 2: 8 (WhatsApp + email enviado)
  Nivel 3: 6 (Marcados para llamada)
  Nivel 4: 3 (Carta formal generada)
  Nivel 5: 1 (Alerta crítica — $95k vencido 50 días)

⚠ Acciones que requieren tu input:
  - Cliente XYZ ($95k, 50 días): considerar escalación legal
  - 6 clientes nivel 3 pendientes de llamar

Bitácora completa: bitacora/cobranza-2026-03-15.jsonl
```

## Filtros opcionales

```
/freelancers:cobranza-mensual --cliente=ABC-CV
/freelancers:cobranza-mensual --dias-min=15
/freelancers:cobranza-mensual --monto-min=10000
```

## Validación legal pendiente

⚠ La plantilla de **carta formal de requerimiento** (nivel 4) requiere revisión por abogado mercantilista antes de uso productivo. Las cartas generadas llevan marca "SIMULADO / REQUIERE VALIDACIÓN LEGAL" hasta que se confirme con experto.

## Modo simulado

Sin credenciales reales WhatsApp/PAC: el workflow genera los textos sugeridos sin enviarlos. Reporte final indica claramente cuáles se "habrían enviado" en modo real.
