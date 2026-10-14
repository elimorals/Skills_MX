"""Cédula profesional SEP (Registro Nacional de Profesionistas).

Portal: https://cedulaprofesional.sep.gob.mx/ (Angular). Verificado 2026-10-14
leyendo `assets/config.json` y `main.*.js`:

- Token: GET  https://cedulaprofesional.sep.gob.mx/api/auth/token
         (headers X-Client-Id / X-API-Key públicos del bundle)
- Consulta: POST https://cedulaprofesional.sep.gob.mx/api/rnp/solr/profesionista/consultar/byDetalle
         body {"numCedula": ...}, headers Authorization: Bearer + **X-Recaptcha-Token**
         (reCAPTCHA v3, site key 6Leb1M4rAAAAAP_gRcAyMiOo99-j6eqQajKuMlB9).

Cada consulta exige un token reCAPTCHA v3 (action "submit", api.js no Enterprise).
- Con solver opt-in (`solver_activo("sep_profesional")`): se lee la sitekey de
  `assets/config.json` (respaldo: constante), 2captcha emite el token y se consulta
  la API real. 401/403 o 400 que mencione captcha = token rechazado → reintento.
- Sin solver: **handoff humano**.
Mock solo con PLUGINS_MX_MOCK=1.
"""

from __future__ import annotations

import os
import re
from typing import Any, Optional

import httpx

from shared.captcha_solver import CaptchaSolver, TokenRechazado, con_token, solver_activo
from shared.errors import UpstreamError, ValidationError
from shared.portal_handoff import USER_AGENT, armar_handoff

URL_SEP_CEDULA = "https://cedulaprofesional.sep.gob.mx/"
API_CONSULTA = f"{URL_SEP_CEDULA}api/rnp/solr/profesionista/consultar/byDetalle"
URL_CONFIG = f"{URL_SEP_CEDULA}assets/config.json"
URL_TOKEN = f"{URL_SEP_CEDULA}api/auth/token"
# Respaldo si config.json no responde (valores públicos del bundle, 2026-10-14).
CONFIG_RESPALDO = {
    "clientId": "rnp-angular-app-prod",
    "apiKey": "65da8s675f8s75fda675s8d76as87d5as675da",
    "recaptchaSiteKey": "6Leb1M4rAAAAAP_gRcAyMiOo99-j6eqQajKuMlB9",
}
RECAPTCHA_ACCION = "submit"


def validar_formato_cedula(cedula: str) -> bool:
    """Cédula SEP es 7-8 dígitos numéricos."""
    if not cedula or not isinstance(cedula, str):
        return False
    return bool(re.match(r"^\d{7,8}$", cedula.strip()))


def handoff_sep(campos: dict[str, Any]) -> dict[str, Any]:
    return armar_handoff(
        motivo="captcha",
        url=URL_SEP_CEDULA,
        pasos=[
            "Abrir la URL en un navegador.",
            "En 'Búsqueda de Cédulas Profesionales' capturar los datos prellenados.",
            "Pulsar 'Buscar' (reCAPTCHA v3 se valida en el navegador).",
            "Verificar nombre, profesión, institución y año de expedición.",
        ],
        campos_prellenados={k: v for k, v in campos.items() if v},
        fuente="SEP-RNP",
    )


def consultar_cedula_sep(
    cedula: Optional[str] = None,
    nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    curp: Optional[str] = None,
) -> dict[str, Any]:
    """Consulta cédula SEP: handoff humano en real, mock con PLUGINS_MX_MOCK=1."""
    if cedula and not validar_formato_cedula(cedula):
        raise ValidationError(f"Cédula '{cedula}' no tiene formato válido (7-8 dígitos).")
    if not any([cedula, nombre, curp]):
        raise ValidationError(
            "Debe proveer al menos uno: cedula, nombre+apellido, o curp."
        )
    if os.environ.get("PLUGINS_MX_MOCK") == "1":
        return _mock_response(cedula, nombre, primer_apellido)
    if solver_activo("sep_profesional"):
        if cedula:
            body = {"numCedula": cedula.strip()}
        else:
            body = {k: v.strip().upper() for k, v in {
                "nombre": nombre, "primerApellido": primer_apellido,
                "segundoApellido": segundo_apellido, "curp": curp,
            }.items() if v}
        return _consulta_con_solver(body, cedula.strip() if cedula else None)
    return handoff_sep({
        "cedula": cedula,
        "nombre": nombre,
        "primer_apellido": primer_apellido,
        "segundo_apellido": segundo_apellido,
        "curp": curp,
    })


def _consulta_con_solver(body: dict[str, str], cedula: Optional[str]) -> dict[str, Any]:
    with httpx.Client(timeout=30, headers={"User-Agent": USER_AGENT}) as http:
        try:
            cfg = {**CONFIG_RESPALDO, **http.get(URL_CONFIG).json()}
        except (httpx.HTTPError, ValueError):
            cfg = CONFIG_RESPALDO
        solver = CaptchaSolver()

        def obtener_token() -> str:
            return solver.recaptcha(cfg["recaptchaSiteKey"], URL_SEP_CEDULA, version="v3", accion=RECAPTCHA_ACCION)

        def enviar(token: str) -> Any:
            try:
                auth = http.get(URL_TOKEN, headers={"X-Client-Id": cfg["clientId"], "X-API-Key": cfg["apiKey"]})
                auth.raise_for_status()
                r = http.post(API_CONSULTA, json=body, headers={
                    "Authorization": f"Bearer {auth.json()['access_token']}", "X-Recaptcha-Token": token,
                })
            except (httpx.HTTPError, KeyError, ValueError) as exc:
                raise UpstreamError(f"SEP no respondió: {type(exc).__name__}") from exc
            if r.status_code in (401, 403) or (r.status_code == 400 and "captcha" in r.text.lower()):
                raise TokenRechazado()
            if r.status_code != 200:
                raise UpstreamError(f"SEP respondió HTTP {r.status_code}.", {"status_code": r.status_code})
            return r.json() if r.content else []

        datos = con_token(obtener_token, enviar, "SEP-RNP")
    registros = datos if isinstance(datos, list) else [datos] if datos else []
    if cedula:
        registros = [x for x in registros if str(x.get("cedula")) == cedula]
    base = {"fuente": "SEP-RNP", "url_consultada": URL_SEP_CEDULA, "simulated": False, "consultado": True}
    if not registros:
        return {**base, "encontrada": False, "cedula": cedula, "vigente": False}
    salida = [_normalizar_registro(x) for x in registros]
    if cedula:
        return {**base, "encontrada": True, **salida[0]}
    return {**base, "encontrada": True, "total": len(salida), "resultados": salida, **salida[0]}


def _normalizar_registro(x: dict[str, Any]) -> dict[str, Any]:
    nombre = " ".join(str(x.get(k) or "").strip() for k in ("nombre", "primerApellido", "segundoApellido")).strip()
    return {
        "cedula": str(x.get("cedula") or ""),
        "nombre_completo": nombre,
        "profesion": x.get("profesion"),
        "institucion": x.get("institucion"),
        "entidad_institucion": x.get("entidadInstitucion"),
        "anio_registro": x.get("anioRegistro"),
        "genero": {"1": "M", "2": "F"}.get(str(x.get("genero")), x.get("genero")),
        # El RNP no publica bajas: la cédula listada es la registrada (no caduca).
        "vigente": True,
    }


def _mock_response(
    cedula: Optional[str], nombre: Optional[str], primer_apellido: Optional[str]
) -> dict[str, Any]:
    """Respuesta mock realista para desarrollo."""
    return {
        "cedula": cedula or "1234567",
        "nombre_completo": f"{nombre or 'JUAN'} {primer_apellido or 'PEREZ'} GARCIA",
        "profesion": "Médico Cirujano",
        "institucion": "Universidad Nacional Autónoma de México",
        "fecha_expedicion": "2015-06-15",
        "vigente": True,
        "fuente": "SEP-RNP",
        "url_consultada": URL_SEP_CEDULA,
        "simulated": True,
    }
