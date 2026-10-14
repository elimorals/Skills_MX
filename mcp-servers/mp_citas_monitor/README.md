# mp_citas_monitor

Monitor **ético** de cupos para citas gob.mx — alterna al mercado negro $1,000 MXN/cita.

## Diferenciador clave

| Mercado negro | mp_citas_monitor |
|---|---|
| Acapara y revende | Alerta al titular, no reserva |
| Polling ~5s | Throttling mínimo 60s |
| Sin consentimiento | `consent_token` vinculado a CURP |
| Sin trazabilidad | Bitácora hasheada LFPDPPP |
| $1,000 MXN/cita | $99-149 MXN/mes max |

## Portales soportados

| Clave | Portal | Trámites |
|---|---|---|
| `sat_citas` | citas.sat.gob.mx | e.firma renov/nueva, RFC, CSF, devoluciones |
| `imss_citas` | citas.imss.gob.mx | pensión, NSS, aclaración semanas |
| `sre_mexitel` | citas.sre.gob.mx | pasaporte, doble nacionalidad |
| `ine_modulos` | ine.mx | credencial reposición, cambio domicilio |

## Tools

- `citas_listar_portales()` — catálogo + compromiso ético
- `citas_generar_consent_token(curp, portal, tramite)` — token LFPDPPP del titular
- `citas_crear_alerta(token, canal, destinatario)` — whatsapp/email/sms/webhook
- `citas_revisar_cupos(portal, tramite)` — read-only, sin titular
- `citas_estadisticas_eticas()` — métricas auditoría

## Modelo comercial

- B2C: $99-149 MXN/mes por alerta vinculada a un CURP
- Si en 30 días no se conseguía cita, reembolso 100%
- Uso indebido detectado → reporte a PFDC + cancelación inmediata

## Estado real

**Handoff humano** en los 4 portales; salvaguardas éticas intactas (`consent_token` del
titular, throttling ≥ 60 s, sin auto-reserva). Revisado en vivo 2026-10-14 (5 s entre hosts):

| Portal | Resultado | Bloqueo |
|---|---|---|
| citas.sat.gob.mx | 200 (SPA Angular) | Al elegir "Registrar cita", `GET /api/account` → 401: la agenda exige sesión del titular |
| citas.sre.gob.mx | 200 → `validate.perfdrive.com` | Radware Captcha Page |
| citas.imss.gob.mx | sin DNS | La URL del catálogo no existe; por confirmar con IMSS |
| www.ine.mx/credencial | 200 | Página informativa; la cita la agenda el titular |

- `citas_revisar_cupos` fuera de mock devuelve `tiene_cupos: null` + handoff con el bloqueo
  verificado. Para SAT añade `alternativas_digitales`, leídas en vivo del JSON público
  `https://citas.sat.gob.mx/content/json/tc_menu.json` (200, 1.9 KB, 2026-10-14): los trámites que
  el SAT pide hacer en línea antes de buscar cita.
- `citas_crear_alerta` ya no inventa `alerta_id` "activa": devuelve la especificación con
  `persistida: false`.
- Mock solo con `PLUGINS_MX_MOCK=1`. Live: `PLUGINS_MX_LIVE=1 pytest mp_citas_monitor -k live`.
