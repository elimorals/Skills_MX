---
name: ordenes-unificadas-inbox
description: Inbox consolidado de órdenes de TODOS los canales (Mercado Libre, Amazon MX, Shopify, tienda física, WhatsApp directo) en un solo lugar. Cada orden lleva metadata del canal origen, datos del cliente, items, status (nueva, procesando, enviada, entregada, cancelada). Permite triage y acciones masivas (imprimir guías, marcar enviadas, responder mensajes). Usar cuando el usuario diga ordenes pendientes, inbox tienda, procesar pedidos, todas mis ventas.
allowed-tools: Read, Write
---

# Inbox unificado de órdenes

## Schema orden normalizada

```python
class OrdenUnificada(BaseModel):
    orden_id: str               # ID del canal origen
    canal: Literal["mercadolibre", "amazon", "shopify", "tienda_fisica", "whatsapp", "instagram"]
    fecha: datetime
    cliente_nombre: str
    cliente_rfc: str | None
    cliente_tel: str | None
    cliente_email: str | None
    items: list[ItemOrden]
    subtotal_mxn: Decimal
    envio_mxn: Decimal
    total_mxn: Decimal
    estado: Literal["nueva", "procesando", "enviada", "entregada", "cancelada", "devuelta"]
    metodo_pago: str
    fecha_envio_esperada: date | None
    guia_envio: str | None
    cfdi_emitido: bool
    cfdi_uuid: str | None
    notas: str
```

## Vista típica

```
📦 INBOX ORDENES (45 pendientes)

🟢 Nuevas (12):
  • ML-001  | Juan P.   | $580   | 3 items | hace 2h
  • AMZ-001 | María L.  | $290   | 1 item  | hace 4h
  • SHP-001 | Carlos R. | $1,200 | 5 items | hace 30min

🟡 Procesando (8):
  • ML-XXX  | ...

🔵 Enviadas pendientes confirmar entrega (15):
  • ...

⛔ Canceladas (3):
  • ...

→ Acciones disponibles:
  /tienda:procesar-batch     (marcar 12 nuevas como procesando)
  /tienda:imprimir-guias     (batch labels)
  /tienda:emitir-cfdi-batch  (timbrar las 8 que tienen RFC)
```

## Acciones batch

- Procesar batch (mover de "nuevas" a "procesando")
- Imprimir guías de envío
- Emitir CFDI para todas con RFC
- Marcar enviadas con tracking
- Reportar canceladas a canal origen

## Dependencias

- `mp_mercado_libre.listar_ordenes`, `mp_amazon_mx_seller.list_orders`, `mp_shopify_mx.orders_list`
- Tracker manual tienda física
- `mp_meta_whatsapp` para órdenes WA
