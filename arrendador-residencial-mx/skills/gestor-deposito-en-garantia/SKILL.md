---
name: gestor-deposito-en-garantia
description: Gestiona depósitos en garantía recibidos del inquilino al firmar contrato. Mantiene registro del monto, fecha recepción, daños descontados durante el contrato, monto a devolver al cierre. Notifica al inquilino al cierre el detalle del descuento si lo hay. Útil para disputas (sin tracking → SAT/jueces favorecen al inquilino). Usar cuando el usuario diga deposito garantia, devolver deposito, daños inquilino.
allowed-tools: Read, Write
---

# Gestor depósito en garantía

## Schema

```python
class DepositoGarantia(BaseModel):
    propiedad_id: str
    inquilino_id_hash: str
    monto_recibido_mxn: Decimal
    fecha_recepcion: date
    moneda: str  # "MXN"
    almacenado_en: str  # cuenta CLABE donde está
    intereses_acumulados_mxn: Decimal | None
    incidentes_durante_contrato: list[IncidenteDano]
    deducciones_potenciales_mxn: Decimal
    monto_estimado_devolver_mxn: Decimal
```

## Output al cierre

```
💰 DEPÓSITO EN GARANTÍA — Propiedad Roma Norte 1A

Depósito original:        $12,000 MXN (recibido 2025-09-01)
Intereses acumulados:     $0 MXN (cuenta sin interés)

Deducciones por daños:
  • Pintura interior:     $3,000  (no es uso normal)
  • Limpieza profunda:    $1,500  (acumulación 12 meses)
  • Vidrio roto cocina:   $800
  ─────────────────────────────
  Total deducciones:      $5,300 MXN

🟢 Monto a devolver:      $6,700 MXN
   Forma:                 Transferencia SPEI
   Deadline:              2026-09-30 (30d post-entrega)
```

## ⚠ Documentación crítica

- Fotos comparativas inicio vs cierre (sin esto, inquilino puede reclamar)
- Recibos/presupuestos de reparaciones
- Carta firmada por inquilino aceptando descuentos (recomendado)
