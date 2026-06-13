"""Catálogo central de portales de multas de tránsito en MX.

Las multas son competencia ESTATAL (no municipal), aunque algunas ciudades
grandes (CDMX, Monterrey, Guadalajara) tienen sus propios sistemas.

Patrón típico: input placa → consulta → tabla de infracciones pendientes.

⚠ Muchos portales usan reCAPTCHA — humano-en-loop obligatorio para esos.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.playwright_municipal_generic import PortalConfig  # noqa: E402


# Portales estatales/municipales de multas con selectores conocidos
PORTALES_MULTAS: dict[str, dict[str, PortalConfig]] = {
    "cdmx": {
        "default": PortalConfig(
            url="https://www.semovi.cdmx.gob.mx/tramites-y-servicios/automovilistas/infracciones",
            input_selectors=["input[name='placa']", "input#placa"],
            submit_selectors=["button:has-text('Consultar')", "button[type='submit']"],
            result_selector="table, .resultado",
            identificador_etiqueta="placa",
        ),
    },
    "nl": {
        "default": PortalConfig(
            url="https://www.nl.gob.mx/tramites-y-servicios/multas",
            input_selectors=["input[name='placa']", "input#placa"],
            submit_selectors=["button:has-text('Consultar')"],
            result_selector="table",
            identificador_etiqueta="placa",
        ),
    },
    "jal": {
        "default": PortalConfig(
            url="https://multas.jalisco.gob.mx",
            input_selectors=["input[name='placa']"],
            submit_selectors=["button[type='submit']"],
            result_selector="table",
            identificador_etiqueta="placa",
        ),
    },
    "yuc": {
        "default": PortalConfig(
            url="https://transito.yucatan.gob.mx/multas",
            input_selectors=["input[name='placa']"],
            submit_selectors=["button[type='submit']"],
            result_selector="table",
            identificador_etiqueta="placa",
        ),
    },
    "bc": {
        "default": PortalConfig(
            url="https://transitobc.gob.mx/multas",
            input_selectors=["input[name='placa']"],
            submit_selectors=["button[type='submit']"],
            result_selector="table",
            identificador_etiqueta="placa",
        ),
    },
    "pue": {
        "default": PortalConfig(
            url="https://hacienda.puebla.gob.mx/multas",
            input_selectors=["input[name='placa']"],
            submit_selectors=["button[type='submit']"],
            result_selector="table",
            identificador_etiqueta="placa",
        ),
    },
    "qro": {
        "default": PortalConfig(
            url="https://control-vehicular.queretaro.gob.mx/multas",
            input_selectors=["input[name='placa']"],
            submit_selectors=["button[type='submit']"],
            result_selector="table",
            identificador_etiqueta="placa",
        ),
    },
    "edomex": {
        "default": PortalConfig(
            url="https://sfpya.edomexico.gob.mx/multas/",
            input_selectors=["input[name='placa']"],
            submit_selectors=["button[type='submit']"],
            result_selector="table",
            identificador_etiqueta="placa",
        ),
    },
}


# Estados que sabemos requieren reCAPTCHA / anti-bot — humano-en-loop obligatorio
ESTADOS_CON_CAPTCHA: set[str] = {"cdmx"}  # SEMOVI reCAPTCHA Enterprise

# Notas explicativas por estado (para errores informativos)
NOTAS_ESTADO: dict[str, str] = {
    "cdmx": "SEMOVI usa reCAPTCHA Enterprise — NO automatizable. Humano debe completar el CAPTCHA.",
    "nl": "Portal NL gob.mx — verificar selectores experimentales.",
    "jal": "multas.jalisco.gob.mx — funcional pero validar selectores.",
    "yuc": "Yucatán transito — validar URL vigente.",
}


def get_portal_multas(estado: str) -> Optional[PortalConfig]:
    """Devuelve PortalConfig para multas del estado, o None si no soportado."""
    portales_estado = PORTALES_MULTAS.get(estado.lower())
    if not portales_estado:
        return None
    return portales_estado.get("default")


def estados_soportados() -> list[str]:
    return sorted(PORTALES_MULTAS.keys())


def requiere_captcha(estado: str) -> bool:
    return estado.lower() in ESTADOS_CON_CAPTCHA
