"""Acceso real al portal CEP de Banxico (https://www.banxico.org.mx/cep/).

Endpoints descubiertos leyendo `js/cep-min.js` del portal (2026-10-14):

- GET  /cep/instituciones.do?fecha=DD-MM-YYYY → JSON {"instituciones": [[clave5, nombre], ...]}
  Catálogo de participantes SPEI vigente para la fecha. La clave de 5 dígitos
  termina en el código CLABE de 3 dígitos (40012 → 012 BBVA, 90646 → 646 STP).
- POST /cep/valida.do (form) → HTML con el estado del pago.
  Campos: tipoCriterio=T, fecha, criterio (clave de rastreo), emisor, receptor,
  cuenta, receptorParticipante=0, monto, captcha, tipoConsulta (0 = consultar
  estado, 1 = descargar CEP).
- GET  /cep/descarga.do?formato=XML|PDF → CEP de la última consulta tipo 1 de la sesión.

CAPTCHA: el formulario trae la imagen de seguridad oculta y el input
`captcha` precargado con "c" por el propio portal; el JS manda ese valor
mientras el servidor no active `varHideCaptcha=false`. Replicamos exactamente
lo que envía el navegador. Si el portal vuelve a mostrar el CAPTCHA no se
intenta resolverlo: se lanza `CaptchaRequerido` y el caller devuelve un handoff
humano.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date
from typing import Any

import httpx

from shared.errors import McpError, UpstreamError, handle_httpx_error
from shared.http_helpers import build_ssl_verify

BASE_URL = "https://www.banxico.org.mx/cep/"
TIMEOUT = httpx.Timeout(90.0, connect=20.0)
USER_AGENT = "plugins-mx/mp_banxico_cep (conciliacion SPEI)"

_NO_ENCONTRADO = ("operación no encontrada", "operacion no encontrada", "no se encontró ningún pago")


class CaptchaRequerido(McpError):
    """El portal activó el CAPTCHA visible: no se resuelve automáticamente."""

    code = "captcha_requerido"


def fecha_portal(f: date) -> str:
    return f.strftime("%d-%m-%Y")


def nuevo_cliente() -> httpx.Client:
    return httpx.Client(
        base_url=BASE_URL,
        timeout=TIMEOUT,
        verify=build_ssl_verify(),
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    )


def _get(client: httpx.Client, path: str, **kw: Any) -> httpx.Response:
    try:
        r = client.get(path, **kw)
        r.raise_for_status()
        return r
    except httpx.HTTPError as exc:
        raise handle_httpx_error(exc) from exc


def abrir_sesion(client: httpx.Client) -> None:
    """Carga el formulario (cookie de sesión) y verifica que el CAPTCHA siga oculto."""
    html = _get(client, "").text
    if captcha_visible(html):
        raise CaptchaRequerido(
            "El portal CEP de Banxico está pidiendo CAPTCHA visible; requiere a una persona.",
            {"url": BASE_URL},
        )


def captcha_visible(html: str) -> bool:
    if re.search(r'name="varHideCaptcha"[^>]*value="false"', html):
        return True
    m = re.search(r'id="captchaInput"\s+class="([^"]*)"', html)
    return bool(m and "oculta" not in m.group(1))


def instituciones(client: httpx.Client, fecha: date) -> list[dict[str, str]]:
    r = _get(client, "instituciones.do", params={"fecha": fecha_portal(fecha)})
    try:
        data = r.json()
        return [{"clave": c, "nombre": n} for c, n in data["instituciones"]]
    except (ValueError, KeyError, TypeError) as exc:
        raise UpstreamError(
            "instituciones.do devolvió un formato inesperado.",
            {"body_preview": r.text[:300]},
        ) from exc


def clave_participante(catalogo: list[dict[str, str]], codigo3: str) -> dict[str, str] | None:
    """Mapea código CLABE de 3 dígitos → participante SPEI (clave de 5 dígitos)."""
    codigo3 = codigo3.zfill(3)
    for inst in catalogo:
        if inst["clave"][-3:] == codigo3 and len(inst["clave"]) >= 4:
            return inst
    return None


def consultar(
    client: httpx.Client,
    *,
    fecha: date,
    clave_rastreo: str,
    emisor: str,
    receptor: str,
    cuenta: str = "",
    monto: float | None = None,
    tipo_consulta: int = 0,
) -> dict[str, Any]:
    """POST valida.do. Devuelve {estado, mensaje, html}."""
    data = {
        "tipoCriterio": "T",
        "fecha": fecha_portal(fecha),
        "criterio": clave_rastreo,
        "emisor": emisor,
        "receptor": receptor,
        "cuenta": cuenta,
        "receptorParticipante": "0",
        "monto": f"{monto:.2f}" if monto is not None else "",
        "captcha": "c",  # valor que el propio portal precarga con el CAPTCHA oculto
        "tipoConsulta": str(tipo_consulta),
    }
    try:
        r = client.post("valida.do", data=data, headers={"X-Requested-With": "XMLHttpRequest"})
        r.raise_for_status()
    except httpx.HTTPError as exc:
        raise handle_httpx_error(exc) from exc
    return interpretar_respuesta(r.text)


def _texto(html: str) -> str:
    html = re.sub(r"(?s)<!--.*?-->|<script.*?</script>|<style.*?</style>", " ", html)
    txt = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", txt).strip()


def interpretar_respuesta(html: str) -> dict[str, Any]:
    texto = _texto(html)
    bajo = texto.lower()
    if "meta:stats=err" in html.lower():
        estado = "error_datos"
    elif any(s in bajo for s in _NO_ENCONTRADO):
        estado = "no_encontrado"
    elif "operacionesDevueltas" in html or "devuelt" in bajo:
        estado = "devuelto"
    elif "operacionesLiquidados" in html or "liquidad" in bajo:
        estado = "liquidado"
    elif "descarga.do" in html:
        estado = "cep_disponible"
    elif re.search(r"\[[A-Z]{2}\]", texto):
        estado = "error_portal"
    else:
        estado = "desconocido"
    return {"estado": estado, "mensaje": texto[:1000], "html": html}


def descargar(client: httpx.Client, formato: str) -> bytes:
    r = _get(client, "descarga.do", params={"formato": formato})
    return r.content


def parsear_xml_cep(xml_bytes: bytes) -> dict[str, Any]:
    """Parsea el XML SPEI_Tercero del CEP. Cuentas se devuelven enmascaradas."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise UpstreamError(
            "descarga.do no devolvió XML válido.",
            {"body_preview": xml_bytes[:300].decode("latin-1", "replace")},
        ) from exc

    def bloque(tag: str) -> dict[str, str]:
        el = root.find(tag)
        return dict(el.attrib) if el is not None else {}

    ben, ord_ = bloque("Beneficiario"), bloque("Ordenante")

    def enmascarar(c: str | None) -> str | None:
        return f"**** {c[-4:]}" if c else None

    return {
        "fecha_operacion": root.attrib.get("FechaOperacion"),
        "hora_operacion": root.attrib.get("Hora"),
        "clave_spei_receptor": root.attrib.get("ClaveSPEI"),
        "numero_certificado": root.attrib.get("numeroCertificado"),
        "ordenante": {
            "banco": ord_.get("BancoEmisor"),
            "nombre": ord_.get("Nombre"),
            "rfc": ord_.get("RFC"),
            "cuenta_enmascarada": enmascarar(ord_.get("Cuenta")),
        },
        "beneficiario": {
            "banco": ben.get("BancoReceptor"),
            "nombre": ben.get("Nombre"),
            "rfc": ben.get("RFC"),
            "cuenta_enmascarada": enmascarar(ben.get("Cuenta")),
        },
        "concepto": ben.get("Concepto"),
        "monto": float(ben["MontoPago"]) if ben.get("MontoPago") else None,
        "iva": float(ben["IVA"]) if ben.get("IVA") else None,
    }
