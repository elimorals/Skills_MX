# Integración con pasarelas de pago

**Propósito**: cómo conectar Stripe, Mercado Pago, Conekta para cobros.

**Audiencia**: desarrolladores activando cobranza.

**Pre-lectura**: [seguridad.md](seguridad.md).

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

Stripe tiene API keys separadas para test (sk_test_) y producción (sk_live_).

### 3. `.env`

```bash
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_ACCOUNT_COUNTRY=MX
```

### 4. Activar MCP

```json
{
  "stripe": {
    "command": "npx",
    "args": ["-y", "@stripe/mcp-server"],
    "env": {
      "STRIPE_API_KEY": "${STRIPE_API_KEY}"
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

### 5. MCP custom (no hay oficial al cierre del entrenamiento)

```python
# mcp-servers/mercado-pago.py
import os
import httpx
from fastmcp import FastMCP

mcp = FastMCP("mercado-pago")
TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
BASE_URL = "https://api.mercadopago.com"

@mcp.tool()
async def create_preference(
    items: list,
    payer_email: str = None,
    external_reference: str = None,
) -> dict:
    """Crea preferencia de pago (Checkout Pro).
    
    Args:
        items: lista de dicts {title, quantity, unit_price, currency_id}
        payer_email: email del pagador (opcional)
        external_reference: tu ID interno para tracking
    """
    body = {
        "items": items,
        "external_reference": external_reference,
    }
    if payer_email:
        body["payer"] = {"email": payer_email}
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/checkout/preferences",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json=body,
        )
        data = resp.json()
        return {
            "preference_id": data["id"],
            "init_point": data["init_point"],  # URL para pago producción
            "sandbox_init_point": data["sandbox_init_point"],
        }

@mcp.tool()
async def get_payment(payment_id: str) -> dict:
    """Consulta estado de un pago específico."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {TOKEN}"},
        )
        return resp.json()
```

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

### URL pública necesaria

Para recibir webhooks necesitas URL pública. Opciones:
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
- [seguridad.md](seguridad.md) — manejo de credenciales pasarela
- [glosario-fiscal-mx.md](glosario-fiscal-mx.md) — términos forma/método de pago
