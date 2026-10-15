# Integración con pasarelas de pago

**Propósito**: cómo conectar Stripe, Mercado Pago, Conekta para cobros.

**Audiencia**: desarrolladores activando cobranza.

**Pre-lectura**: [seguridad.md](../architecture/seguridad.md).

---

## Opciones de pasarela en México

| Pasarela | Setup | Costo | Métodos soportados | Recomendado para |
|---|---|---|---|---|
| **Stripe** | Medio | 3.6% + $3 MXN | TDC, TDD, OXXO, SPEI | Plataformas internacionales |
| **Mercado Pago** | Fácil | 3.49% + $4 MXN | TDC, TDD, Mercado Pago | LATAM, B2C, ecommerce |
| **Conekta** | Medio | 2.9% + $2 MXN | TDC, OXXO, SPEI | PyMEs MX, B2C/B2B |
| **OpenPay** | Medio | 3.5% + $2.50 MXN | TDC, OXXO, SPEI | Enterprise MX (BBVA) |
| **Kueski Pay** | Medio | 4-7% | BNPL (compra ahora paga después) | Ecommerce alto AOV |

---

## Setup con Stripe

### 1. Cuenta

https://dashboard.stripe.com/register

### 2. Modo test vs live

Stripe se conecta con su MCP oficial `@stripe/mcp` (vía `npx`), que `freelancers-mx`, `colegios-mx` y `talleres-mx` declaran deshabilitado por defecto. Stripe tiene API keys separadas para test (sk_test_) y producción (sk_live_).

### 3. `.env`

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_ACCOUNT_COUNTRY=MX
```

### 4. Activar MCP

```json
{
  "stripe": {
    "command": "npx",
    "args": ["-y", "@stripe/mcp", "--tools=all"],
    "env": {
      "STRIPE_SECRET_KEY": "${STRIPE_SECRET_KEY:-}"
    },
    "disabled": false
  }
}
```

### 5. Primer payment link

```
Usuario: "Genera link de pago de $5,800 MXN para la cotización CT-1234
        del cliente Bimbo."

Claude → invoca Stripe MCP
        Crea Payment Link con descripción "Cotización CT-1234"
        Devuelve URL: https://buy.stripe.com/...
        Tú la mandas al cliente vía WA o email.
```

---

## Setup con Mercado Pago

### 1. Cuenta de desarrollador

https://www.mercadopago.com.mx/developers

### 2. Crear aplicación

Panel → Tus integraciones → Crear aplicación

### 3. Obtener credenciales

Cada app tiene:
- Public key (cliente)
- Access token (servidor)
- Para sandbox: `TEST-...`
- Para producción: `APP_USR-...`

### 4. `.env`

```bash
MERCADOPAGO_ACCESS_TOKEN=TEST-...
MERCADOPAGO_PUBLIC_KEY=TEST-...
MERCADOPAGO_WEBHOOK_SECRET=...
```

### 5. MCP

El repo incluye **`mp_mercado_pago`** (links de pago, validación HMAC de webhooks, reembolsos y cancelaciones), ya declarado en `core-mexico/.mcp.json`. Lee `MERCADOPAGO_ACCESS_TOKEN`. Sin token responde datos de ejemplo marcados `simulated: true`; con token, los errores de la API se propagan. Configuración en `mcp-servers/mp_mercado_pago/example.mcp.json`; estado en [`mcp-servers/CATALOGO.md`](../../mcp-servers/CATALOGO.md).

---

## Setup con Conekta

El repo incluye **`mp_conekta`** (órdenes, cargos con tarjeta, OXXO y SPEI, reembolsos, clientes, links de pago, suscripciones y validación HMAC de webhooks), declarado en `core-mexico/.mcp.json`.

```bash
CONEKTA_API_KEY=key_test_xxxxxxxx
CONEKTA_WEBHOOK_SECRET=tu_webhook_secret
```

Mismo comportamiento: sin llave, datos de ejemplo `simulated: true`; con llave, consulta real sin fallback silencioso. Ver `mcp-servers/mp_conekta/README.md`.

---

## Webhooks: cómo confirmar pagos

Toda pasarela usa webhooks para notificar eventos (pago recibido, refund, dispute).

### Estructura recomendada

```
1. Pasarela envía POST a tu webhook URL
2. Tu servidor:
   a. Valida firma del webhook (HMAC, etc.)
   b. Identifica el evento (payment.created, payment.refunded)
   c. Actualiza tu sistema interno
   d. Si es pago confirmado: dispara CFDI (con cfdi-emision)
   e. Si es refund: dispara CFDI de Egreso (nota de crédito)
3. Responder 200 OK a la pasarela
```

### Receptor incluido

`webhooks/` es un receptor FastAPI con handlers para Stripe, Mercado Pago, Conekta, Facturama, Mercado Libre, WhatsApp (Meta) y otros: validación HMAC o Bearer, allowlist, idempotencia y bitácora JSONL. Ver [`webhooks/README.md`](../../webhooks/README.md).

### URL pública necesaria

Para recibir webhooks necesitas URL pública. Opciones:
- El receptor de `webhooks/` desplegado (ver `webhooks/DEPLOY.md`)
- Webhook receiver propio (cloud function, lambda, server)
- Servicio tipo Pipedream / Make / Zapier
- Tunneling para desarrollo: ngrok, Cloudflare Tunnel

---

## Flujo: cobro + CFDI atómico

Este es el patrón que automatiza el plugin:

```
1. Generar cotización con /freelancers:cotizar
2. Si cliente acepta, crear Payment Link/Preference
3. Mandar link al cliente
4. Cliente paga → webhook recibido
5. Webhook dispara CFDI:
   - Lee preferencia para obtener datos
   - Invoca cfdi-emision con MétodoPago=PUE, FormaPago=04 (tarjeta) o 03 (SPEI)
   - Timbra
   - Manda XML+PDF al cliente vía WA
6. Bitácora se actualiza con folio fiscal
```

---

## Manejo de saldos a favor / refunds

Si hay refund parcial o total:

```
1. Pasarela envía webhook payment.refunded
2. Skill construye CFDI tipo E (Egreso) - nota de crédito
3. TipoRelacion 01, vinculado al CFDI original
4. UsoCFDI G02 (devoluciones, descuentos o bonificaciones)
5. Importe del refund con su IVA
6. Timbra y guarda
```

Sin esta nota de crédito, la contabilidad del emisor queda con ingreso fantasma.

---

## Compliance de cobranza con tarjeta (PCI)

### Lo que NO debes hacer
- Almacenar datos de tarjeta (número, CVV) en tu base
- Procesar pagos sin PCI compliance
- Loggear datos sensibles

### Lo que la pasarela hace por ti
- Stripe / MP / Conekta son PCI Level 1
- Te dan APIs que NUNCA tocan los datos sensibles del cliente
- El cliente ingresa datos directo en pasarela (hosted page, Stripe Elements, etc.)

### Tu responsabilidad
- HTTPS en todas las URLs que muestran el botón de pago
- Validar firmas de webhooks
- No exponer tu API key del lado del cliente (solo la public key)

---

## CFDI por cobros (forma de pago)

| Forma de pago real | Clave `c_FormaPago` |
|---|---|
| Tarjeta crédito | 04 |
| Tarjeta débito | 28 |
| Tarjeta servicios | 29 |
| Efectivo | 01 |
| Transferencia SPEI | 03 |
| Cheque nominativo | 02 |
| Monedero electrónico | 05 |
| OXXO (efectivo en convenio) | 01 |
| BNPL Kueski/Mercado Crédito | 99 si financiado, 03/04 según cómo te lo paguen |

El skill `cfdi-emision` mapea correctamente con base en lo que la pasarela reporta.

---

## Pricing comparativo (PyME promedio)

### Volumen bajo (10-50 cobros/mes)
- Total cobrado: $50k-$200k MXN
- Comisiones Stripe: $1.5k-$6k MXN
- Comisiones MP: $1.5k-$7k MXN
- Comisiones Conekta: $1.2k-$5k MXN

### Volumen medio (100-500 cobros/mes)
- Total cobrado: $200k-$1M MXN
- Comisiones: 2-3% del total
- Negociable con pasarela si volumen es estable

### Volumen alto (1000+ cobros/mes)
- Negociar pricing custom
- Considerar OpenPay/Stripe enterprise

---

## Ver también

- `_shared/cfdi-emision/SKILL.md` — emisión de CFDI al cobrar
- [integracion-pac.md](integracion-pac.md) — timbrado del CFDI
- [seguridad.md](../architecture/seguridad.md) — manejo de credenciales pasarela
- [glosario-fiscal-mx.md](../reference/glosario-fiscal-mx.md) — términos forma/método de pago
