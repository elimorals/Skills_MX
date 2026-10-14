"""Login con e.firma (FIEL) a los portales del SAT por HTTP puro (httpx).

Port mínimo del módulo `satcfdi.portal` (MIT, https://pypi.org/project/satcfdi/,
v26.8.0). Se porta en vez de depender del paquete porque satcfdi usa
`requests` (no se puede probar con respx) y arrastra weasyprint, lxml y
pyOpenSSL. Lo que se porta: el handshake FIEL del NIDP del SAT y tres flujos de
consulta: Constancia de Situación Fiscal, Opinión de cumplimiento 32-D y RFC en
la LCO (portal de Factura electrónica: ExisteLrfc + ValidaLco).

Handshake FIEL (validado en vivo 2026-10-14, sin credenciales, hasta el reto):
  1. GET a la URL del aplicativo → redirige al NIDP (`loginda.siat`,
     `login.siat`, …) con un <form> que se auto-envía por JS.
  2. POST de ese form → página con `<form id="certform">` y un `guid` de reto.
  3. POST de certform con `token` = b64(b64(guid|rfc|no_cert) + "#" + b64(firma))
     y `fert` = vencimiento del certificado (YYMMDDhhmmssZ).
  4. Si el SAT rechaza, devuelve otra vez certform con `var error = '<motivo>'`
     ("Certificado Revocado", "Certificado Caduco", …). Si acepta, sigue la
     cadena de redirects SAML/OAuth hacia el aplicativo.

Los pasos posteriores al login (SAML, JSF de la constancia, endpoint JSON del
PDF de la 32-D) se portan tal cual de satcfdi y solo se pueden validar con una
e.firma real (test `@pytest.mark.live`).

TLS: varios hosts del SAT negocian DH de 1024 bits que OpenSSL 3 rechaza
(`DH_KEY_TOO_SMALL`). Igual que satcfdi, se excluyen las suites DH.
"""

from __future__ import annotations

import base64
import json
import re
import ssl
import time
import uuid
from datetime import datetime
from html.parser import HTMLParser
from typing import Any, Protocol
from urllib.parse import urljoin, urlparse

import httpx

from shared.errors import AuthError, UpstreamError

URL_FACTURA = "https://portal.facturaelectronica.sat.gob.mx"
URL_LOGIN_PORTAL ="https://loginda.siat.sat.gob.mx/nidp/app/login?id=fiel"
URL_LOGIN_CONSTANCIA = "https://login.siat.sat.gob.mx/nidp/idff/sso?id=fiel_Aviso"
URL_CONSTANCIA_BROKER = (
    "https://rfcampc.siat.sat.gob.mx/app/seg/SessionBroker?url=/PTSC/IdcSiat/autc/"
    "ReimpresionTramite/ConsultaTramite.jsf&parametro=c&idSessionBit=&idSessionBit=null"
)
URL_CONSTANCIA_PDF = "https://rfcampc.siat.sat.gob.mx/PTSC/IdcSiat/IdcGeneraConstancia.jsf"
URL_32D_ENTRADA = "https://ptsc32d.clouda.sat.gob.mx/?/reporteOpinion32DContribuyente"
URL_32D_PDF = "https://ptsc32d.clouda.sat.gob.mx/RespuestaCompleta/ObtenerRespuestaCompletaPdf"

_CIPHERS = (
    "ECDHE+AESGCM:ECDHE+CHACHA20:ECDH+AESGCM:ECDH+AES:RSA+AESGCM:RSA+AES"
    ":!aNULL:!eNULL:!MD5:!DSS:!DH"
)
_HEADERS = {
    # El NIDP del SAT sirve páginas vacías a UAs no-navegador; mismo UA que satcfdi.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
_RE_ERROR_LOGIN = re.compile(r"var\s+error\s*=\s*'([^']*)'")


class Firmante(Protocol):
    """Lo mínimo que el login necesita de una e.firma (ver EfirmaLoader)."""

    def metadata(self) -> Any: ...  # .rfc, .numero_certificado, .not_after
    def firmar_sha1(self, data: bytes) -> bytes: ...


def ssl_context_sat() -> ssl.SSLContext:
    import certifi

    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.set_ciphers(_CIPHERS)
    return ctx


# ---------- parsing de formularios ----------


class _FormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.forms: list[dict[str, Any]] = []
        self._actual: dict[str, Any] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "form":
            self._actual = {"attrs": a, "inputs": {}}
            self.forms.append(self._actual)
        elif tag == "input" and self._actual is not None and a.get("name"):
            self._actual["inputs"][a["name"]] = a.get("value")

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self._actual = None


def get_form(html: str, base_url: str, form_id: str | None = None) -> tuple[str | None, dict[str, str]]:
    """Primer <form method=POST> (o el de `form_id`). Devuelve (action absoluta, inputs).

    Inputs sin `value` se omiten (igual que requests con valores None).
    """
    p = _FormParser()
    p.feed(html)
    for f in p.forms:
        if form_id and f["attrs"].get("id") != form_id:
            continue
        if (f["attrs"].get("method") or "").upper() != "POST":
            continue
        action = urljoin(base_url, f["attrs"].get("action") or base_url)
        return action, {k: v for k, v in f["inputs"].items() if v is not None}
    return None, {}


def generar_token(firmante: Firmante, guid: str) -> str:
    meta = firmante.metadata()
    co = f"{guid}|{meta.rfc}|{meta.numero_certificado}".encode()
    firma_b64 = base64.b64encode(firmante.firmar_sha1(co))
    return base64.b64encode(base64.b64encode(co) + b"#" + base64.b64encode(firma_b64)).decode()


# ---------- sesión ----------


class SatFielSession:
    """Sesión httpx autenticada con e.firma contra el NIDP del SAT."""

    def __init__(self, firmante: Firmante, *, client: httpx.Client | None = None, timeout: float = 60.0) -> None:
        self.firmante = firmante
        self.client = client or httpx.Client(
            verify=ssl_context_sat(), follow_redirects=True, timeout=timeout, headers=_HEADERS
        )

    def __enter__(self) -> "SatFielSession":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.client.close()

    # -- helpers HTTP --

    def _check(self, res: httpx.Response, paso: str) -> httpx.Response:
        if res.status_code != 200:
            raise UpstreamError(
                f"Portal SAT respondió {res.status_code} en '{paso}'",
                {"paso": paso, "url": str(res.url), "status": res.status_code},
            )
        return res

    def _req(self, method: str, url: str, paso: str, **kw: Any) -> httpx.Response:
        try:
            res = self.client.request(method, url, **kw)
        except httpx.HTTPError as exc:
            raise UpstreamError(f"Portal SAT no respondió en '{paso}': {type(exc).__name__}", {"url": url}) from exc
        return self._check(res, paso)

    def _form(self, action: str, referer: str, data: dict[str, str], paso: str) -> httpx.Response:
        u = urlparse(referer)
        headers = {"Origin": f"{u.scheme}://{u.netloc}", "Referer": referer}
        return self._req("POST", action, paso, data=data, headers=headers)

    def _get(self, url: str, paso: str) -> httpx.Response:
        return self._req("GET", url, paso)

    # -- login --

    def fiel_login(self, res: httpx.Response) -> httpx.Response:
        """Contesta el reto `certform`. AuthError si el SAT rechaza la e.firma."""
        action, data = get_form(res.text, str(res.url), form_id="certform")
        if action is None or "guid" not in data:
            raise UpstreamError(
                "No se encontró el formulario de e.firma (certform) — el portal cambió",
                {"url": str(res.url)},
            )
        meta = self.firmante.metadata()
        not_after: datetime = meta.not_after
        data = data | {
            "token": generar_token(self.firmante, data["guid"]),
            "fert": not_after.strftime("%y%m%d%H%M%SZ"),
        }
        out = self._form(action, str(res.url), data, "login_fiel")
        if 'id="certform"' in out.text:
            m = _RE_ERROR_LOGIN.search(out.text)
            motivo = (m.group(1) if m else "") or "rechazo sin motivo explícito"
            raise AuthError(f"El SAT rechazó la e.firma: {motivo}", {"motivo": motivo})
        return out

    def _entrar(self, url: str) -> httpx.Response:
        """GET a la entrada del NIDP + auto-submit + reto FIEL."""
        res = self._get(url, "entrada_login")
        action, data = get_form(res.text, str(res.url))
        if action is None:
            raise UpstreamError("Página de login SAT sin formulario — el portal cambió", {"url": str(res.url)})
        return self.fiel_login(self._form(action, str(res.url), data, "autosubmit_login"))

    def login_portal(self) -> httpx.Response:
        """Login al portal general (loginda.siat). Sirve para verificar que el SAT acepta la e.firma."""
        return self._entrar(URL_LOGIN_PORTAL)

    # -- Padrón: "Factura electrónica" (ExisteLrfc + ValidaLco) --

    def consultar_rfc(self, rfc: str) -> dict[str, Any]:
        """¿Existe el RFC en la LCO del SAT y qué datos de padrón trae? (requiere e.firma propia)."""
        res = self._get(URL_FACTURA, "entrada_factura")
        action, data = get_form(res.text, str(res.url))
        if action and action.startswith("https://cfdiau.sat.gob.mx/"):
            fiel = action.replace("nidp/wsfed/ep?id=SATUPCFDiCon", "nidp/app/login?id=SATx509Custom")
            res = self.fiel_login(self._form(fiel, str(res.url), data, "cambio_a_fiel"))
            action, data = get_form(res.text, str(res.url))
            res = self._form(action, str(res.url), data, "wsfed_1")
            action, data = get_form(res.text, str(res.url))
        if not action:
            raise UpstreamError("Portal de factura sin formulario WS-Fed — el portal cambió", {"url": str(res.url)})
        res = self._form(action, str(res.url), data, "wsfed_2")
        m = re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"', res.text)
        if not m:
            raise UpstreamError("Portal de factura sin __RequestVerificationToken — login incompleto")
        headers = {
            "Origin": URL_FACTURA,
            "Request-Context": "appId=cid-v1:20ff76f4-0bca-495f-b7fd-09ca520e39f7",
            "__RequestVerificationToken": m.group(1),
        }
        rfc = rfc.strip().upper()
        existe = self._req(
            "POST", f"{URL_FACTURA}/Clientes/ExisteLrfc", "existe_lrfc",
            data={"rfcValidar": rfc}, headers=headers, follow_redirects=False,
        ).json()
        if not existe.get("exitoso"):
            raise UpstreamError("ExisteLrfc respondió sin éxito", {"respuesta": existe})
        lco = self._req(
            "GET", f"{URL_FACTURA}/Clientes/ValidaLco", "valida_lco",
            params={"rfcValidar": rfc, "aplicaRegionFronteriza": "true", "_": int(time.time() * 1000)},
            headers=headers, follow_redirects=False,
        ).json()
        return {"existe_en_lco": bool(existe.get("resultado")), "lco": json.loads(lco) if isinstance(lco, str) else lco}

    # -- Constancia de Situación Fiscal --

    def descargar_constancia(self) -> bytes:
        self._entrar(URL_LOGIN_CONSTANCIA)
        res = self._get(URL_CONSTANCIA_BROKER, "constancia_broker")
        action, data = get_form(res.text, str(res.url))
        if action == "https://login.siat.sat.gob.mx/nidp/saml2/sso":
            res = self._form(action, str(res.url), data, "saml_request")
            action, data = get_form(res.text, str(res.url))
            res = self._form(action, str(res.url), data, "saml_response")
            action, data = get_form(res.text, str(res.url))
        if action and action.endswith("/ReimpresionTramite/ConsultaTramite.jsf"):
            self._form(
                action,
                str(res.url),
                {
                    "javax.faces.partial.ajax": "true",
                    "javax.faces.source": "formReimpAcuse:j_idt50",
                    "javax.faces.partial.execute": "@all",
                    "formReimpAcuse:j_idt50": "formReimpAcuse:j_idt50",
                    "formReimpAcuse": "formReimpAcuse",
                    "formReimpAcuse:tipoTramite_input": "0",
                    "formReimpAcuse:tipoTramite_focus": "",
                    "formReimpAcuse:fechaInicio_input:": "",
                    "formReimpAcuse:fechaFin_input": "",
                    "formReimpAcuse:folio": "",
                    "javax.faces.ViewState": data.get("javax.faces.ViewState", ""),
                },
                "constancia_jsf",
            )
        pdf = self._get(URL_CONSTANCIA_PDF, "constancia_pdf").content
        return _exigir_pdf(pdf, "Constancia de Situación Fiscal")

    # -- Opinión de cumplimiento 32-D (la propia, completa) --

    def descargar_opinion_32d(self) -> bytes:
        res = self._get(URL_32D_ENTRADA, "entrada_32d")
        action, data = get_form(res.text, str(res.url))
        if action and "/nidp/app/login" in action:
            # La entrada ofrece CIEC; se cambia a FIEL.
            res = self._form(action.replace("id=ciec", "id=fiel"), str(res.url), data, "cambio_a_fiel")
            res = self.fiel_login(res)
        m = re.search(r"location\.href=['\"]([^'\"]+)['\"]", res.text)
        if m:
            res = self._get(m.group(1), "redirect_js")
        for _ in range(10):
            action, data = get_form(res.text, str(res.url))
            if not action:
                break
            res = self._form(action, str(res.url), data, "saml_oauth")
        rfc = self.firmante.metadata().rfc
        pdf_res = self._req(
            "POST",
            URL_32D_PDF,
            "opinion_pdf",
            json={
                "canal": "G",
                "curp": "",
                "idCorrelacion": str(uuid.uuid4()),
                "ip": "127.0.0.1",
                "rfc": rfc,
                "tipoConsulta": "COMPLETA",
                "tipoReporte": "32D",
                "usuario": rfc,
                "rfcCorto": rfc,
            },
            headers={
                "Accept": "application/json",
                "Origin": "https://ptsc32d.clouda.sat.gob.mx",
                "Referer": "https://ptsc32d.clouda.sat.gob.mx/",
            },
        )
        try:
            b64 = pdf_res.json().get("ContenidoBase64")
        except ValueError:
            b64 = None
        if not b64:
            raise UpstreamError("El SAT no devolvió el PDF de la opinión 32-D", {"paso": "opinion_pdf"})
        return _exigir_pdf(base64.b64decode(b64), "Opinión de cumplimiento 32-D")


def _exigir_pdf(data: bytes, que: str) -> bytes:
    if not data.startswith(b"%PDF"):
        raise UpstreamError(
            f"El SAT no devolvió un PDF de {que} (sesión expirada o portal cambió)",
            {"inicio": data[:40].decode("latin-1", "replace")},
        )
    return data
