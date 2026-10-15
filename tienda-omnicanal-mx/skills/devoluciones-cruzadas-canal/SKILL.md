---
name: devoluciones-cruzadas-canal
description: Gestiona devoluciones cuando el cliente compra en un canal y devuelve en otro (típico: compra ML, devuelve en tienda física). Reconcilia el flujo: cliente entrega item, verifica autenticidad (orden ML correcta), procesa reembolso por canal original, actualiza inventario en TODOS los canales, y emite nota de crédito CFDI si aplica. Usar cuando el usuario diga devolución cruzada, cliente devuelve en tienda, refund cross-channel, nota credito devolucion.
allowed-tools: Read, Write
---

# Devoluciones cruzadas canal

## Flujo típico

1. Cliente compró en ML → recibe item → no le gusta
2. Acude a tienda física en lugar de mandarlo de regreso por paquetería
3. Tienda verifica: orden existe (`mercadolibre_get_order` / `amazon_mx_get_order` / `shopify_get_order`) + item coincide + dentro de plazo
4. Reembolso **por el canal de origen** siempre que se pueda (ML/Mercado Pago, Amazon, pasarela de Shopify). Si la tienda reembolsa en mostrador, documenta y evita que el canal reembolse otra vez (doble reembolso)
5. Item se reintegra al inventario si está vendible y se propaga el stock a todos los canales
6. Emite CFDI de egreso (nota de crédito) relacionado al CFDI de la venta; si la venta iba en CFDI global, el egreso también va a público en general (ver `cfdi-emision`)

### Plazos legales mínimos (LFPC)
- **Revocación** en ventas a distancia: 5 días hábiles desde que se recibe el bien; se reembolsa el precio y el flete corre por cuenta del consumidor (Art. 56).
- **Defecto o producto distinto**: reposición o reembolso a elección del consumidor + bonificación mínima de 20% (Arts. 92 y 92 Ter); reclamación dentro de 2 meses desde que se recibió (Art. 93).
- Una ventana mayor (p. ej. 30 días) es política comercial propia o del marketplace (ML y Amazon tienen las suyas: **verificar** la vigente).

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

    # 3. Dentro de plazo: el mayor entre el legal y la política de la tienda/canal
    #    (sin defecto: 5 días hábiles Art. 56 LFPC; con defecto: 2 meses Art. 93)
    if not dentro_de_plazo(orden.fecha_entrega, politica_dias, con_defecto):
        return {"valido": False, "razon": "fuera_de_plazo"}

    # 4. No devuelto previamente
    if orden.estado == "devuelta":
        return {"valido": False, "razon": "ya_devuelta"}

    # Revocación sin defecto: reembolsar precio pagado; el flete de devolución lo paga el cliente.
    # Defecto: reembolso total + bonificación ≥ 20% (Art. 92 Ter).
    return {"valido": True, "monto_a_reembolsar_mxn": orden.total}
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
| Pagó con tarjeta | Reembolso al mismo medio; el plazo de reflejo depende del banco/pasarela |
| El canal ya no permite reembolso (plazo vencido en ML/Amazon) | Reembolso directo de la tienda, documentado, y CFDI de egreso |
| Producto defectuoso | Además del reembolso o reposición, bonificación ≥ 20% (Art. 92 Ter LFPC) |
| Cliente quiere cambio (no reembolso) | Procesar swap + ajuste de inventario |
