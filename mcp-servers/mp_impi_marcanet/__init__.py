"""mp_impi_marcanet — MCP para búsqueda de marcas en IMPI (vía ViDoc).

IMPI = Instituto Mexicano de la Propiedad Industrial.
Antes: MARCANET (descontinuado). Hoy: ViDoc (https://vidoc.impi.gob.mx).

Universo: legaltech, agencias creativas, startups, marketplaces — validar
denominación de marca antes de lanzar producto en MX.

Protecciones del portal:
  - Angular SPA (no httpx-only)
  - reCAPTCHA v3 invisible (Google site key 6LefZpMqAAAAA...)
  - XSRF Token (ASP.NET Core DataProtection)

Por eso este MCP usa **Playwright** en modo real (3-5s/query), o mock
determinístico en CI/dev (default).
"""
__all__: list[str] = []
