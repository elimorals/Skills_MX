---
name: shopify-mx
description: Configuración y gestión de tienda Shopify específica para mercado mexicano (CFDI por venta, pasarelas con OXXO/SPEI como Mercado Pago, Conekta, Openpay o Shopify Payments si está disponible, paqueterías nacionales Estafeta/DHL MX/FedEx MX en lugar de USPS, ofertar pesos con IVA incluido, exigencias LFPDPPP, traducción mx-MX vs es-ES). Útil para sellers cross-border y locales MX. Usar cuando el usuario diga Shopify México, tienda en línea MX, configurar Shopify MX, gateway Conekta Shopify, paqueterías Shopify, CFDI Shopify. NO usar para Shopify de otros países (es genérico) — este es solo para operación MX.
allowed-tools: Read, Write, Edit
---

# Shopify para mercado mexicano

Shopify por default está optimizado para US/CA. Operar en México requiere ajustes específicos.

## Setup inicial obligatorio

### Moneda y formato
- Moneda principal: **MXN** (no USD aunque tengas tráfico US)
- Formato display: `$1,234.56` con coma para miles
- `Precios con impuestos incluidos`: SÍ (Art. 7 Bis LFPC: el precio mostrado debe ser el monto total con impuestos y cargos)

### Idioma
- Locale: `es-MX` (no `es-ES` — distinto vocabulario)
- Localización de checkout: revisar traducción de "Add to cart" → "Agregar al carrito"
- Información al consumidor en español (Art. 76 Bis LFPC y NOM-050-SCFI-2004 para productos)

### Información de la tienda
- Razón social completa (no solo nombre comercial)
- RFC del titular
- Domicilio físico, teléfonos y medios para reclamaciones, visibles **antes** de la compra (Art. 76 Bis fr. III LFPC)
- Aviso de privacidad conforme a la LFPDPPP (DOF 20-03-2025) enlazado desde el footer; autoridad: Secretaría Anticorrupción y Buen Gobierno (ver `compliance-lfpdppp`)
- Términos y condiciones con: derecho de revocación de 5 días hábiles (Art. 56 LFPC), garantía (Arts. 77-78) y reposición/devolución por defectos (Art. 92)
- Si vendes suscripciones con cobro recurrente: informar periodicidad, monto y fecha, pedir consentimiento expreso, avisar la renovación automática con 5 días naturales de anticipación y permitir cancelar sin penalización (Art. 76 Bis fr. VIII-IX LFPC, DOF 12-12-2025)

## Pasarelas de pago

Elegir según los medios que pide tu cliente (tarjeta, OXXO, SPEI, MSI) y el costo real:

| Pasarela | Medios típicos | Nota |
|---|---|---|
| **Shopify Payments** | Tarjetas, wallets | Fuentes de terceros 2026 la listan como disponible en México (confianza media); confirmar en Settings > Payments de tu tienda |
| **Mercado Pago** | Tarjeta, OXXO, MSI, saldo MP | Útil si tu cliente ya usa Mercado Pago |
| **Conekta** | Tarjeta, OXXO, SPEI | Pasarela mexicana |
| **Openpay (BBVA)** | Tarjeta, tiendas, SPEI | Alternativa |
| **PayPal** | Saldo PayPal, tarjeta | Útil para compradores internacionales |

Tarifas: **verificar** en el sitio de cada pasarela al contratar (cambian y se negocian por volumen). Con pasarela externa Shopify puede cobrar además una comisión por transacción según tu plan.

Activar en Shopify > Settings > Payments.

## Paqueterías locales

Shopify por default integra UPS, USPS (US-only). Para MX:

| Paquetería | Integración | Cobertura |
|---|---|---|
| **Estafeta** | App o vía agregador | Nacional MX |
| **DHL** | App o vía agregador | Nacional + internacional |
| **FedEx** | App o vía agregador | Nacional + internacional |
| **Agregadores (Skydropx, Envia.com, etc.)** | App Shopify | Multi-carrier, comparan tarifa por ruta |
| **99 Minutos** | App propia | Mismo día / día siguiente en zonas metropolitanas |
| **Mercado Envíos** | Solo para ventas en ML | — |

Tarifas: cotizar por ruta en el agregador (ver `paqueteria-mx`).

Instalar al menos 2: una nacional (Estafeta o DHL) + una para CDMX express (99 Minutos).

## Impuestos (Settings > Taxes)

Configuración México:
- Tax region: México
- Charge tax: SÍ
- Tax inclusive prices: SÍ (precio mostrado YA incluye IVA)
- Tax rate: 16% general; 8% solo si el vendedor aplica el estímulo de región fronteriza (aviso ante SAT, entrega en la región; vigente a 31-12-2026)

⚠ Tasa 0% no es lo mismo que exento. Tasa 0% (Art. 2-A LIVA): medicinas de patente, alimentos no procesados y otros. Libros: tasa 0% si los edita el propio vendedor; en reventa son exentos (Art. 9 fr. III LIVA). Shopify solo maneja "cobra / no cobra impuesto": configura un override por colección y refleja la diferencia en el CFDI (tasa 0% vs exento). Ver `iva-retenciones-mx` y `cfdi-emision`.

## CFDI por venta

Shopify NO emite CFDIs nativos. Opciones:

### Opción A: App de terceros (recomendado)
| App | Costo | Pros | Contras |
|---|---|---|---|
| **App de facturación del PAC** (p. ej. Facturama) | Verificar | Integración directa | Atado a un PAC |
| **ERP con conector Shopify** (p. ej. Bind ERP) | Verificar | ERP completo | Más complejo |

Precios de apps: **verificar** en la Shopify App Store.

### Opción B: Webhook → MCP propio
Webhook Shopify `orders/paid` (o `orders/create`) → endpoint propio que llama a `facturama_timbrar_cfdi` del MCP `mp_facturama_extendido` (antes `facturama_validar_payload_local`). Más control, más trabajo. `shopify_list_webhooks` muestra qué webhooks tiene la tienda.

### Opción C: CFDI bajo solicitud
Cliente recibe email "factúrame esta compra" → ingresa RFC → emites CFDI manual. Funciona para volumen bajo (< 50 ventas/mes).

⚠ En México todas las ventas requieren CFDI:
- **Con RFC del comprador**: CFDI a su nombre (lo puede pedir PF o PM)
- **Sin RFC**: CFDI global a público en general (XAXX010101000) con nodo InformacionGlobal; periodicidad diaria, semanal, quincenal o mensual (bimestral solo en los casos previstos, p. ej. RESICO PF). Ver `cfdi-emision`

## Apps esenciales MX

| Categoría | App | Por qué |
|---|---|---|
| Facturación | Facturama / Bind ERP / B Sale | CFDI automático |
| Logística | Skydropx / Envia.com | Multi-carrier MX |
| Reviews | Loox / Stamped | Reseñas con foto (PROFECO friendly) |
| WhatsApp | WhatsApp Business by Shopify | Notificaciones a cliente |
| Tracking | AfterShip | Status envío |
| Email | Klaviyo | Newsletter + abandono carrito |

## Casos edge específicos MX

### 1. RFC del cliente para factura
Capturar en checkout con campo extra `Cliente solicita factura?`. Validar formato RFC con `rfc-validacion` skill.

### 2. Devoluciones
- Venta a distancia: el consumidor puede revocar la compra dentro de **5 días hábiles** desde que recibe el bien; reembolsas el precio y el flete de devolución corre por su cuenta (Art. 56 LFPC).
- Producto defectuoso o distinto a lo ofrecido: reposición o devolución del dinero a elección del consumidor, más bonificación mínima de 20% (Arts. 92 y 92 Ter); reclamación dentro de 2 meses (Art. 93).
- Una política más amplia (p. ej. 30 días) es decisión comercial, no obligación legal. Escríbela en Términos y cúmplela.

### 3. OXXO Pay (Conekta + MercadoPago)
Cliente paga en tienda física con una referencia que vence en el plazo que fije la pasarela. **No marcar orden como pagada hasta confirmar webhook**.

### 4. Tipo de cambio
Si cotizas en USD pero cobras MXN: `banxico_get_tc_dof` / `banxico_convertir_monto` (MCP `mp_banxico`, requiere `BANXICO_TOKEN`; sin token devuelve datos simulados). Muestra siempre el precio final en MXN (Art. 7 Bis LFPC).

### 5. Servicio al cliente WhatsApp
En México WhatsApp suele tener mejor respuesta que el email. Con la API de WhatsApp Business, Meta cobra por mensaje de plantilla desde 01-07-2025 (ver `whatsapp-business-mx`).

## Output estructurado

```json
{
  "audit_shopify_mx": {
    "shop": "tienda.myshopify.com",
    "configuracion": {
      "moneda": "MXN",
      "idioma": "es-MX",
      "tax_inclusive": true,
      "tax_rate": 0.16,
      "aviso_privacidad_publicado": true,
      "rfc_titular_configurado": true
    },
    "gateways_activos": ["conekta", "mercadopago"],
    "paqueterias_activas": ["estafeta", "99minutos"],
    "cfdi_emision": {
      "metodo": "app_pac",
      "timbrado_al_pagar": true,
      "cobertura": "b2c_y_b2b"
    },
    "score": 8.5,
    "gaps": [
      "Falta integrar tracking AfterShip",
      "Webhook order.created no notifica WhatsApp"
    ],
    "siguientes_pasos": [
      "Instalar app AfterShip",
      "Configurar template WhatsApp 'orden confirmada'"
    ]
  }
}
```

## Limitaciones

- MCP `mp_shopify_mx`: "real sin validar (requiere credenciales)". Tools: `shopify_list_products`, `shopify_get_order`, `shopify_list_orders`, `shopify_get_inventory_level`, `shopify_update_inventory_level`, `shopify_create_fulfillment`, `shopify_list_webhooks`, `shopify_calculate_tax_mx`.
- Tarifas de pasarelas, apps y paqueterías: verificar al contratar.
- No sustituye la revisión legal de tus Términos y aviso de privacidad.

## Ver también

- `mercado-libre-listings` — alternativa marketplace
- `inventario-multicanal` — sincronizar con ML
- `paqueteria-mx` — comparar tarifas
- `mp_shopify_mx` MCP
