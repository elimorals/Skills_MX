---
name: cartera-polizas
description: Gestiona cartera de pólizas del agente de seguros con registro por póliza (ramo auto/GMM/vida/daños/fianzas, aseguradora emisora, contratante PF o PM, vigencia desde-hasta, prima total + forma de pago anual o fraccionado mensual, beneficiarios designados, suma asegurada por cobertura, deducible aplicable, comisión base + bono de calidad si aplica), cálculo automático de fechas críticas (renovación 60-30-7 días antes, vencimiento real, periodo de gracia típico 30 días sin cobertura), validación de status vigente vía portal de la aseguradora cuando disponible (`mp_aseguradoras_mx` futuro), e identificación de asegurados con cobertura insuficiente para upsell. Diferencia entre póliza individual y colectiva (empresarial). Usar cuando el usuario diga "cartera seguros", "registrar póliza", "renovaciones próximas", "pólizas vigentes", "dashboard agente seguros". NO usar para emisión de póliza (eso lo hace la aseguradora) ni para tracking de siniestros (usar seguimiento-siniestro).
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
  pagada: 7
  pendiente: 5
coberturas:
  - tipo: responsabilidad_civil
    suma_asegurada: 3000000
    deducible_pct: 5
beneficiarios: []
comision:
  porcentaje_base: 0.18
  bono_calidad_pct: 0.02
  ya_cobrada: 2610.00
estado: vigente  # vigente|por_vencer|vencida|cancelada|siniestro_curso
```

## Alertas automáticas

- 60 días antes de vencimiento: WA cordial recordando renovación
- 30 días antes: propuesta de renovación con comparativo
- 7 días antes: recordatorio urgente
- 0 días: aviso de inicio de periodo de gracia
- 30 días post-vencimiento: cliente sin cobertura — escalación

## Output

```
cartera-seguros/<rfc-hash-agente>/
  ├── polizas/
  ├── renovaciones-proximas.json
  ├── cartera-vencida.json
  └── dashboard-rentabilidad.json
```
