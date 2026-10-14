"""Catálogo de portales de multas de tránsito MX (revisado en vivo 2026-10-14).

Todos los portales oficiales que siguen vivos exigen CAPTCHA o no tienen flujo
automatizable, así que el MCP devuelve un handoff humano verificado
(`shared.portal_handoff`).

Retirados el 2026-10-14 (DNS inexistente o 404 en el GET de validación):
semovi.cdmx.gob.mx/.../infracciones (404), nl.gob.mx/.../multas (404),
multas.jalisco.gob.mx, transito.yucatan.gob.mx, transitobc.gob.mx,
hacienda.puebla.gob.mx, control-vehicular.queretaro.gob.mx (DNS).
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared import portal_handoff as ph  # noqa: E402

PORTALES_MULTAS: dict[str, ph.PortalCaptcha] = {
    "cdmx": ph.SAF_CDMX_ADEUDOS,
    "edomex": ph.EDOMEX_INFRACCIONES,
    "jal": ph.JALISCO_ADEUDOS,
    "nl": ph.ICVNL_ESTADO_CUENTA,
    "nl_sanpedro": ph.SAN_PEDRO_MULTAS,
}

ESTADOS_SIN_PORTAL: dict[str, str] = {
    "yuc": "transito.yucatan.gob.mx no resuelve DNS (2026-10-14).",
    "bc": "transitobc.gob.mx no resuelve DNS (2026-10-14).",
    "pue": "hacienda.puebla.gob.mx no resuelve DNS (2026-10-14).",
    "qro": "control-vehicular.queretaro.gob.mx no resuelve DNS (2026-10-14).",
}

NOTAS_ESTADO: dict[str, str] = {
    "cdmx": "SAF CDMX: CAPTCHA imagen.",
    "edomex": "SS EdoMex: Cloudflare Turnstile.",
    "jal": "Gobierno en Línea Jalisco: reCAPTCHA v2; pide placa, serie, nombre y motor.",
    "nl": "ICVNL solo expone refrendo; las multas en NL son municipales.",
    "nl_sanpedro": "San Pedro Garza García: reCAPTCHA v2.",
    **ESTADOS_SIN_PORTAL,
}


def estados_soportados() -> list[str]:
    return sorted(PORTALES_MULTAS)
