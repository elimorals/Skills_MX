"""SAF CDMX (Secretaría de Administración y Finanzas) — consulta de adeudos vehiculares.

Endpoint público sin Llave CDMX. Lo usan mp_cdmx_municipal, mp_verificacion_vehicular_mx,
mp_multas_mx y mp_multas_vehiculares_mx.

Estructura verificada en vivo (solo GET) el 2026-10-14:
- GET  https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana → Laravel; cookies
  `XSRF-TOKEN` + `saf_data_session`; `<meta name="csrf-token">`; form `form_adeudos`
  con `inputPlaca` y `captcha_code`; imagen `<img src=".../captcha/flat?XXXX">` (PNG 160x52,
  ligada a la sesión).
- El JS `js/consultar_pagos/consulta_adeudos.js` hace POST AJAX a
  `/consulta_adeudos/obtenAdeudos` con `placa`, `captcha_code` y header `X-CSRF-TOKEN`.
  Éxito: JSON `{status: "valido", html, tenencia_code, fotocivicas_verifica, sin_derecho}`.
  Error de validación (Laravel): 422 `{errors: {campo: [...]}}`.

Con `solver_activo("saf_cdmx")` se resuelve el captcha con 2captcha; si no, handoff humano.
La respuesta POST no se ha visto en vivo (falta llave de 2captcha): el parseo sigue al JS.
"""
from __future__ import annotations

import re
from typing import Any

import httpx

from shared.captcha_solver import (
    REINTENTOS_CAPTCHA,
    CaptchaSolver,
    imagen_de_src,
    solver_activo,
    texto_html,
)
from shared.errors import UpstreamError, ValidationError
from shared.portal_handoff import SAF_CDMX_ADEUDOS, USER_AGENT, handoff_humano

URL_SAF_CDMX_CONSULTA = "https://data.finanzas.cdmx.gob.mx/sma/Consultaciudadana"
URL_SAF_CDMX_ADEUDOS = "https://data.finanzas.cdmx.gob.mx/consulta_adeudos"
URL_SAF_CDMX_OBTEN_ADEUDOS = "https://data.finanzas.cdmx.gob.mx/consulta_adeudos/obtenAdeudos"
URL_SAF_CDMX_PAGOS = "https://data.finanzas.cdmx.gob.mx/consultas_pagos/consulta_pagos"

SAF_CDMX_FORM_ID = "form_adeudos"
SAF_CDMX_FIELDS = {
    "placa": "inputPlaca",
    "captcha": "captcha_code",
}
SAF_CDMX_METHOD = "POST"


def normalizar_placa(placa: str) -> str:
    """Quita espacios/guiones y mayúsculas."""
    return placa.strip().upper().replace(" ", "").replace("-", "")


def _buscar(patron: str, texto: str, que: str) -> str:
    m = re.search(patron, texto)
    if not m:
        raise UpstreamError(f"SAF CDMX cambió: no se encontró {que} en el formulario.")
    return m.group(1)


def _resultado(placa: str, data: dict[str, Any]) -> dict[str, Any]:
    if data.get("status") != "valido":
        raise UpstreamError("SAF CDMX respondió sin resultado válido", {"status": data.get("status")})
    fragmento = data.get("html") or ""
    fotocivicas = data.get("fotocivicas_verifica")
    puede = None
    if fotocivicas is not None:  # misma regla que consulta_adeudos.js
        puede = fotocivicas is True and not data.get("sin_derecho") and data.get("tenencia_code") == "sin_adeudos"
    return {
        "status": "consultado",
        "consultado": True,
        "requiere_humano": False,
        "simulated": False,
        "portal": SAF_CDMX_ADEUDOS.nombre,
        "url": URL_SAF_CDMX_CONSULTA,
        "placa": placa,
        "tenencia_code": data.get("tenencia_code"),
        "fotocivicas_verifica": fotocivicas,
        "sin_derecho": data.get("sin_derecho"),
        "puede_verificar": puede,
        # El JS lee $mensaje_infracciones, $total_sanciones… definidos dentro del html devuelto.
        "resumen": {k: texto_html(v) for k, v in re.findall(r"\$(\w+)\s*=\s*['\"](.*?)['\"]\s*;", fragmento)},
        "detalle_texto": texto_html(fragmento),
    }


def consultar_adeudos(
    placa: str, *, http: httpx.Client | None = None, solver: CaptchaSolver | None = None,
) -> dict[str, Any]:
    """Consulta real con captcha resuelto por 2captcha. Reintenta si el portal lo rechaza."""
    placa = normalizar_placa(placa)
    solver = solver or CaptchaSolver()
    c = http or httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30, follow_redirects=True)
    try:
        for _ in range(REINTENTOS_CAPTCHA):
            form = c.get(URL_SAF_CDMX_CONSULTA)
            form.raise_for_status()
            token = _buscar(r'name="csrf-token"\s+content="([^"]+)"', form.text, "csrf-token")
            src = _buscar(r'<img[^>]+src="([^"]*captcha[^"]*)"', form.text, "la imagen CAPTCHA")
            codigo = solver.imagen(imagen_de_src(c, src, URL_SAF_CDMX_CONSULTA))
            r = c.post(
                URL_SAF_CDMX_OBTEN_ADEUDOS,
                data={"placa": placa, "captcha_code": codigo},
                headers={"X-CSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
            )
            if r.status_code == 422:
                try:
                    errores = r.json().get("errors") or {}
                except ValueError:
                    errores = {}
                if "captcha_code" in errores:
                    continue
                raise ValidationError("SAF CDMX rechazó la consulta", {"errores": errores})
            r.raise_for_status()
            try:
                data = r.json()
            except ValueError as exc:
                raise UpstreamError("SAF CDMX no devolvió JSON") from exc
            return _resultado(placa, data)
    except httpx.HTTPError as exc:
        raise UpstreamError(f"SAF CDMX no respondió: {type(exc).__name__}") from exc
    finally:
        if http is None:
            c.close()
    raise UpstreamError(f"SAF CDMX rechazó el CAPTCHA {REINTENTOS_CAPTCHA} veces", {"placa": placa})


def adeudos_o_handoff(placa: str, **extra: Any) -> dict[str, Any]:
    """Consulta real si el solver está activo; si no, el handoff humano de siempre."""
    if solver_activo("saf_cdmx"):
        return {**consultar_adeudos(placa), **extra}
    return handoff_humano(SAF_CDMX_ADEUDOS, placa=normalizar_placa(placa), **extra)


__all__ = [
    "URL_SAF_CDMX_CONSULTA", "URL_SAF_CDMX_ADEUDOS", "URL_SAF_CDMX_OBTEN_ADEUDOS", "URL_SAF_CDMX_PAGOS",
    "SAF_CDMX_FORM_ID", "SAF_CDMX_FIELDS", "SAF_CDMX_METHOD",
    "normalizar_placa", "consultar_adeudos", "adeudos_o_handoff",
]
