---
name: shopify-mx
description: Configuración y gestión de tienda Shopify específica para mercado mexicano (CFDI por venta, MercadoPago/Conekta como gateway local, paqueterías nacionales Estafeta/DHL MX/FedEx MX en lugar de USPS, ofertar pesos con IVA incluido, exigencias LFPDPPP, traducción mx-MX vs es-ES). Útil para sellers cross-border y locales MX. Usar cuando el usuario diga Shopify México, tienda en línea MX, configurar Shopify MX, gateway Conekta Shopify, paqueterías Shopify, CFDI Shopify. NO usar para Shopify de otros países (es genérico) — este es solo para operación MX.
allowed-tools: Read, Write, Edit
---

# Shopify para mercado mexicano

Shopify por default está optimizado para US/CA. Operar en México requiere ajustes específicos.

## Setup inicial obligatorio

### Moneda y formato
- Moneda principal: **MXN** (no USD aunque tengas tráfico US)
- Formato display: `$1,234.56` con coma para miles
- `Precios con impuestos incluidos`: SÍ (México exige precio total visible)

### Idioma
- Locale: `es-MX` (no `es-ES` — distinto vocabulario)
- Localización de checkout: revisar traducción de "Add to cart" → "Agregar al carrito"
- Términos legales en español obligatorio (PROFECO)

### Información de la tienda
- Razón social completa (no solo nombre comercial)
- RFC del titular
- Domicilio fiscal completo
- Aviso de privacidad LFPDPPP enlazable desde footer (obligatorio)
- Términos y condiciones con políticas de devolución (Art. 92 LFPC)

## Gateways de pago — usar Conekta o MercadoPago

### NO USAR (por default Shopify):
- Shopify Payments (solo US/CA/UK/AU)
- PayPal Standard (cobra 6.95% + tipo de cambio desfavorable)

### USAR (gateways MX):
| Gateway | Tarifa | Cuándo usar |
|---|---|---|
| **Conekta** | 3.6% + $4 + IVA | Default para B2C con TDC + OXXO + SPEI |
| **MercadoPago** | 4.39% + IVA | Si esperas mucho cliente sin TDC (OXXO 25% transacciones MX) |
| **Openpay** | 3.6% + $4 + IVA | Alternativa empresarial |
| **Stripe MX** | 4.5% + $3 MXN | Cross-border MX↔US |

Activar via Shopify > Settings > Payments > Add payment method.

## Paqueterías locales

Shopify por default integra UPS, USPS (US-only). Para MX:

| Paquetería | App Shopify | Cobertura | Precio promedio |
|---|---|---|---|
| **Estafeta** | App Estafeta Shopify | Nacional MX | $120-250 MXN |
| **DHL MX** | App MyDHL Plus | Nacional + internacional | $180-350 MXN |
| **FedEx MX** | App FedEx | Nacional + internacional | $200-400 MXN |
| **paqueteX** (varios) | App Envia.com / Skydropx | Comparador multi-carrier | $100-300 MXN |
| **99 Minutos** | App propia | Same-day CDMX/GDL/MTY | $80-200 MXN |
| **Mercado Envíos** | NO directo (usa ML) | — | — |

Instalar al menos 2: una nacional (Estafeta o DHL) + una para CDMX express (99 Minutos).

## Impuestos (Settings > Taxes)

Configuración México:
- Tax region: México
- Charge tax: SÍ
- Tax inclusive prices: SÍ (precio mostrado YA incluye IVA)
- Tax rate: 16% (general) o 8% (frontera con USA si aplica)

⚠ Productos exentos: medicamentos, libros, alimentos básicos. Configurar por colección con `tax: false`.

## CFDI por venta

Shopify NO emite CFDIs nativos. Opciones:

### Opción A: App de terceros (recomendado)
| App | Costo | Pros | Contras |
|---|---|---|---|
| **Facturama Shopify** | $290 MXN/mes | Integración directa | Sólo Facturama PAC |
| **Bind ERP** | $499 MXN/mes | + ERP completo | Más complejo |
| **B Sale** | $399 MXN/mes | Multi-PAC | Curva aprendizaje |

### Opción B: Webhook → MCP propio
Configurar webhook Shopify `order.created` → endpoint que dispara `mp_facturama_extendido.timbrar_cfdi`. Más control, más trabajo.

### Opción C: CFDI bajo solicitud
Cliente recibe email "factúrame esta compra" → ingresa RFC → emites CFDI manual. Funciona para volumen bajo (< 50 ventas/mes).

⚠ En México todas las ventas requieren CFDI:
- **B2B**: a RFC del comprador
- **B2C**: público general (RFC genérico XAXX010101000) — emisión periódica (mensual)

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
PROFECO obliga aceptar devolución hasta 30 días naturales con producto en buen estado. Configurar política clara en Términos.

### 3. OXXO Pay (Conekta + MercadoPago)
Cliente paga en tienda física. Genera referencia, vence en 3 días. **No marcar orden como pagada hasta confirmar webhook**.

### 4. Tipo de cambio
Si vendes USD pero capturas MXN: usar `mp_banxico` para TC del DOF al momento de la venta. Aviso al cliente.

### 5. Servicio al cliente WhatsApp
Mexicanos prefieren WA sobre email 8:1. Integrar WhatsApp Business con respuestas automáticas para FAQs.

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
      "metodo": "app_facturama",
      "automatico": true,
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

## Validación pendiente

- Comisiones gateways 2026
- Costos paqueterías 2026
- Versión actual Facturama Shopify App
- Cumplimiento LFPDPPP detallado por sección de Shopify
- Testimonios sellers MX Shopify con > 100 ventas/mes

## Ver también

- `mercado-libre-listings` — alternativa marketplace
- `inventario-multicanal` — sincronizar con ML
- `paqueteria-mx` — comparar tarifas
- `mp_shopify_mx` MCP
