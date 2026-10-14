"""Predial Toluca — consulta pública por clave catastral (httpx, sin CAPTCHA).

Validado en vivo 2026-10-14: GET + POST ASP.NET WebForms a
http://predial.toluca.gob.mx/Formas/ImpuestoPredial.aspx (campo `txtCuenta`,
botón `Button2`). Una clave inexistente responde 200 con
"La Clave Catastral no está registrada" en `LabelMsg`.

La respuesta exitosa trae el nombre del propietario: NO se devuelve.
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from shared.errors import NotFoundError, UpstreamError, ValidationError
from shared.portal_handoff import USER_AGENT

URL = "http://predial.toluca.gob.mx/Formas/ImpuestoPredial.aspx"
CLAVE_RE = re.compile(r"^\d{16}$")


def _texto(fragmento: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragmento))).strip()


def _hidden(page: str) -> dict[str, str]:
    return dict(re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', page))


def _tabla(page: str) -> list[dict[str, str]]:
    """Filas de la tabla de liquidación (`grdliquidacion`) como dicts encabezado→valor."""
    m = re.search(r'<table[^>]*id="grdliquidacion"[^>]*>(.*?)</table>', page, re.S | re.I)
    if not m:
        return []
    filas = [
        [_texto(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S | re.I)]
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S | re.I)
    ]
    filas = [f for f in filas if any(f)]
    if len(filas) < 2:
        return []
    encabezados = filas[0]
    return [dict(zip(encabezados, f)) for f in filas[1:]]


def _monto(valor: str) -> float | None:
    limpio = re.sub(r"[^\d.\-]", "", valor or "")
    try:
        return float(limpio) if limpio else None
    except ValueError:
        return None


def parse_respuesta(page: str) -> dict[str, Any]:
    msg = re.search(r'<span[^>]*id="LabelMsg"[^>]*>(.*?)</span>', page, re.S | re.I)
    mensaje = _texto(msg.group(1)) if msg else ""
    if "no está registrada" in mensaje.lower() or "no esta registrada" in mensaje.lower():
        raise NotFoundError("La clave catastral no está registrada en Toluca.", {"portal": URL})
    conceptos = _tabla(page)
    if not conceptos:
        raise UpstreamError(
            "Toluca respondió sin tabla de liquidación ni mensaje conocido; el portal pudo cambiar.",
            {"portal": URL, "mensaje": mensaje[:200]},
        )
    # ponytail: no se ha visto una respuesta exitosa real (requiere la clave de
    # un particular); el total solo se toma de una fila rotulada "TOTAL".
    total = None
    for fila in conceptos:
        valores = list(fila.values())
        if valores and "total" in valores[0].lower():
            montos = [m for m in (_monto(v) for v in valores[1:]) if m is not None]
            total = montos[-1] if montos else None
    return {"conceptos": conceptos, "adeudo_total_mxn": total, "mensaje_portal": mensaje or None}


def consultar(clave_catastral: str, *, timeout: float = 30.0) -> dict[str, Any]:
    clave = re.sub(r"[\s-]", "", clave_catastral)
    if not CLAVE_RE.match(clave):
        raise ValidationError("La clave catastral de Toluca tiene 16 dígitos.")
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True,
                          headers={"User-Agent": USER_AGENT}) as http:
            r = http.get(URL)
            r.raise_for_status()
            r2 = http.post(URL, data={**_hidden(r.text), "txtCuenta": clave, "Button2": "Aceptar"})
            r2.raise_for_status()
    except httpx.HTTPError as e:
        raise UpstreamError(f"Predial Toluca no respondió: {type(e).__name__}", {"portal": URL}) from e
    datos = parse_respuesta(r2.text)
    return {
        "municipio": "Toluca",
        "clave_catastral_hash": clave[:4] + "***",
        **datos,
        "estatus": (
            "ver_conceptos" if datos["adeudo_total_mxn"] is None
            else "al_corriente" if datos["adeudo_total_mxn"] == 0 else "con_adeudo"
        ),
        "url_consultada": URL,
        "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        "simulated": False,
    }
