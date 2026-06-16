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
