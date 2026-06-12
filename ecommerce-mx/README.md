# ecommerce-mx

Plugin para vendedores online en México que operan en uno o más marketplaces (Mercado Libre, Shopify, Amazon MX) + canales propios.

## Casos de uso

- **Seller Mercado Libre**: optimizar listings, mantener reputación, pricing competitivo vs comisión 13-17%
- **Tienda Shopify MX**: gestionar productos, fulfillment con paqueterías locales, CFDI por venta
- **Omnichannel** (varios canales): sincronizar inventario para no vender más de lo que tienes
- **Dropshipping/reventa**: pricing dinámico considerando margen + comisión + envío

## Skills incluidos (5 propios + 6 heredados de core-mexico)

### Propios del vertical
| Skill | Cuándo se activa |
|---|---|
| `mercado-libre-listings` | Crear, actualizar, pausar listings ML con criterio MX (categorías, garantías, envío gratis ML) |
| `mercado-libre-pricing` | Calcular precio óptimo considerando comisión ML, margen y precio competidores |
| `shopify-mx` | Configuración Shopify específica MX (CFDI, paqueterías locales, MercadoPago/Conekta) |
| `inventario-multicanal` | Sincronizar stock entre ML + Shopify + Amazon + tienda física |
| `paqueteria-mx` | Cotizar envío con Estafeta, DHL MX, FedEx MX, paqueteX según peso/dimensión/destino |

### Heredados de core-mexico
- `cfdi-emision` — emitir CFDI por cada venta (B2C global o B2B con datos del cliente)
- `iva-retenciones-mx` — IVA trasladado en cada venta + retenciones si aplica
- `rfc-validacion` — validar RFC del cliente en checkout B2B
- `whatsapp-business-mx` — confirmación de orden, tracking de envío, post-venta
- `compliance-lfpdppp` — aviso de privacidad para tienda en línea
- `mxn-formato` — formato de precios en peso mexicano

## Comandos slash

```
/ecommerce:sync-inventario       # sincroniza stock entre todos los canales
/ecommerce:optimizar-pricing     # recalcula precios ML/Shopify según comisión y competencia
/ecommerce:publicar-listing      # publica producto nuevo en todos los marketplaces
/ecommerce:cotizar-envio         # cotiza envío en 4 paqueterías
/ecommerce:cierre-ventas         # cierre del día/mes: ventas + CFDIs + inventario
```

## MCPs requeridos

Configurados en `.mcp.json`:
- `core-mexico` (heredado): banxico, facturama, mercadopago, conekta, sat_portal
- Propios: `mp_mercado_libre`, `mp_shopify_mx` (Tier B), `mp_amazon_mx_seller` (futuro)

## Setup

1. Instalar plugin: incluido en monorepo `plugins-mx`
2. Heredar `core-mexico` (declarado en `compatibility.requires`)
3. Configurar credenciales en `.env`:
   ```bash
   ML_APP_ID=...
   ML_SECRET=...
   ML_REFRESH_TOKEN=...
   SHOPIFY_SHOP=tienda.myshopify.com
   SHOPIFY_ACCESS_TOKEN=...
   ```
4. Sin credenciales corre en mock con datos demo

## Estado actual

⚠ **Scaffolding (v0.1.0)** — skills lint-passing pero no validados con seller MX real. Score honesto promedio estimado: 4.5/9 (ver `docs/estado-real.md` cuando se actualice para este vertical).

## Validaciones pendientes para producción

- Validar reglas Mercado Libre 2026 (categorías, políticas, comisiones)
- Confirmar APIs Shopify Plus vs Shopify Standard (algunas tools solo Plus)
- Validar tarifas paqueterías 2026 (Estafeta, DHL MX, FedEx MX)
- Testimonios de al menos 1 seller MX operando
- Casos edge con devoluciones cross-marketplace

## Ver también

- `docs/roadmap.md` Q4 2026
- `mcp-servers/mp_mercado_libre/README.md`
- `core-mexico/README.md`
