---
spec: "webhook-receiver"
estado: "DRAFT"
creado: "2026-06-11"
autor: "Elías Rashid Morales Mendoza"
ultima_actualizacion: "2026-06-11"
esfuerzo_estimado_horas: [100, 180]
prioridad: "tier-1"
---

# Spec 01 — Webhook receiver + 12 handlers

## 1. Propósito

Permitir que el monorepo reciba **webhooks entrantes** de servicios externos (Stripe, Mercado Pago, Conekta, Facturama, Meta WhatsApp, GitHub, Calendly, Typeform, ML, Banxico, IMSS, CONDUSEF) y los **dispare a workflows del plugins-mx** (ej. webhook MP pagado → emitir CFDI + notificar cliente).

Sin esto los workflows existentes son **manuales** — el usuario debe invocar `/core:conciliar-pago` cuando recibe el pago. Con webhook receiver es **automático**.

## 2. Contexto y por qué es novedoso

- **Lo que existe**: validación de firma HMAC dentro de MCPs (`mp_mercado_pago.validate_webhook`, `mp_conekta.conekta_validate_webhook`). Estos son **componentes de validación**, no receivers HTTP públicos.
- **Por qué es novedoso**: ningún componente del repo actualmente expone HTTPS público para recibir POSTs. Toda comunicación es Claude Code → MCP (stdin/stdout JSON-RPC), no servicios externos → repo.
- **Referencia plan original**: sección 10.3 "Webhooks Inbound" lista 12 handlers.

## 3. Alcance

**Dentro:**
- Servidor HTTP público (1 endpoint genérico `/webhooks/<source>`)
- Validación de firma por servicio (delegada a los MCPs existentes)
- Idempotencia (deduplicate por `(source, event_id)`)
- Dispatch a handler específico → invoca workflow del repo
- Bitácora append-only de todo webhook recibido (hashed sensitive data)
- Retry queue para handlers que fallan

**Fuera (decisión deliberada):**
- Dashboard UI de webhooks (texto/CLI only por ahora)
- Webhooks **outbound** (sólo inbound — los outbound los hacen los MCPs)
- Authentication mutual TLS (HMAC firma del payload es suficiente para los 12 servicios)
- Scaling distribuido (1 instancia OK hasta ~10k webhooks/día)

## 4. Inputs / outputs / schemas

### Endpoint genérico

```
POST https://<deployment>/webhooks/<source>
Headers:
  - <source>-Signature: ...      (validación HMAC)
  - X-Webhook-Event-Id: ...      (idempotencia)
Body: JSON propio del servicio
```

### Respuesta

```
200 OK              → handler aceptó, encolará al workflow
202 Accepted        → recibido + en cola para procesar
401 Unauthorized    → firma inválida
409 Conflict        → ya procesado (idempotencia)
500                 → error interno (servicio reintenta)
```

### Handler interno (schema)

```python
class WebhookEvent(BaseModel):
    source: Literal["stripe", "mercadopago", "conekta", "facturama",
                    "meta_whatsapp", "github", "calendly", "typeform",
                    "mercadolibre", "banxico_cep", "imss_buzon", "condusef"]
    event_id: str  # idempotency key
    event_type: str
    timestamp: datetime
    payload: dict  # raw body
    signature_valid: bool
    received_at: datetime
```

## 5. Tools / endpoints / triggers expuestos

| Endpoint | Auth | Acción |
|---|---|---|
| `POST /webhooks/stripe` | Stripe-Signature HMAC | Dispatch a handler stripe |
| `POST /webhooks/mercadopago` | x-signature MP | Idem |
| `POST /webhooks/conekta` | Digest / conekta-signature | Idem |
| `POST /webhooks/facturama` | Bearer + IP allowlist | Idem |
| `POST /webhooks/meta-whatsapp` | x-hub-signature-256 | Idem |
| `POST /webhooks/github` | x-hub-signature-256 | Idem |
| `POST /webhooks/calendly` | calendly-webhook-signature | Idem |
| `POST /webhooks/typeform` | typeform-signature | Idem |
| `POST /webhooks/mercadolibre` | x-tracking-id + IP allowlist | Idem |
| `POST /webhooks/banxico-cep` | (delegado a Banxico) | Idem |
| `POST /webhooks/imss-buzon` | (manual trigger) | Idem |
| `POST /webhooks/condusef` | (manual trigger) | Idem |
| `GET /webhooks/health` | — | Liveness probe |
| `GET /webhooks/recent?source=X` | API key admin | Audit log últimos 100 |

## 6. Casos edge

| Caso | Comportamiento |
|---|---|
| Firma inválida | 401 + log + NO procesar (anti-spoofing) |
| Event ID repetido | 409 + log (idempotencia) |
| Payload sin event_id | Generar hash(payload + ts) como event_id |
| Handler downstream falla | Encolar retry con backoff exponencial (3 intentos máx) |
| Body > 1MB | 413 Payload Too Large |
| Servicio reintenta porque devolvimos 5xx | Devolver 200 si ya está en queue |
| Source no soportado | 404 + log (puede ser typo) |
| Timestamp > 5 min anterior (replay) | 401 Reject |

## 7. Dependencias

- **Librerías nuevas**: `fastapi`, `uvicorn`, `python-multipart` (~3 deps)
- **MCPs**: `mp_mercado_pago`, `mp_conekta`, `mp_facturama_extendido`, `mp_mercado_libre`, `mp_banxico_cep` (validación firma)
- **Workflows**: invoca `workflow-pago-conciliacion`, `workflow-cfdi-emision-completa`, etc.
- **Deployment**: Cloudflare Workers (recomendado por gratis hasta 100k req/día) o FastAPI + uvicorn en VPS
- **Storage idempotencia**: SQLite local (≤10k webhooks) o Cloudflare KV

## 8. Criterios de aceptación

- [ ] `POST /webhooks/stripe` con firma válida → 200, log entry, queue dispatch
- [ ] `POST /webhooks/stripe` con firma inválida → 401, log entry sin dispatch
- [ ] Mismo event_id 2 veces → segundo recibe 409
- [ ] Test contra 6 servicios principales con payloads de ejemplo
- [ ] Retry queue procesa handler caído cuando vuelve
- [ ] Health endpoint responde 200 con MCPs status
- [ ] Logs hashean RFC, email, payment_id si están en payload
- [ ] Deployment a Cloudflare Workers funciona (smoke test)
- [ ] Docs `docs/webhooks-setup.md` con setup paso a paso

## 9. Esfuerzo estimado

- **Diseño + setup FastAPI/Workers**: 15-25h
- **Receiver genérico + idempotencia**: 20-30h
- **12 handlers (delegación a workflows existentes)**: 40-60h (~3-5h/handler)
- **Retry queue + dead letter**: 10-20h
- **Tests + fixtures**: 15-25h
- **Deployment + docs**: 10-20h
- **TOTAL**: **100-180 horas** (~3-5 semanas FT)

## 10. Riesgos + mitigaciones

| Riesgo | Prob | Impacto | Mitigación |
|---|---|---|---|
| Servicios cambian firma HMAC sin avisar | Baja | Alto | Cada validador en su MCP — fácil ajustar |
| Replay attacks | Media | Alto | Validar timestamp + ventana 5min |
| Spike de tráfico mata el receiver | Baja | Medio | Cloudflare Workers auto-scaling |
| Handler downstream lento (timbrado PAC) | Alta | Medio | Async queue, no bloquear receiver |
| URL pública expuesta = riesgo seguridad | Media | Alto | HMAC obligatorio + IP allowlist donde posible |
| Costo Cloudflare/VPS no controlado | Baja | Bajo | Free tier suficiente para volumen actual |

## 11. Decisiones pendientes

- [ ] ¿Cloudflare Workers (sin estado, escala automática) o VPS con FastAPI (más control)?
- [ ] ¿Idempotency storage: SQLite local, Cloudflare KV, o Redis?
- [ ] ¿Retries síncronos o async via cola?
- [ ] ¿Cómo notificar al usuario cuando handler falla 3 veces? (¿WhatsApp?)
- [ ] ¿Domain personalizado o `workers.dev` para empezar?

## 12. Plan de implementación

### Fase 1: Foundation (15-25h)
1. Elegir entre Cloudflare Workers o FastAPI (recomendado: Workers para empezar)
2. Setup proyecto `webhooks/` aparte del monorepo (deploy independiente)
3. Endpoint health + estructura de routes
4. Logger + idempotency storage stub

### Fase 2: Receiver genérico (20-30h)
1. `POST /webhooks/<source>` con dispatch table
2. Validación de firma delegada a MCPs (importar shared logic)
3. Idempotency check
4. Queue stub (in-memory primero)
5. Tests para los 3 endpoints más usados (MP, Conekta, Facturama)

### Fase 3: 12 handlers (40-60h)
1. Stripe → `workflow-pago-conciliacion`
2. MP → `workflow-pago-conciliacion`
3. Conekta → `workflow-pago-conciliacion`
4. Facturama → notificación CFDI timbrado
5. Meta WhatsApp → log + posible respuesta automática
6. GitHub → re-sync `_shared/` (CI-style)
7. Calendly → onboarding
8. Typeform → onboarding
9. ML → procesar orden nueva
10. Banxico CEP → marcar pago cobrado
11. IMSS Buzón → alertar usuario
12. CONDUSEF → respuesta requerida

### Fase 4: Production hardening (10-20h)
1. Retry queue con backoff
2. Dead letter queue
3. Rate limiting básico
4. Metrics endpoint

### Fase 5: Docs + deployment (10-20h)
1. `docs/webhooks-setup.md`
2. `.env.example` con secrets necesarios
3. Deployment guide (Cloudflare Workers)
4. Update `STATUS.md`

## 13. Links

- Plan original: `/Users/elias/Downloads/plugins-mx-planeacion-mcps-agentica.md` sección 10.3
- MCPs validación firma existentes: `mp_mercado_pago/webhooks.py`, `mp_conekta/webhooks.py`
- Stripe webhook docs: https://stripe.com/docs/webhooks
- Mercado Pago webhook docs: https://www.mercadopago.com.mx/developers/es/docs/notifications/webhooks
- Cloudflare Workers: https://developers.cloudflare.com/workers/
