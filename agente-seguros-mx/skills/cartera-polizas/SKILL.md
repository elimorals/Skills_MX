---
name: cartera-polizas
description: Gestiona la cartera de pólizas del agente de seguros con registro por póliza (ramo auto/GMM/vida/daños/fianzas, aseguradora emisora, contratante PF o PM, vigencia desde-hasta, prima total y forma de pago anual o fraccionada, beneficiarios, suma asegurada por cobertura, deducible, comisión base y bono de calidad), cálculo de fechas críticas (renovación 60-30-7 días antes, fin de vigencia, plazo para pagar la prima del Art. 40 LSCS), verificación de que la aseguradora esté autorizada (SIPRES de CONDUSEF) y detección de asegurados con cobertura insuficiente para upsell. Diferencia entre póliza individual y colectiva (empresarial). Usar cuando el usuario diga "cartera seguros", "registrar póliza", "renovaciones próximas", "pólizas vigentes", "dashboard agente seguros", "pólizas por vencer". NO usar para emisión de póliza (eso lo hace la aseguradora) ni para seguimiento de siniestros (usar seguimiento-siniestro).
allowed-tools: Read, Write, Edit
---

# Cartera de pólizas del agente

## Estructura por póliza

```yaml
poliza_id: AXA-AUTO-2026-12345
aseguradora: AXA
ramo: auto  # auto|gmm|vida|daños|fianzas
contratante:
  tipo: PF  # PF|PM
  rfc: ...
  nombre: ...
  contacto_wa: +52...
vigencia:
  desde: 2026-01-15
  hasta: 2027-01-14
prima:
  total: 14500.00
  forma_pago: mensual  # anual|semestral|trimestral|mensual
  plazo_pago_dias: 30  # el pactado en la póliza; si no se pactó, 30 días naturales (Art. 40 LSCS)
  recibos_pagados: 7
  recibos_pendientes: 5
coberturas:
  - tipo: daños_materiales
    suma_asegurada: valor_comercial
    deducible_pct: 5
  - tipo: responsabilidad_civil
    suma_asegurada: 3000000
beneficiarios: []
comision:
  porcentaje_base: 0.18
  bono_calidad_pct: 0.02
  ya_cobrada: 2610.00
estado: vigente  # vigente|recibo_vencido|por_vencer|vencida|cancelada|siniestro_curso
```

## Plazo para pagar la prima (no es "periodo sin cobertura")

Art. 40 de la Ley sobre el Contrato de Seguro: si la prima o el recibo fraccionado no se paga dentro del plazo convenido, los efectos del contrato cesan automáticamente a las 12:00 h del último día de ese plazo; si no se pactó plazo, son 30 días naturales desde el vencimiento del recibo. Durante ese plazo la póliza sigue cubriendo. No aplica igual a los seguros obligatorios del Art. 150 Bis LSCS, salvo pacto.

Este plazo se refiere a recibos de prima de una póliza vigente. Al terminar la vigencia, si la póliza no se renueva, no hay cobertura desde el día siguiente.

## Alertas

- 60 días antes del fin de vigencia: WhatsApp cordial recordando la renovación
- 30 días antes: propuesta de renovación con comparativo
- 7 días antes: recordatorio urgente
- Recibo vencido: avisar el día del vencimiento y 5 días antes de que termine el plazo de pago (la póliza se cancela automáticamente al terminar)
- Fin de vigencia sin renovar: cliente sin cobertura — escalación inmediata

## Verificaciones

- Aseguradora autorizada: `sipres_verificar_autorizada` (MCP `mp_condusef_sipres`).
- Estado de la póliza en la aseguradora: no hay MCP de aseguradoras; consulta el portal de agentes de cada compañía y captura el resultado.

## Output

```
cartera-seguros/<rfc-hash-agente>/
  ├── polizas/
  ├── renovaciones-proximas.json
  ├── cartera-vencida.json
  └── dashboard-rentabilidad.json
```
