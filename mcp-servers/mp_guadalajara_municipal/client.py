"""Cliente mp_guadalajara_municipal.

Predial: pagoenlinea.guadalajara.gob.mx/impuestopredial (Angular) exige reCAPTCHA
v2 antes de `consulta_adeudo` (main.js, verificado 2026-10-14). Flujo del bundle:
  1. POST aytoapi.guadalajara.gob.mx/rest/index.php/captcha/captcha  (form `response`=token)
     → {"success": bool}
  2. POST apipagoenlinea.guadalajara.gob.mx/predialApi/consulta_adeudo
     (form recaudadora 1-4, tipo U/R, cuenta 6 dígitos, correo, version) → {status, tipo, message, data}
Adeudos vehiculares Jalisco (estatal): gobiernoenlinea1.jalisco.gob.mx, form `frmAdeudos`
(POST mismo URL, accion=getAdeudos) con reCAPTCHA en botón (`data-action="submit"`).

Con solver opt-in (`PLUGINS_MX_CAPTCHA_SOLVER=2captcha` + `TWOCAPTCHA_API_KEY`) se consulta;
si no, o si faltan datos que el portal exige, handoff humano.
"""

from __future__ import annotations

import html as html_lib
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
    CaptchaSolver, TokenRechazado, con_token, extraer_sitekey, solver_activo,
)
from shared.errors import UpstreamError  # noqa: E402
from shared.portal_handoff import USER_AGENT, armar_handoff  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "guadalajara_mun"
URL_PREDIAL = "https://pagoenlinea.guadalajara.gob.mx/impuestopredial/"
URL_VEHICULAR_JAL = "https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos"

# Constantes de respaldo (main.js / HTML, 2026-10-14); en vivo se re-extraen.
PREDIAL_SITEKEY = "6LfPYOQrAAAAAG4wXEmhHL070x0BHcOHQU0GIKUc"
PREDIAL_CAPTCHA_URL = "https://aytoapi.guadalajara.gob.mx/rest/index.php/captcha/captcha"
PREDIAL_API = "https://apipagoenlinea.guadalajara.gob.mx/predialApi/consulta_adeudo"
PREDIAL_VERSION = "2026-02-05 16:24:00"  # `version_system` del bundle
JAL_SITEKEY = "6LehxCgfAAAAAE_6lvOTiXBtQNZCyc37CLZssnzC"
# ponytail: el botón usa el patrón de v3 (`data-action`); si 2captcha no lo resuelve, probar "v2".
JAL_RECAPTCHA_VERSION = "v3"


def _texto(fragmento: str) -> str:
    return " ".join(html_lib.unescape(re.sub(r"<[^>]+>", " ", fragmento)).split())


class GuadalajaraMunClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    @staticmethod
    def _http() -> httpx.Client:
        return httpx.Client(timeout=30, follow_redirects=True, headers={"User-Agent": USER_AGENT})

    # ---------------- predial ----------------

    def consultar_predial(self, cuenta_predial: str, recaudadora: str | None = None,
                          tipo: str | None = None) -> dict:
        self.bitacora.log("consultar_predial", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"cuenta_predial": cuenta_predial, "adeudo_total_mxn": 2100.0})
        if solver_activo("guadalajara_predial") and recaudadora and tipo:
            return self._predial_con_solver(cuenta_predial, str(recaudadora), tipo.upper())
        return armar_handoff(
            url=URL_PREDIAL,
            motivo="captcha",
            detalle="El portal exige reCAPTCHA v2 antes de mostrar el adeudo.",
            pasos=[
                f"Abrir {URL_PREDIAL}",
                f"Elegir recaudadora y tipo, capturar la cuenta {cuenta_predial}",
                "Resolver el reCAPTCHA y pulsar 'Consultar Adeudo Predial'",
            ],
        )

    def _predial_con_solver(self, cuenta: str, recaudadora: str, tipo: str) -> dict[str, Any]:
        with self._http() as http:
            try:
                js = http.get(URL_PREDIAL + "main.js").text
            except httpx.HTTPError:
                js = ""
            sitekey = extraer_sitekey(js, PREDIAL_SITEKEY)
            solver = CaptchaSolver()

            def enviar(token: str) -> dict[str, Any]:
                try:
                    v = http.post(PREDIAL_CAPTCHA_URL, data={"response": token})
                    v.raise_for_status()
                    if not v.json().get("success"):
                        raise TokenRechazado()
                    r = http.post(PREDIAL_API, data={
                        "recaudadora": recaudadora, "tipo": tipo, "cuenta": cuenta,
                        "correo": "", "version": PREDIAL_VERSION,
                    })
                    r.raise_for_status()
                    return r.json()
                except (httpx.HTTPError, ValueError) as exc:
                    raise UpstreamError(f"Predial Guadalajara falló: {type(exc).__name__}",
                                        {"url": PREDIAL_API}) from exc

            res = con_token(lambda: solver.recaptcha(sitekey, URL_PREDIAL), enviar, "Predial Guadalajara")
        data = res.get("data") if isinstance(res.get("data"), dict) else {}
        return {
            "consultado": True,
            "simulated": False,
            "fuente": PREDIAL_API,
            "cuenta_predial": cuenta,
            "recaudadora": recaudadora,
            "tipo_predio": tipo,
            "status": res.get("status"),
            "tipo_respuesta": res.get("tipo"),
            "mensaje": res.get("message"),
            "procede_pago": res.get("status") is True and str(res.get("tipo")) == "3",
            "importe_mxn": data.get("importe"),
            "fecha_limite": data.get("fecha_limite"),
            "linea_captura": data.get("linea_captura"),
            "adeudos": data.get("adeudos") or [],
            "clave_catastral": data.get("ClaveCatastral"),
            "domicilio": " ".join(str(data.get(k) or "") for k in ("Calle", "NoExterior", "NoInterior", "Colonia")).strip() or None,
            "valor_catastral": data.get("ValorCatastral"),
            "captcha": {"tipo": "recaptcha_v2", "sitekey": sitekey},
        }

    # ---------------- adeudos vehiculares Jalisco ----------------

    def consultar_adeudos_vehiculares(self, placa: str, numero_serie: str | None = None,
                                      nombre_propietario: str | None = None,
                                      numero_motor: str | None = None) -> dict:
        self.bitacora.log("consultar_adeudos_vehiculares", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"placa": placa, "adeudo_total_mxn": 640.0})
        if solver_activo("jalisco_adeudos") and numero_serie and len(numero_serie.strip()) >= 5:
            return self._jalisco_con_solver(placa, numero_serie, nombre_propietario or "", numero_motor or "")
        return armar_handoff(
            url=URL_VEHICULAR_JAL,
            motivo="captcha",
            detalle="Adeudos vehiculares de Jalisco (refrendo/multas estatales); el portal exige reCAPTCHA.",
            pasos=[
                f"Abrir {URL_VEHICULAR_JAL}",
                f"Capturar la placa {placa} (y número de serie si lo pide)",
                "Resolver el reCAPTCHA y pulsar 'Consultar'",
            ],
        )

    def _jalisco_con_solver(self, placa: str, serie: str, nombre: str, motor: str) -> dict[str, Any]:
        with self._http() as http:
            try:
                pagina = http.get(URL_VEHICULAR_JAL).text
            except httpx.HTTPError:
                pagina = ""
            sitekey = extraer_sitekey(pagina, JAL_SITEKEY)
            accion = (re.search(r'data-action="([^"]+)"', pagina) or [None, "submit"])[1]
            solver = CaptchaSolver()

            def enviar(token: str) -> str:
                try:
                    r = http.post(URL_VEHICULAR_JAL, data={
                        "origen": "normal", "accion": "getAdeudos",
                        "placa": placa.upper().strip(), "numeroSerie": serie.upper().strip(),
                        "nombrePropietario": nombre.upper().strip(), "numeroMotor": motor.upper().strip(),
                        "g-recaptcha-response": token,
                    })
                    r.raise_for_status()
                except httpx.HTTPError as exc:
                    raise UpstreamError(f"Adeudos Jalisco falló: {type(exc).__name__}",
                                        {"url": URL_VEHICULAR_JAL}) from exc
                if "captcha" in _error_jal(r.text).lower():
                    raise TokenRechazado()
                return r.text

            html = con_token(
                lambda: solver.recaptcha(sitekey, URL_VEHICULAR_JAL, version=JAL_RECAPTCHA_VERSION, accion=accion),
                enviar, "Adeudos vehiculares Jalisco",
            )
        error = _error_jal(html)
        # ponytail: página de resultado no vista en vivo (falta llave); se devuelven las tablas tal cual.
        filas = [
            [_texto(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
            for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I)
        ]
        return {
            "consultado": True,
            "simulated": False,
            "fuente": URL_VEHICULAR_JAL,
            "placa": placa.upper().strip(),
            "mensaje_portal": error or None,
            "filas": [f for f in filas if any(f)],
            "formato_resultado_validado": False,
            "captcha": {"tipo": f"recaptcha_{JAL_RECAPTCHA_VERSION}", "sitekey": sitekey, "accion": accion},
        }


def _error_jal(html: str) -> str:
    m = re.search(r'<div id="error"[^>]*>(.*?)</div>', html or "", re.S | re.I)
    return _texto(m.group(1)) if m else ""
