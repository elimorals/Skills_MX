---
name: calendario-fiscal-clientes
description: Calendario consolidado de obligaciones fiscales de TODOS los clientes del despacho. Genera vista diaria/semanal de quiénes tienen pagos provisionales, anuales, IMSS-IDSE, DIOT, contabilidad electrónica, etc., por mes. Útil para no perder ningún deadline. Usar cuando el usuario diga calendario fiscal, obligaciones clientes, deadlines del mes.
allowed-tools: Read, Write
---

# Calendario fiscal clientes

## Output mensual

```
📅 JUNIO 2026 — Obligaciones fiscales clientes

Día 12 (HOY):
  • DIOT mayo: 8 clientes PM pendientes
  • Contabilidad electrónica 5 PM

Día 14-17 (próximos):
  • Pago provisional ISR/IVA mayo: 35 clientes
  • IMSS junio: 15 patronales

Día 30:
  • CFDI nómina junio fin de mes: 12 patronales

Total tareas mes: 84
Completadas: 22 (26%)
En riesgo (deadline < 3 días): 8 ⚠
```

## Schema obligación

```python
class ObligacionFiscal(BaseModel):
    cliente_id: str
    cliente_rfc_hash: str
    tipo_obligacion: Literal["isr_iva_prov", "anual_pf", "anual_pm", "diot", "idse_imss", "cfdi_nomina", "contabilidad_electronica"]
    periodo: str  # "2026-05"
    deadline: date
    estado: Literal["pendiente", "en_proceso", "completada", "vencida"]
    responsable_despacho: str
    importe_a_pagar_estimado_mxn: Decimal | None
```
