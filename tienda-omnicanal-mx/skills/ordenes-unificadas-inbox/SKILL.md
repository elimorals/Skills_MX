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

→ Acciones sugeridas (las ejecuta el agente con los tools de abajo, no son comandos):
  • marcar 12 nuevas como procesando
  • generar guías (cotizador/agregador de paquetería; ver paqueteria-mx)
  • timbrar CFDI de las 8 que traen RFC (facturama_timbrar_cfdi)
```

## Acciones batch

- Procesar batch (mover de "nuevas" a "procesando")
- Imprimir guías de envío (no hay MCP de paquetería: agregador o portal del carrier)
- Emitir CFDI para las que traen RFC; el resto al CFDI global (ver `cfdi-emision`)
- Marcar enviadas con tracking (`shopify_create_fulfillment` en Shopify; en ML/Amazon según su logística)
- Reportar canceladas a canal origen

## Dependencias

- `mercadolibre_list_orders` / `mercadolibre_get_order`, `amazon_mx_list_orders` / `amazon_mx_get_order`, `shopify_list_orders` / `shopify_get_order` (MCPs "real sin validar", requieren credenciales; sin ellas, CSV exportado de cada panel)
- `facturama_timbrar_cfdi` (MCP `mp_facturama_extendido`) para CFDI
- Tracker manual tienda física
- WhatsApp e Instagram: no hay MCP en el repo; captura manual o exportación (ver `whatsapp-business-mx`). Datos personales del cliente: tratarlos conforme a la LFPDPPP (ver `compliance-lfpdppp`)
