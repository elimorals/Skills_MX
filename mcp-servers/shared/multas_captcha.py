"""Multas con solver de CAPTCHA opt-in: SS EdoMex (Turnstile) y San Pedro Garza García (reCAPTCHA v2).

Solo corre si `solver_activo("multas_edomex"|"multas_sanpedro")`; si no, los MCPs
devuelven el handoff humano de siempre. Descubierto en vivo (GET) el 2026-10-14:

- EdoMex  GET/POST https://infracciones.ssedomex.gob.mx/Search (ASP.NET Core).
  Form: doctype (1=PLACA, 5=FOLIO), Doc, __RequestVerificationToken (+ cookie antiforgery),
  cf-turnstile-response. Turnstile sitekey 0x4AAAAAABvIKlFRR9OpwO3-, sin action/cData.
  El HTML de resultados NO se ha visto (exige token): el parser es genérico y falla
  cerrado (UpstreamError) si no reconoce tabla ni mensaje de "sin infracciones".
- San Pedro GET multasnew.asp → POST e_cuenta_sp.asp con placa, token (hidden),
  submit=Consultar, g-recaptcha-response. reCAPTCHA v2 sitekey 6LfCmAEoAAAAAPZhXqaVaJQ074mEvYZ2kHutYTDA.
  Resultado: tabla Mun./Boleta/Fecha/Infracción/Crucero/Valor/Bonif. Desc./Total/
  Fecha Pago/Recibo/Pagado/Saldo.

Sin validar en vivo con token real (falta llave de 2captcha).
"""
from __future__ import annotations

import html as htmllib
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin

import httpx

from shared import portal_handoff as ph
from shared.captcha_solver import CaptchaSolver, TokenRechazado, con_token, extraer_sitekey, solver_activo
from shared.errors import UpstreamError

EDOMEX_SITEKEY = "0x4AAAAAABvIKlFRR9OpwO3-"
SANPEDRO_SITEKEY = "6LfCmAEoAAAAAPZhXqaVaJQ074mEvYZ2kHutYTDA"
PORTAL_SOLVER = {"edomex": "multas_edomex", "nl_sanpedro": "multas_sanpedro"}
_SIN_RESULTADOS = re.compile(r"no se encontr|sin infracciones|no (tiene|cuenta con|existen) infracciones", re.I)


def con_solver(clave: str) -> bool:
    return clave in PORTAL_SOLVER and solver_activo(PORTAL_SOLVER[clave])


def consultar_con_solver(clave: str, placa: str) -> dict[str, Any]:
    with httpx.Client(timeout=30, follow_redirects=True, headers={"User-Agent": ph.USER_AGENT}) as http:
        if clave == "edomex":
            return _edomex(http, placa)
        return _sanpedro(http, placa)


# ---------- EdoMex (Turnstile) ----------

def _edomex(http: httpx.Client, placa: str) -> dict[str, Any]:
    url = ph.EDOMEX_INFRACCIONES.url
    pagina = {"html": _pedir(http, "GET", url).text}
    sitekey = extraer_sitekey(pagina["html"], EDOMEX_SITEKEY)
    solver = CaptchaSolver()

    def enviar(token: str) -> list[dict[str, Any]]:
        r = _pedir(http, "POST", url, data={
            "doctype": "1", "Doc": placa, "cf-turnstile-response": token,
            "__RequestVerificationToken": _csrf(pagina["html"]),
        })
        pagina["html"] = r.text  # si rechaza, el form re-renderiza con antiforgery nuevo
        return parse_edomex(r.text)

    multas = con_token(lambda: solver.turnstile(sitekey, url), enviar, "SS EdoMex")
    return _respuesta("edomex", placa, url, "turnstile", multas)


def parse_edomex(html: str) -> list[dict[str, Any]]:
    for tabla in _tablas(html):
        if len(tabla) >= 2 and len(tabla[0]) >= 2:
            cab = [c or f"col{i}" for i, c in enumerate(tabla[0])]
            filas = [dict(zip(cab, f)) for f in tabla[1:] if len(f) == len(cab)]
            for f in filas:
                monto = next((v for k, v in f.items() if re.search(r"importe|total|monto|saldo", k, re.I)), None)
                if monto is not None and (m := _monto(monto)) is not None:
                    f["monto_mxn"] = m
            return filas
    if _SIN_RESULTADOS.search(html):
        return []
    if "cf-turnstile" in html:
        raise TokenRechazado()
    raise UpstreamError("SS EdoMex devolvió un formato no reconocido; revisar el parser.",
                        {"url": ph.EDOMEX_INFRACCIONES.url})


# ---------- San Pedro Garza García (reCAPTCHA v2) ----------

def _sanpedro(http: httpx.Client, placa: str) -> dict[str, Any]:
    url = ph.SAN_PEDRO_MULTAS.url
    destino = urljoin(url, "e_cuenta_sp.asp")
    pagina = {"html": _pedir(http, "GET", url).text}
    sitekey = extraer_sitekey(pagina["html"], SANPEDRO_SITEKEY)
    solver = CaptchaSolver()

    def enviar(token: str) -> list[dict[str, Any]]:
        r = _pedir(http, "POST", destino, data={
            "placa": placa, "token": _hidden(pagina["html"], "token"),
            "submit": "Consultar", "g-recaptcha-response": token,
        })
        return parse_sanpedro(r.text)

    multas = con_token(lambda: solver.recaptcha(sitekey, url), enviar, "Tesorería San Pedro")
    return _respuesta("nl_sanpedro", placa, destino, "recaptcha_v2", multas)


_COLS_SP = ("municipio", "boleta", "fecha", "infraccion", "crucero", "valor_mxn", "bonificacion_mxn",
            "total_mxn", "fecha_pago", "recibo", "pagado_mxn", "saldo_mxn")


def parse_sanpedro(html: str) -> list[dict[str, Any]]:
    for tabla in _tablas(html):
        if tabla and "Boleta" in tabla[0] and "Saldo" in tabla[0]:
            multas = []
            for f in tabla[1:]:
                if len(f) != len(_COLS_SP):
                    continue  # separadores y renglón de Total
                m: dict[str, Any] = dict(zip(_COLS_SP, f))
                for k in ("valor_mxn", "bonificacion_mxn", "total_mxn", "pagado_mxn", "saldo_mxn"):
                    m[k] = _monto(m[k])
                m["folio"], m["monto_mxn"] = m["boleta"], m["saldo_mxn"]
                m["estatus"] = "PENDIENTE" if (m["saldo_mxn"] or 0) > 0 else "PAGADA"
                multas.append(m)
            return multas
    if re.search(r"robot|recaptcha|captcha", html, re.I):
        raise TokenRechazado()
    raise UpstreamError("San Pedro devolvió un formato no reconocido; revisar el parser.",
                        {"url": ph.SAN_PEDRO_MULTAS.url})


# ---------- utilidades ----------

def _respuesta(clave: str, placa: str, url: str, captcha: str, multas: list[dict[str, Any]]) -> dict[str, Any]:
    pendientes = [m for m in multas if m.get("estatus", "PENDIENTE") == "PENDIENTE"]
    montos = [m.get("monto_mxn") for m in pendientes]
    return {
        "requiere_humano": False, "consultado": True, "simulated": False,
        "estado": clave, "placa": placa, "fuente": url, "captcha_resuelto": captcha,
        "multas": pendientes, "historial": multas,
        "multas_total": len(pendientes), "total_multas_pendientes": len(pendientes),
        # None si algún monto no se pudo leer: nunca se reporta 0 por falta de dato.
        "adeudo_total_mxn": round(sum(montos), 2) if None not in montos else None,
        "fecha_consulta": datetime.now(timezone.utc).isoformat(),
    }


def _pedir(http: httpx.Client, metodo: str, url: str, **kw: Any) -> httpx.Response:
    try:
        r = http.request(metodo, url, **kw)
    except httpx.HTTPError as e:
        raise UpstreamError(f"Portal no respondió: {type(e).__name__}", {"url": url}) from e
    if r.status_code != 200:
        raise UpstreamError(f"Portal respondió HTTP {r.status_code}.", {"url": url, "status_code": r.status_code})
    return r


def _hidden(html: str, nombre: str) -> str:
    m = re.search(rf'name="{nombre}"[^>]*value="([^"]*)"', html) or re.search(
        rf'value="([^"]*)"[^>]*name="{nombre}"', html)
    if not m:
        raise UpstreamError(f"El formulario ya no trae el campo '{nombre}'; el portal cambió.")
    return m.group(1)


def _csrf(html: str) -> str:
    return _hidden(html, "__RequestVerificationToken")


def _texto(celda: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", celda))).strip()


def _tablas(html: str) -> list[list[list[str]]]:
    """Tablas más internas (sin tablas anidadas) como listas de renglones de texto."""
    tablas = []
    for cuerpo in re.findall(r"<table\b[^>]*>((?:(?!<table\b).)*?)</table>", html, re.S | re.I):
        filas = [[_texto(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
                 for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", cuerpo, re.S | re.I)]
        tablas.append([f for f in filas if any(f)])
    return tablas


def _monto(v: str) -> float | None:
    v = (v or "").replace("$", "").replace(",", "").strip()
    try:
        return float(v)
    except ValueError:
        return None
