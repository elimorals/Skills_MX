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

## Path real

`pip install playwright httpx` + `MP_PLAYWRIGHT_PUBLIC=1` para checks reales.
