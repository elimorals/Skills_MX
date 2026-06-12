# mp_conekta — MCP para Conekta (pasarela de pagos MX)

Conecta con la pasarela de pagos Conekta para crear órdenes, charges (TDC + OXXO Pay + SPEI), customers, payment links y suscripciones. Útil como **alternativa a Mercado Pago** cuando se requiere flujo OXXO/SPEI nativo o tarifas distintas.

## Tools (13)

### Órdenes
| Tool | Propósito | Mock |
|---|---|---|
| `conekta_create_order` | Crear orden con line items | Sí |
| `conekta_get_order` | Leer orden por ID (cache 2 min) | Sí |
| `conekta_list_orders` | Listar órdenes con cursor + filtros | Sí |

### Charges
| Tool | Propósito | Mock |
|---|---|---|
| `conekta_create_charge_on_order` | Charge card/oxxo/spei sobre orden | Sí |
| `conekta_refund_order` | Refund total o parcial | Sí |

### Customers
| Tool | Propósito | Mock |
|---|---|---|
| `conekta_create_customer` | Crear customer reutilizable | Sí |
| `conekta_get_customer` | Leer customer por ID (cache 15 min) | Sí |

### Payment Links
| Tool | Propósito | Mock |
|---|---|---|
| `conekta_create_payment_link` | Crear Checkout Link hospedado | Sí |

### Suscripciones
| Tool | Propósito | Mock |
|---|---|---|
| `conekta_subscription_create` | Suscripción del customer a un plan | Sí |
| `conekta_subscription_update` | Cambiar plan o tarjeta de suscripción | Sí |
| `conekta_subscription_cancel` | Cancelar suscripción | Sí |

### Webhooks
| Tool | Propósito | Mock |
|---|---|---|
| `conekta_validate_webhook` | Verificar firma HMAC (Digest o conekta-signature) | N/A (validación local) |

### Discovery
| Tool | Propósito |
|---|---|
| `conekta_listar_catalogos` | Status orden/charge, métodos pago, decline codes, eventos webhook |

## Configuración

| Variable | Propósito |
|---|---|
| `CONEKTA_API_KEY` | API key (sandbox: `key_test_*`, producción: `key_live_*`) |
| `CONEKTA_WEBHOOK_SECRET` | Secret para validar firmas de webhooks |
| `PLUGINS_MX_MOCK=1` | Forzar mock (override de credenciales) |

Sin `CONEKTA_API_KEY` → modo mock automático.

## Convención de precios

⚠ **Conekta usa CENTAVOS enteros, no decimales**. Ejemplos:
- $1.00 MXN → `100`
- $100.50 MXN → `10050`
- $1,500.00 MXN → `150000`

Los `unit_price` y `amount` en todos los tools son enteros.

## Detección sandbox vs producción

Se determina automáticamente por el prefijo de `CONEKTA_API_KEY`:
- `key_test_*` o cualquier key con "test" → **sandbox**
- `key_live_*` o `key_*` → **producción**
- Ausente → **mock**

`client.environment` retorna el modo activo.

## Webhooks: validación de firma

Conekta soporta dos formatos según versión de cuenta:

1. **`Digest: SHA256=<base64>`** (formato legacy)
2. **`conekta-signature: t=<ts>,v1=<hmac_hex>`** (formato moderno tipo Stripe)

El tool `conekta_validate_webhook` detecta ambos automáticamente:

```python
result = conekta_validate_webhook(
    headers={"Digest": "SHA256=..."},  # o {"conekta-signature": "t=...,v1=..."}
    payload='{"event":"charge.paid",...}',  # body crudo
    secret=os.environ["CONEKTA_WEBHOOK_SECRET"],
    max_age_seconds=300,  # anti-replay
)
if not result["valid"]:
    raise HTTPError(401)
```

## Casos de uso típicos

### 1. Pago único con OXXO
```python
order = await conekta_create_order(
    line_items=[{"name": "Curso", "unit_price": 199900, "quantity": 1}],
    currency="MXN",
    customer_info={"name": "...", "email": "..."},
    charges=[{"type": "oxxo_cash"}],
)
# order["charges"]["data"][0]["payment_method"]["reference"] = "9320XXXXXXXX"
```

### 2. Payment link para WhatsApp
```python
link = await conekta_create_payment_link(
    name="Asesoría 1 hr",
    amount=80000,  # $800 MXN
    currency="MXN",
    expires_at=int(time.time()) + 86400,  # 24 hrs
)
# link["url"] = https://pay.conekta.com/link/chk_xyz → mandar por WA
```

### 3. Suscripción mensual
```python
cliente = await conekta_create_customer(name="...", email="...")
sub = await conekta_subscription_create(
    customer_id=cliente["id"],
    plan_id="plan_consultoria_mensual",
)
```

## Tests

```bash
cd /Users/elias/Documents/Trabajo/skills/mcp-servers
.venv/bin/python -m pytest mp_conekta/tests/ -q
```
