---
name: inventario-medicamentos-insumos
description: Control de inventario de medicamentos e insumos médicos de la clínica con alertas de stock bajo, caducidades próximas (90/30/7 días) y registro de uso por paciente/consulta. Manejo especial de estupefacientes y psicotrópicos (LGS Arts. 234 y 245) con libros de control, custodia y conciliación física. Usar cuando el usuario diga inventario medicamentos, stock clínica, caducidades, control de psicotrópicos, libro de control, botiquín de controlados, medicamentos caducos.
allowed-tools: Read, Write
---

# Inventario medicamentos + insumos

## Categorías

| Tipo | Control |
|---|---|
| Medicamentos sin restricción especial (Art. 226 fr. IV-VI LGS) | Inventario normal + caducidad + lote |
| Psicotrópicos (Art. 245 fr. II-IV, p. ej. benzodiacepinas, tramadol, fenobarbital) | **Libro de control** + custodia bajo llave + conciliación |
| Estupefacientes (Art. 234, p. ej. morfina, fentanilo) | **Libro de control** + custodia + recetario especial para su prescripción |
| Insumos de curación | Inventario normal |
| Material de laboratorio / reactivos | Caducidad estricta |

Manejar estupefacientes o psicotrópicos puede requerir **licencia sanitaria** (LGS Art. 198 fr. I: "proceso", que incluye suministro, de medicamentos con estupefacientes y psicotrópicos) y responsable sanitario. Confirmar el trámite de la clínica con `mp_cofepris_aviso_funcionamiento` → `cofepris_clasificar_giro` y con la COFEPRIS/autoridad estatal. Formato y periodicidad de los libros/reportes: **verificar** con la autoridad (no se cotejó el Reglamento de Insumos para la Salud).

## Alertas

- **Stock < punto de reorden**: marcar para reabastecer
- **Caducidad 90 días**: alerta amarilla
- **Caducidad 30 días**: alerta naranja
- **Caducidad < 7 días**: alerta crítica + bloquear uso
- **Caducado**: separar, no usar y disponer como residuo con empresa autorizada (los controlados requieren además el procedimiento de destrucción ante la autoridad sanitaria — **verificar**)

## Output

```json
{
  "items_total": 245,
  "stock_bajo_count": 12,
  "caducidad_proxima_30d": 8,
  "caducidad_critica_7d": 3,
  "valor_inventario_mxn": "185000.00",
  "controlados_inventario": {
    "items": 5,
    "ultima_conciliacion_libro_vs_fisico": "2026-09-30",
    "diferencias": 0
  },
  "alertas_criticas": [
    "Insulina glargina caduca 2026-10-20 — uso priorizado o devolución a proveedor"
  ]
}
```

## ⚠ Controlados

- Libro de control actualizado en cada entrada, salida y baja (LGS Art. 226 fr. II-III mencionan los libros de control)
- Inventario físico vs libro: debe coincidir 100%; cualquier diferencia se investiga y documenta
- Custodia bajo llave con responsable nombrado
- Conservar recetas retenidas y documentación para inspección
