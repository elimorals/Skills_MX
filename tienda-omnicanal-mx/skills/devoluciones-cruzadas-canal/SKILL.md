---
name: devoluciones-cruzadas-canal
description: Gestiona devoluciones cuando el cliente compra en un canal y devuelve en otro (típico: compra ML, devuelve en tienda física). Reconcilia el flujo: cliente entrega item, verifica autenticidad (orden ML correcta), procesa reembolso por canal original, actualiza inventario en TODOS los canales, y emite nota de crédito CFDI si aplica. Usar cuando el usuario diga devolución cruzada, cliente devuelve en tienda, refund cross-channel, nota credito devolucion.
allowed-tools: Read, Write
---

# Devoluciones cruzadas canal

## Flujo típico

1. Cliente compró en ML → recibe item → no le gusta
2. Acude a tienda física en lugar de mandarlo de regreso por paquetería
3. Tienda verifica: orden ML existe + item coincide + dentro de plazo devolución (típico 7-30 días)
4. Tienda procesa reembolso (efectivo si pagó efectivo en ML, transferencia si pagó tarjeta)
5. Item se reintegra al inventario
6. ML se notifica del refund
7. Emite nota de crédito CFDI si CFDI original existe

## Validaciones

```python
def validar_devolucion(orden_id: str, canal: str, item_sku: str) -> dict:
    # 1. Orden existe
    orden = consultar_orden(orden_id, canal)
    if not orden:
        return {"valido": False, "razon": "orden_no_encontrada"}

    # 2. Item del SKU está en la orden
    if item_sku not in [i.sku for i in orden.items]:
        return {"valido": False, "razon": "item_no_en_orden"}

    # 3. Dentro de plazo
    dias_desde_entrega = (today - orden.fecha_entrega).days
    if dias_desde_entrega > 30:
        return {"valido": False, "razon": "fuera_plazo_30d"}

    # 4. No devuelto previamente
    if orden.estado == "devuelta":
        return {"valido": False, "razon": "ya_devuelta"}

    return {"valido": True, "monto_a_reembolsar_mxn": orden.total - orden.envio}
```

## Output

```json
{
  "operation": "devolucion_cruzada",
  "orden_origen": "ML-12345",
  "canal_origen": "mercadolibre",
  "canal_devolucion": "tienda_fisica",
  "fecha_devolucion": "2026-06-12",
  "items_devueltos": [{"sku": "SKU-001", "cantidad": 1, "valor_mxn": "289.00"}],
  "monto_reembolso_mxn": "289.00",
  "metodo_reembolso": "transferencia_spei",
  "nota_credito_cfdi_emitida": true,
  "nota_credito_uuid": "abc-123",
  "inventario_actualizado_canales": ["mercadolibre", "amazon", "shopify"],
  "estado": "completado"
}
```

## Casos edge

| Caso | Acción |
|---|---|
| Cliente sin orden ID pero con item físico | Pedir CFDI o ticket; si no, política de tienda |
| Item dañado / usado | Aplicar deducción o rechazar |
| Pagó con tarjeta crédito | Reembolso a misma tarjeta (3-7 días) |
| ML no permite refund retroactivo > 30d | Hacer refund interno (tienda), ML queda completada |
| Cliente quiere cambio (no reembolso) | Procesar swap + ajuste de inventario |
