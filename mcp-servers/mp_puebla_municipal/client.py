"""Cliente mp_puebla_municipal.

Predial: srvappayt.pueblacapital.gob.mx:7016/pabel/iniciopredial (Spring/Oracle, verificado
en vivo solo con GET el 2026-10-14): form `forma`, POST a la misma URL con `tipo` (PU/PR),
`cuenta` (7 dígitos) + `delegacion` (2 dígitos) o `lc` (línea de captura, 24 dígitos),
`answer` (CAPTCHA de imagen `simpleImg.jpg`, PNG 150x50, ligado a JSESSIONID) y `_csrf`.
Sin solver → handoff humano. Con `solver_activo("puebla_predial")` → consulta real.
Multas estatales: sin portal público verificado (usar mp_multas_mx).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import httpx

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.captcha_solver import (  # noqa: E402
    REINTENTOS_CAPTCHA,
    CaptchaSolver,
    imagen_de_src,
    solver_activo,
    texto_html,
)
from shared.errors import UpstreamError  # noqa: E402
from shared.portal_handoff import USER_AGENT, armar_handoff  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "puebla_mun"
URL_PREDIAL = "https://srvappayt.pueblacapital.gob.mx:7016/pabel/iniciopredial"

# ponytail: las respuestas POST no se han visto en vivo (falta llave de 2captcha). Si el portal
# devuelve el formulario otra vez se asume captcha rechazado, salvo que traiga una alerta de
# error distinta; ajustar estas regex con la primera respuesta real.
_CAPTCHA_MAL = re.compile(r"(?i)(c[oó]digo|captcha|imagen|caracteres)\W+(?:\w+\W+){0,6}?(incorrect|inv[aá]lid|no coincide|err[oó]ne)")
_ALERTA_ERROR = re.compile(r'(?is)<div[^>]+class="[^"]*(?:alert-danger|alert-warning|error)[^"]*"[^>]*>(.*?)</div>')
_TOTAL = re.compile(r"(?i)total[^$\d]{0,40}\$?\s*([\d,]+\.\d{2})")


def _resultado(html: str, cuenta: str) -> dict[str, Any]:
    filas = [
        [texto_html(c) for c in re.findall(r"(?is)<t[hd][^>]*>(.*?)</t[hd]>", fila)]
        for fila in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", html)
    ]
    texto = texto_html(html)
    m = _TOTAL.search(texto)
    return {
        "status": "consultado",
        "consultado": True,
        "requiere_humano": False,
        "simulated": False,
        "portal": "Tesorería Municipal de Puebla — pago de predial",
        "url": URL_PREDIAL,
        "cuenta_predial": cuenta,
        "total_mxn": float(m.group(1).replace(",", "")) if m else None,
        "tablas": [f for f in filas if any(f)],
        "detalle_texto": texto[:4000],
    }


def consultar_predial_portal(
    *, tipo: str = "PU", cuenta: str = "", delegacion: str = "", lc: str = "",
    http: httpx.Client | None = None, solver: CaptchaSolver | None = None,
) -> dict[str, Any]:
    """Consulta real con el CAPTCHA resuelto por 2captcha; reintenta si el portal lo rechaza."""
    solver = solver or CaptchaSolver()
    c = http or httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30, follow_redirects=True)
    try:
        for _ in range(REINTENTOS_CAPTCHA):
            form = c.get(URL_PREDIAL)
            form.raise_for_status()
            csrf = re.search(r'name="_csrf"\s+value="([^"]+)"', form.text)
            src = re.search(r'<img[^>]*src="([^"]+)"[^>]*id="captcha"', form.text)
            if not (csrf and src):
                raise UpstreamError("El portal de predial de Puebla cambió: falta _csrf o la imagen CAPTCHA.")
            answer = solver.imagen(imagen_de_src(c, src.group(1), URL_PREDIAL), max_len=5)
            r = c.post(URL_PREDIAL, data={
                "tipo": tipo, "cuenta": cuenta, "delegacion": delegacion, "lc": lc,
                "answer": answer, "_csrf": csrf.group(1),
            })
            r.raise_for_status()
            if 'name="answer"' not in r.text:
                return _resultado(r.text, lc or cuenta)
            if _CAPTCHA_MAL.search(texto_html(r.text)):
                continue
            alerta = " ".join(texto_html(a) for a in _ALERTA_ERROR.findall(r.text)).strip()
            if alerta:
                raise UpstreamError(f"El portal de predial de Puebla rechazó la consulta: {alerta}", {"mensaje_portal": alerta})
    except httpx.HTTPError as exc:
        raise UpstreamError(f"Portal de predial de Puebla no respondió: {type(exc).__name__}") from exc
    finally:
        if http is None:
            c.close()
    raise UpstreamError(f"El portal de predial de Puebla rechazó el CAPTCHA {REINTENTOS_CAPTCHA} veces")


class PueblaMunClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_predial(self, cuenta_predial: str, delegacion: str = "", tipo: str = "PU") -> dict:
        self.bitacora.log("consultar_predial", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"cuenta_predial": cuenta_predial, "adeudo_total_mxn": 1700.0})
        digitos = re.sub(r"\D", "", cuenta_predial)
        es_lc = len(digitos) == 24
        if solver_activo("puebla_predial") and (es_lc or delegacion):
            if es_lc:
                return consultar_predial_portal(tipo=tipo, lc=digitos)
            return consultar_predial_portal(tipo=tipo, cuenta=digitos, delegacion=re.sub(r"\D", "", delegacion))
        return armar_handoff(
            url=URL_PREDIAL,
            motivo="captcha",
            detalle="El portal exige un CAPTCHA de imagen junto con cuenta, delegación y LC.",
            pasos=[
                f"Abrir {URL_PREDIAL}",
                f"Capturar cuenta {cuenta_predial}, delegación y LC (vienen en el recibo)",
                "Escribir el texto del CAPTCHA y pulsar 'Consultar'",
            ],
        )
