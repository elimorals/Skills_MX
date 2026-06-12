---
name: workflow-pf-anual-completa
description: Workflow orquestador end-to-end para declaración anual PF en México. Ejecuta secuencialmente recopilación de CFDIs, identificación de deducciones personales, cruce con bancos, cálculo ISR, generación de borrador y comparativa con pagos provisionales. Detecta alertas críticas (depósitos sin facturar > $15k/mes, CFDIs de RFC en lista 69-B, saldo a favor > $100k). Usar al inicio del ciclo (marzo-abril) o cuando el usuario diga corre todo el flujo anual, declaración completa, end-to-end, workflow anual.
allowed-tools: Read, Write
---

# Workflow PF Anual Completa

Orquestador end-to-end. Ejecuta las 8 fases en secuencia, validando que cada una complete antes de pasar a la siguiente.

## Fase 0 — Validación inicial

- Confirmar `regimen` ∈ {PFAE_612, RESICO_PF_626, ASALARIADO_HONORARIOS_605}
- Si no está claro: preguntar al usuario antes de empezar
- Confirmar `ejercicio` (default: año previo)
- Verificar e.firma vigente si modo real (vía `mp_sat_portal.sat_verificar_efirma_vigente`)
- Si e.firma vence en < 30 días: alertar pero continuar

## Fase 1 — Recopilación de CFDIs

Invocar `recopilar-cfdis-anuales` con `(rfc, ejercicio)`.

Espera output con `total_cfdis_emitidos`, `total_cfdis_recibidos`, `ingresos_mxn`, etc.

Si modo mock: data sintética OK.
Si modo real: puede tardar 4-24h (avisar al usuario).

## Fase 2 — Identificación de deducciones personales

Invocar `identificar-deducciones-personales` con el dataset de CFDIs recibidos.

Espera output con `deducciones_personales_totales_mxn` + categorías.

## Fase 3 — Cruce bancos vs CFDIs

Invocar `cruzar-bancos-vs-cfdis`.

Si modo mock o sin extractos bancarios: omitir con warning.
Si encuentra depósitos sin facturar > tolerancia: incluir en alertas críticas.

## Fase 4 — Cálculo ISR anual

Invocar `calculadora-isr-anual` con todos los inputs anteriores + pagos provisionales del tracker `cierre-fiscal-mensual` (del `core-mexico`).

Espera: `isr_anual_causado_mxn`, `pagos_provisionales_acumulados_mxn`, `diferencia_mxn`, `resultado`.

## Fase 5 — Análisis de riesgo

Determinar:
- Si saldo a favor > $50,000: alerta riesgo auditoría
- Si saldo a favor > $100,000: alerta crítica
- Si depósitos sin facturar > $15k acumulado/mes: alerta discrepancia
- Si CFDIs con RFC en 69-B definitivo: excluir + alertar

## Fase 6 — Generación de borrador

Invocar `generar-borrador-declaracion`.

Output: PDF presentable + path local.

## Fase 7 — Registro en tracker anual

Persistir resultado en `~/.local/share/plugins-mx/pf-anual/<rfc_hash>/<ejercicio>/resultado.json` para comparativa con años futuros.

## Fase 8 — Recomendaciones finales

Listar acciones específicas:
1. "Llevar PDF a contador certificado antes del 25 de abril"
2. "Si se solicita devolución, configurar CLABE de cobro en DeclaraSAT"
3. "Si saldo a pagar > $50k: opciones de pago en parcialidades"
4. "Si depósitos sin facturar: considerar facturar retroactivamente"
5. Próxima sesión: `/pf-anual:status-devolucion` (mayo-julio)

## Output final

```json
{
  "workflow": "pf-anual-completa",
  "rfc_hash": "...",
  "ejercicio": 2025,
  "regimen": "PFAE_612",
  "fases_completadas": [0, 1, 2, 3, 4, 5, 6, 7, 8],
  "isr_causado_mxn": "238250.00",
  "diferencia_mxn": "10750.00",
  "resultado": "SALDO_A_PAGAR",
  "pdf_borrador_path": "~/.local/share/plugins-mx/declaraciones/2025/abc123-borrador.pdf",
  "alertas_criticas": [],
  "siguiente_paso": "Revisar con contador certificado antes del 25 abril 2026",
  "vigencia_validada": false
}
```

## Casos edge

| Caso | Comportamiento del workflow |
|---|---|
| Fase 1 falla (e.firma vencida) | Abortar + sugerir renovar e.firma |
| Fase 1 retorna 0 CFDIs | Continuar con warning "año sin actividad" |
| Fase 3 omitida (sin bancos) | Continuar pero marcar `riesgo_discrepancia: no_evaluado` |
| Régimen mid-año (cambio PFAE → RESICO) | Calcular cada periodo por separado en Fase 4 |
| RESICO PF con ingresos > $3.5M | Recalcular Fase 4 como PFAE |
| Aborto mid-workflow | Persistir progreso, permitir reanudar |

## Compliance

- Hashear RFC, UUIDs, montos en logs
- `vigencia_validada: false` final
- Mensaje cierre debe incluir disclaimer "no sustituye opinión de contador"
- Aviso LFPDPPP firmado por usuario antes de Fase 1 (mp_sat_portal accede a datos personales)
