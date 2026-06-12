---
name: inventario-medicamentos-insumos
description: Control de inventario de medicamentos e insumos médicos de la clínica con alertas de stock bajo, caducidades próximas (90/60/30 días), y registro de uso por paciente/consulta. Manejo especial de psicotrópicos (libros de control COFEPRIS). Usar cuando el usuario diga inventario medicamentos, stock clinica, caducidades, control psicotropicos.
allowed-tools: Read, Write
---

# Inventario medicamentos + insumos

## Categorías

| Tipo | Control |
|---|---|
| Medicamento Grupo III-V | Inventario normal |
| Medicamento Grupo I-II controlado | Libro especial COFEPRIS + reporte cada movimiento |
| Insumos curación | Inventario normal |
| Material laboratorio | Caducidad estricta |

## Alertas

- **Stock < punto reorden**: marcar para reabastecer
- **Caducidad 90 días**: alerta amarilla
- **Caducidad 30 días**: alerta naranja
- **Caducidad < 7 días**: alerta crítica + bloquear venta

## Output

```json
{
  "items_total": 245,
  "stock_bajo_count": 12,
  "caducidad_proxima_30d": 8,
  "caducidad_critica_7d": 3,
  "valor_inventario_mxn": "185000.00",
  "psicotropicos_inventario": {
    "items": 5,
    "ultimo_reporte_cofepris": "2026-05-31"
  },
  "alertas_criticas": [
    "Insulina Glargina caduca 2026-06-18 — uso priorizado o devolución proveedor"
  ]
}
```

## ⚠ Compliance psicotrópicos

- Libro de control COFEPRIS obligatorio
- Reporte mensual al SSA cada movimiento (entradas/salidas/destrucciones)
- Inventario físico vs registro debe coincidir 100%
- Custodia controlada (cerradura + responsable nombrado)
