# mp_portales_monitor

Monitor continuo de **25+ portales gob.mx críticos** (federales, estatales, municipales).

**Comprador objetivo**: estados con bajo presupuesto IT (Oaxaca, Chiapas, Guerrero, Tabasco) + dependencias federales sin capacidad de monitoreo SRE.

## Universo

| Categoría | Portales monitoreados |
|---|---|
| Federal fiscal | SAT padrón, Verifica CFDI |
| Federal laboral | IMSS IDSE, IMSS semanas, STPS REPSE |
| Federal identidad | RENAPO, INE, Llave MX |
| Federal consumidor | REPEP, Buró Comercial |
| Federal vivienda | INFONAVIT Mi Cuenta |
| Estatal CDMX | SAF Finanzas, SEMOVI |
| Estatal | CDMX, EdoMex, NL, JAL, QRO, YUC, BC |
| Municipal | Monterrey, Guadalajara (Visor Urbano) |

## Tools

- `portales_listar(categoria?)` — lista filtrable
- `portales_check_http(clave)` — HEAD/GET con latencia + SLA
- `portales_check_form_render(clave, selector)` — Playwright opt-in (verifica selector clave)
- `portales_health_dashboard()` — agregado por categoría
- `portales_configurar_alerta(clave, canal, destinatario)` — whatsapp/email/slack/pagerduty

## Modelo comercial

**Licitación menor MIPYME via ComprasMX** — registrarse como proveedor + ofertar a:
- Estados rezagados LNETB (ver `mp_lnetb_auditor`)
- Dependencias federales sin SRE propio
- Servicios estatales que ya operan URBEM (Cívica Digital) y quieren capa de monitoreo

## Estado real

Real por defecto. `PLUGINS_MX_MOCK=1` es la única forma de obtener checks simulados
(`simulated: true`).

- `portales_check_http`: GET con httpx (no HEAD: varios portales gob.mx responden mal a HEAD),
  timeout 30 s. Un portal caído, con TLS roto o bloqueado es **dato** (`vivo: false` +
  `error_tipo`), no error del MCP. Un 403 de Akamai/Cloudflare se reporta como
  `bloqueado_por_waf` con `vivo: null`: el sitio responde pero rechaza clientes no-navegador.
- `portales_check_form_render`: Chromium real vía `shared.playwright_real.playwright_session`
  (extra `publicos-federales-2`). Si Playwright falla → `UpstreamError`, sin fallback.
- `portales_configurar_alerta`: no hay servicio que persista alertas; devuelve la
  especificación con `persistida: false` (antes inventaba un `alerta_id` "activa").

Validación en vivo — 2026-10-14, una pasada por los 25 portales (1 s entre hosts):

| Resultado | Portales |
|---|---|
| 200 | renapo_curp, ine_portal, sre_pasaporte, profeco_repep, profeco_buro, stps_repse, llave_mx, gobmx, cdmx_finanzas (30 s), cdmx_semovi, edomex, nl, jal, qro, yuc, bc, monterrey_predial |
| 403 Akamai (`bloqueado_por_waf`) | infonavit_micuenta, conamer_catalogo |
| 403 sin firma WAF | imss_idse, imss_semanas |
| TLS | sat_padron (`DH_KEY_TOO_SMALL`), sat_verificacfdi (cadena incompleta), dof (`www.dof.gob.mx` hostname mismatch) |
| Timeout | guadalajara_predial (visorurbano.com) |

`portales_check_form_render("conamer_catalogo", "#txtSearch")` 2026-10-14: con Chromium
headless → 403 Akamai (`bloqueado_por_waf`); con `MP_PLAYWRIGHT_HEADLESS=0` → 200 y
`encontrado: true`. Los portales detrás de Akamai necesitan navegador con ventana.

Test live: `PLUGINS_MX_LIVE=1 pytest mp_portales_monitor -k live` (GET https://www.gob.mx/ → 200).
