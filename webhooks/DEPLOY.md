# Webhook receiver — guía de deployment V2

V1 corre local con `uvicorn`. V2 requiere HTTPS pública para recibir webhooks de Stripe/MP/Conekta/Facturama. Esta guía describe dos opciones probadas: **Railway** (recomendada por simplicidad) y **Cloudflare Workers + Container** (recomendada por costo/edge).

## Pre-requisitos

- Repositorio plugins-mx accesible (privado OK).
- Cuenta del servicio elegido + tarjeta de crédito (típico $5-20 USD/mes).
- Secrets de cada proveedor de webhook ya obtenidos:
  - `STRIPE_WEBHOOK_SECRET` (Stripe Dashboard → Developers → Webhooks)
  - `MERCADOPAGO_WEBHOOK_SECRET` (MP panel → Tu integración → Notificaciones)
  - `CONEKTA_WEBHOOK_SECRET` (Conekta → Settings → Webhooks)
  - `FACTURAMA_API_KEY` (Facturama dashboard)
  - `META_WHATSAPP_VERIFY_TOKEN` + `META_WHATSAPP_APP_SECRET` (Meta Business → WhatsApp → Webhooks)
  - `GITHUB_WEBHOOK_SECRET` (repo Settings → Webhooks)
  - `WEBHOOK_ADMIN_API_KEY` (genera con `python -c 'import secrets; print(secrets.token_urlsafe(32))'`)

---

## Opción A — Railway (recomendada para empezar)

**Por qué Railway**: deploy en <10 min, persistent volume incluido (necesario para `retry_queue.sqlite` y `audit-log/`), $5/mes para empezar.

### Pasos

1. **Conectar repo a Railway**

```bash
# Si no tienes CLI:
npm i -g @railway/cli
railway login

# Desde la raíz del repo:
railway init  # selecciona "deploy from GitHub repo"
```

2. **Configurar servicio Python**

En Railway dashboard → Service Settings:

- **Root directory**: `webhooks/`
- **Build command**: `pip install -e .`
- **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path**: `/health`

3. **Setear variables de entorno**

En Railway → Variables, agregar todos los secrets listados arriba más:

```
PLUGINS_MX_WEBHOOK_DB_PATH=/data/retry_queue.sqlite
PLUGINS_MX_WEBHOOK_AUDIT_DIR=/data/audit-log
PLUGINS_MX_MOCK=0
```

4. **Persistent volume**

Railway → Service → Settings → Volumes → Add Volume mount path `/data`. **Crítico** para que la cola SQLite sobreviva redeploys.

5. **Obtener URL pública**

Railway → Settings → Networking → Generate Domain. Obtendrás algo como:
`https://plugins-mx-webhooks-production.up.railway.app`

6. **Registrar URL en cada proveedor**

| Proveedor | URL endpoint | Eventos |
|---|---|---|
| Stripe | `<base>/webhooks/stripe` | `payment_intent.succeeded`, `charge.refunded`, `invoice.payment_succeeded` |
| Mercado Pago | `<base>/webhooks/mercadopago` | `payment`, `merchant_order`, `subscription_authorized_payment` |
| Conekta | `<base>/webhooks/conekta` | `charge.paid`, `charge.refunded`, `order.paid`, `subscription.*` |
| Facturama | `<base>/webhooks/facturama` | `cfdi.stamped`, `cfdi.cancelled` |
| Meta WhatsApp | `<base>/webhooks/meta_whatsapp` | `messages`, `message_template_status_update` |
| GitHub | `<base>/webhooks/github` | `push`, `pull_request` (en repo Settings → Webhooks) |
| Calendly | `<base>/webhooks/calendly` | `invitee.created`, `invitee.canceled` |
| Typeform | `<base>/webhooks/typeform` | `form_response` |
| Mercado Libre | `<base>/webhooks/mercadolibre` | `orders_v2`, `payments`, `questions`, `items` |

7. **Activar worker de retry queue** (V2)

El worker corre como segundo proceso. En Railway, opción A: agregar segundo servicio que comparte el mismo repo y volume:

- **Start command**: `python -c "from app.retry_queue import RetryQueue, QueueWorker; from app.handlers.dispatch import dispatch; QueueWorker(RetryQueue(), dispatch_fn=dispatch).run_forever()"`
- Mismo volume mount `/data`.
- No expone puerto público.

Opción B (más simple para empezar): correr el worker como background task del FastAPI con `app.on_event("startup")`. Tradeoff: si falla el worker, el servicio sigue arriba sin reintentos.

8. **Smoke test**

```bash
curl -X POST https://tu-app.up.railway.app/webhooks/stripe \
  -H 'content-type: application/json' \
  -H 'stripe-signature: t=123,v1=foo' \
  -d '{"id":"evt_test_001","type":"payment_intent.succeeded","data":{"object":{"amount_received":12345}}}'

# Verificar en admin:
curl https://tu-app.up.railway.app/webhooks/recent \
  -H "x-api-key: $WEBHOOK_ADMIN_API_KEY"
```

### Costo estimado

- Servicio web (FastAPI): $5-10/mes
- Worker secundario: $5/mes (si lo separas)
- Volumen 1GB: incluido en plan starter
- **Total: ~$10-15 USD/mes** para empezar.

---

## Opción B — Cloudflare Workers + Container (edge)

**Por qué Cloudflare**: latencia global mejor (POPs near origin del proveedor), $0 para los primeros 100k requests/día, container Workers ahora soporta Python via Pyodide.

### Limitación importante

Cloudflare Workers Python **NO soporta SQLite local persistente**. Para usar este path necesitas reemplazar `RetryQueue` con:

- **Cloudflare D1** (SQLite serverless de CF) — recomendado, API casi idéntica.
- O **Cloudflare KV** + **Queue** para los reintentos.

### Pasos resumidos

1. `wrangler init webhooks-cf`
2. Adaptar `app/main.py` a entry point `worker.py` con Cloudflare bindings.
3. Migrar `retry_queue.py` a D1: cambiar conexión `sqlite3.connect` por `env.DB`.
4. Setear secrets con `wrangler secret put STRIPE_WEBHOOK_SECRET ...` (12 secrets).
5. Deploy: `wrangler deploy`.
6. Registrar URL en cada proveedor.

### Costo estimado

- Worker request: gratuito hasta 100k/día (suficiente para PyMEs).
- D1: gratuito hasta 5M reads/día.
- **Total: $0 USD/mes para empezar** si volumen <100k webhooks/día.

### Tradeoff vs Railway

| Aspecto | Railway | Cloudflare |
|---|---|---|
| Setup inicial | 15 min | 60-90 min (port a CF) |
| SQLite local | ✅ | ❌ (usar D1) |
| Costo $0 inicial | ❌ | ✅ |
| Worker background | Servicio separado | Built-in Queues |
| Adopción del equipo | Simple | Curva mayor |

**Recomendación**: empezar con Railway, migrar a CF cuando el costo justifique (>500 webhooks/día sostenidos).

---

## V2.1 — Monitoreo (opcional)

Una vez en producción:

- **Logs**: integrar con Sentry para errores del worker (`pip install sentry-sdk`).
- **Métricas**: endpoint `/webhooks/stats` ya expone counts; loggear con Grafana Cloud free tier.
- **Alertas**: si `dead_letter_unresolved > 5`, mandar mensaje a Slack/Discord (skill `slack:slack-messaging`).

## Rollback rápido

Si V2 falla en producción:

```bash
railway down                      # apaga el servicio
# Los webhooks rebotan con 503; los proveedores reintentan
railway up --previous-deployment  # vuelve a la versión anterior
```

Stripe, MP y Conekta reintentan automáticamente. Facturama y Meta WA NO reintentan — esos eventos se pierden si V2 está caído.

---

## Estado a 2026-06-12

| Componente V2 | Estado |
|---|---|
| `app/retry_queue.py` (SQLite + backoff + dead-letter) | ✅ codificado |
| Tests `test_retry_queue.py` (13 casos) | ✅ pasando |
| Esta guía de deploy | ✅ |
| Deploy real Railway/Cloudflare | ⏳ requiere humano + cuenta + secrets |
| Worker corriendo en producción | ⏳ requiere deploy |
| Integración con workflows ejecutables del repo | ⏳ requiere wiring entre handler.dispatch → Workflow skill |
| Alertas dead-letter | ⏳ V2.1 |
