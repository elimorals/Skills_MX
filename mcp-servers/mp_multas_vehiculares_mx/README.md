# mp_multas_vehiculares_mx

Consulta y cálculo de multas vehiculares en CDMX + EdoMex + NL + JAL.

**Cobertura combinada**: ~22M vehículos (4 estados).

## Tools

- `multas_consultar_por_placa(estado, placa)` — lista multas activas.
- `multas_calcular_total(estado, placa)` — suma con descuentos por pago oportuno.
- `multas_listar_sistemas()` — los 4 sistemas con metadatos (captcha, URL).

## Path real

- `PLUGINS_MX_MULTAS_LIVE=1` → activa.
- **CDMX**: reusa SAF (mismo endpoint que verificación + tenencia).
- **EdoMex/NL/JAL**: mock por defecto. Discovery 2026-06-15 en
  `docs/discovery-portales-2026-06-15.md`.

## Discovery

Todos los portales verificados con Playwright MCP el 2026-06-15:

| Estado | Portal | CAPTCHA |
|---|---|---|
| CDMX | data.finanzas.cdmx.gob.mx/sma/Consultaciudadana | imagen ASP.NET |
| EdoMex | infracciones.ssedomex.gob.mx/Search | Cloudflare Turnstile |
| NL | icvnl.gob.mx/estadodecuenta (hub) | n/d |
| JAL | gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos | reCAPTCHA v2 |
