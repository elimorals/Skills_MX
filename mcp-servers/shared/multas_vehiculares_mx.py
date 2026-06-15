"""Catálogo multas vehiculares MX — discovery 2026-06-15 con Playwright.

4 sistemas estatales con portal público:
  - CDMX (SAF): reusa data.finanzas.cdmx.gob.mx/sma/Consultaciudadana (mismo
    endpoint que verificación + tenencia + adeudos vehiculares).
  - EdoMex (SSEM): infracciones.ssedomex.gob.mx con Cloudflare Turnstile.
  - NL (ICVNL): icvnl.gob.mx/estadodecuenta — hub que requiere navegación.
  - JAL: gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos con
    reCAPTCHA v2/v3.

Universo: ~30M vehículos registrados MX (cobertura combinada 4 estados ~22M).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


MetodoMultas = Literal["publica", "publica_captcha", "login", "hub_navegacion", "no_implementado"]


@dataclass
class SistemaMultas:
    clave: str
    nombre_estado: str
    organismo: str
    url_portal: str
    url_consulta: str
    identificador_label: str
    identificador_regex: str
    metodo: MetodoMultas
    cobertura_vehiculos: int
    notas: str = ""
    captcha_sitekey: str = ""
    captcha_tipo: str = ""  # "recaptcha_v2", "recaptcha_v3", "turnstile", "imagen", ""


CATALOGO_MULTAS: list[SistemaMultas] = [
    SistemaMultas(
        clave="cdmx",
        nombre_estado="Ciudad de México",
        organismo="Secretaría de Administración y Finanzas (SAF)",
        url_portal="https://data.finanzas.cdmx.gob.mx",
        url_consulta="https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana",
        identificador_label="Placa",
        identificador_regex=r"^[A-Z0-9]{5,8}$",
        metodo="publica_captcha",
        cobertura_vehiculos=5_000_000,
        captcha_tipo="imagen",
        notas="✅ Discovery 2026-06-15: REUSA endpoint SAF de verificación+tenencia. CAPTCHA imagen alfanumérica.",
    ),
    SistemaMultas(
        clave="edomex",
        nombre_estado="Estado de México",
        organismo="Secretaría de Seguridad del Estado de México (SS)",
        url_portal="https://infracciones.ssedomex.gob.mx",
        url_consulta="https://infracciones.ssedomex.gob.mx/Search",
        identificador_label="Placa / Permiso / Serie",
        identificador_regex=r"^[A-Z0-9]{5,17}$",
        metodo="publica_captcha",
        cobertura_vehiculos=8_000_000,
        captcha_sitekey="0x4AAAAAABvIKlFRR9OpwO3-",
        captcha_tipo="turnstile",
        notas="✅ Discovery 2026-06-15: ASP.NET MVC, Cloudflare Turnstile, doctype=PLACA|PERMISO|SERIE.",
    ),
    SistemaMultas(
        clave="nl",
        nombre_estado="Nuevo León",
        organismo="Instituto de Control Vehicular de Nuevo León (ICVNL)",
        url_portal="https://www.icvnl.gob.mx",
        url_consulta="https://www.icvnl.gob.mx/estadodecuenta",
        identificador_label="Placa",
        identificador_regex=r"^[A-Z0-9]{5,8}$",
        metodo="indirecto",
        cobertura_vehiculos=5_000_000,
        notas="⚠ Discovery 2026-06-15 r2: ICVNL solo expone REFRENDO (placas/tenencia), NO multas. Multas NL son municipales — ver `nl_sanpedro`.",
    ),
    SistemaMultas(
        clave="nl_sanpedro",
        nombre_estado="Nuevo León",
        organismo="Tesorería Municipal San Pedro Garza García",
        url_portal="https://www.sanpedro.gob.mx",
        url_consulta="https://aplicativos.sanpedro.gob.mx/esanpedro/multas/multasnew.asp",
        identificador_label="Placa (sin espacios ni guiones)",
        identificador_regex=r"^[A-Z0-9]{5,8}$",
        metodo="publica_captcha",
        cobertura_vehiculos=130_000,  # parque vehicular SPGG
        captcha_sitekey="6LfCmAEoAAAAAPZhXqaVaJQ074mEvYZ2kHutYTDA",
        captcha_tipo="recaptcha_v2",
        notas="✅ Discovery 2026-06-15 r2: form POST e_cuenta_sp.asp, input `placa`, token CSRF, reCAPTCHA v2.",
    ),
    SistemaMultas(
        clave="jal",
        nombre_estado="Jalisco",
        organismo="Secretaría de la Hacienda Pública (Gobierno en Línea)",
        url_portal="https://gobiernoenlinea1.jalisco.gob.mx",
        url_consulta="https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos",
        identificador_label="Placa + número serie + nombre + motor",
        identificador_regex=r"^[A-Z0-9]{5,8}$",
        metodo="publica_captcha",
        cobertura_vehiculos=4_000_000,
        captcha_sitekey="6LehxCgfAAAAAE_6lvOTiXBtQNZCyc37CLZssnzC",
        captcha_tipo="recaptcha_v2",
        notas="✅ Discovery 2026-06-15: form publico /serviciosVehiculares/adeudos con 4 campos. reCAPTCHA v2 checkbox.",
    ),
]


def buscar_sistema(clave: str) -> SistemaMultas | None:
    clave_norm = clave.strip().lower()
    for s in CATALOGO_MULTAS:
        if s.clave == clave_norm:
            return s
    return None


def listar_sistemas() -> list[SistemaMultas]:
    return list(CATALOGO_MULTAS)


__all__ = ["MetodoMultas", "SistemaMultas", "CATALOGO_MULTAS",
           "buscar_sistema", "listar_sistemas"]
