"""Cliente SAT Web Service Descarga Masiva CFDI.

Modos:
  - mock: con PLUGINS_MX_MOCK=1 o sin SAT_EFIRMA_* — respuestas determinísticas
    marcadas `simulated: true`.
  - real: con SAT_EFIRMA_CERT (.cer DER) + SAT_EFIRMA_KEY (.key PKCS#8 DER
    cifrado) + SAT_EFIRMA_PASSWORD. SOAP firmado con XMLDSig. Sin fallback a
    mock: cualquier error del SAT se levanta como McpError con su código.

Flujo end-to-end:
    cliente = SatWsClient()
    sol = cliente.solicitar_descarga(SolicitudDescarga(
        rfc_emisor="ABC120101AB1",
        fecha_inicial="2026-01-01T00:00:00",
        fecha_final="2026-01-31T23:59:59",
        tipo_solicitud="CFDI",
    ))
    estado = cliente.verificar_solicitud(sol["id_solicitud"], rfc_emisor="ABC...")
    # Polling (>=30 s) hasta estado["cod_estatus_solicitud"] == 3
    paquete = cliente.descargar_paquete(estado["paquetes"][0], rfc_emisor="ABC...")

La firma es un port de phpcfdi/sat-ws-descarga-masiva (MIT,
FielRequestBuilder): el XML se arma ya canónico (sin espacios, atributos en
orden), se digiere con SHA-1 y el SignedInfo se firma con RSA-SHA1, que es lo
que exige el servicio del SAT.
"""
from __future__ import annotations

import base64
import hashlib
import os
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    AuthError,
    ConfigError,
    UpstreamError,
    ValidationError,
    handle_httpx_error,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.sat_ws import (  # noqa: E402
    CODIGOS_SAT,
    ESTADO_ACEPTADA,
    ESTADO_EN_PROCESO,
    ESTADO_TERMINADA,
    URL_AUTENTICACION,
    URL_DESCARGAR_MASIVA,
    URL_SOLICITAR_DESCARGA,
    URL_VERIFICAR_SOLICITUD,
    SolicitudDescarga,
    estado_es_terminal,
    parsear_estado_solicitud,
)


NAMESPACE = "sat_ws"
TIMEOUT_SECONDS = 60.0

NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"
NS_DES = "http://DescargaMasivaTerceros.sat.gob.mx"
NS_AUTH = "http://DescargaMasivaTerceros.gob.mx"
NS_DS = "http://www.w3.org/2000/09/xmldsig#"
NS_WSU = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"
NS_WSSE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
_X509V3 = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3"
_B64BIN = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary"

ACCION_AUTENTICA = f"{NS_AUTH}/IAutenticacion/Autentica"
ACCION_VERIFICA = f"{NS_DES}/IVerificaSolicitudDescargaService/VerificaSolicitudDescarga"
ACCION_DESCARGA = f"{NS_DES}/IDescargaMasivaTercerosService/Descargar"

# Nombres OpenSSL de los OIDs que aparecen en el issuer de los certificados SAT.
_OID_NOMBRES = {
    "2.5.4.3": "CN", "2.5.4.10": "O", "2.5.4.11": "OU", "2.5.4.6": "C",
    "2.5.4.8": "ST", "2.5.4.7": "L", "2.5.4.9": "street", "2.5.4.17": "postalCode",
    "2.5.4.45": "x500UniqueIdentifier", "1.2.840.113549.1.9.1": "emailAddress",
    "1.2.840.113549.1.9.2": "unstructuredName",
}


def _x(texto: str) -> str:
    """Escapa texto para XML (equivalente a htmlspecialchars ENT_XML1|ENT_COMPAT)."""
    return escape(texto, {'"': "&quot;"})


class Fiel:
    """e.firma (FIEL) del contribuyente: certificado + llave privada.

    Nunca expone la llave ni la contraseña; solo firma.
    """

    def __init__(self, cert_der: bytes, key_der: bytes, password: str) -> None:
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import serialization
        except ImportError:
            raise ConfigError(
                "Falta `cryptography`. Instala: pip install 'plugins-mx-mcp-servers[sat-ws]'"
            )
        try:
            self._cert = x509.load_der_x509_certificate(cert_der)
        except ValueError:
            raise ConfigError("El .cer de la e.firma no es un certificado X.509 DER válido.")
        try:
            self._key = serialization.load_der_private_key(key_der, password.encode("utf-8"))
        except (ValueError, TypeError):
            raise ConfigError(
                "No se pudo abrir el .key de la e.firma: contraseña incorrecta o "
                "formato distinto a PKCS#8 DER cifrado."
            ) from None
        if self._key.public_key().public_numbers() != self._cert.public_key().public_numbers():
            raise ConfigError("El .cer y el .key de la e.firma no corresponden entre sí.")

    @classmethod
    def from_env(cls) -> "Fiel":
        rutas = {v: os.environ.get(v, "").strip() for v in ("SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY")}
        password = os.environ.get("SAT_EFIRMA_PASSWORD", "")
        faltan = [v for v, r in rutas.items() if not r] + ([] if password else ["SAT_EFIRMA_PASSWORD"])
        if faltan:
            raise ConfigError(f"Faltan variables de e.firma: {', '.join(faltan)}", {"missing": faltan})
        cert, key = (Path(rutas[v]).expanduser() for v in ("SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY"))
        for ruta in (cert, key):
            if not ruta.is_file():
                raise ConfigError(f"No existe el archivo de e.firma: {ruta.name}")
        return cls(cert.read_bytes(), key.read_bytes(), password)

    @property
    def rfc(self) -> str:
        # SAT guarda "RFC / RFC_REPRESENTANTE" en x500UniqueIdentifier (2.5.4.45).
        for attr in self._cert.subject:
            if attr.oid.dotted_string == "2.5.4.45":
                return str(attr.value).split("/")[0].strip().upper()
        raise ConfigError("El certificado no trae RFC (OID 2.5.4.45); ¿es una e.firma del SAT?")

    @property
    def certificado_b64(self) -> str:
        from cryptography.hazmat.primitives.serialization import Encoding

        return base64.b64encode(self._cert.public_bytes(Encoding.DER)).decode("ascii")

    @property
    def numero_serie(self) -> str:
        return str(self._cert.serial_number)

    @property
    def emisor(self) -> str:
        return ",".join(
            f"{_OID_NOMBRES.get(a.oid.dotted_string, a.oid.dotted_string)}={a.value}"
            for a in self._cert.issuer
        )

    def firmar_sha1(self, datos: bytes) -> bytes:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        return self._key.sign(datos, padding.PKCS1v15(), hashes.SHA1())


class SatWsClient:
    """Cliente del Web Service SAT Descarga Masiva CFDI."""

    CRED_ENV_VARS = ["SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
        fiel: Fiel | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)
        self._fiel = fiel
        self._forzar_real = fiel is not None  # e.firma inyectada = modo real
        self._token_cache: tuple[str, float] | None = None

    def _mock(self) -> bool:
        return not self._forzar_real and is_mock_mode(self.CRED_ENV_VARS)

    def _get_fiel(self) -> Fiel:
        if self._fiel is None:
            self._fiel = Fiel.from_env()
        return self._fiel

    # ============================================================
    # Tools del MCP
    # ============================================================

    def solicitar_descarga(self, solicitud: SolicitudDescarga | dict) -> dict[str, Any]:
        """Inicia una solicitud de descarga masiva.

        Returns:
            {"id_solicitud", "cod_estatus" (5000 = aceptada), "mensaje",
             "rfc_emisor", "rango", "tipo_solicitud", "fecha_solicitud", "simulated"}
        """
        if isinstance(solicitud, dict):
            solicitud = SolicitudDescarga(**solicitud)
        solicitud.validar()

        self._bitacora.log(
            "solicitar_descarga",
            success=True,
            params_summary={
                "rfc_emisor_hash": self._bitacora.hash_sensitive(solicitud.rfc_emisor),
                "rango": f"{solicitud.fecha_inicial} → {solicitud.fecha_final}",
                "tipo": solicitud.tipo_solicitud,
            },
        )

        if self._mock():
            return self._mock_solicitud(solicitud)
        return self._real_solicitud(solicitud)

    def verificar_solicitud(self, id_solicitud: str, rfc_emisor: str) -> dict[str, Any]:
        """Polling del estado de una solicitud.

        Returns:
            {"id_solicitud", "cod_estatus_solicitud" (1..6), "estado_legible",
             "es_terminal", "numero_cfdis", "paquetes", "fecha_consulta", "simulated"}
        """
        if not id_solicitud or not rfc_emisor:
            raise ValidationError("id_solicitud y rfc_emisor requeridos.")

        self._bitacora.log(
            "verificar_solicitud",
            success=True,
            params_summary={
                "id_hash": self._bitacora.hash_sensitive(id_solicitud),
                "rfc_hash": self._bitacora.hash_sensitive(rfc_emisor),
            },
        )

        if self._mock():
            return self._mock_verificar(id_solicitud)
        return self._real_verificar(id_solicitud, rfc_emisor)

    def descargar_paquete(self, id_paquete: str, rfc_emisor: str) -> dict[str, Any]:
        """Descarga un paquete ZIP con CFDIs.

        Returns:
            {"id_paquete", "zip_base64", "fecha_descarga", "simulated"}
        """
        if not id_paquete or not rfc_emisor:
            raise ValidationError("id_paquete y rfc_emisor requeridos.")

        self._bitacora.log(
            "descargar_paquete",
            success=True,
            params_summary={"id_hash": self._bitacora.hash_sensitive(id_paquete)},
        )

        if self._mock():
            return self._mock_descargar(id_paquete)
        return self._real_descargar(id_paquete, rfc_emisor)

    # ============================================================
    # Firma XMLDSig (port de phpcfdi FielRequestBuilder::createSignature)
    # ============================================================

    def _firmar_soap_request(self, a_firmar: str, uri: str = "", key_info: str = "") -> str:
        """Devuelve el nodo <Signature> para `a_firmar` (XML ya canónico).

        `a_firmar` debe ser el nodo referenciado en forma exc-c14n: sin espacios
        entre nodos, con sus xmlns declarados y atributos en orden.
        """
        fiel = self._get_fiel()
        digest = base64.b64encode(hashlib.sha1(a_firmar.encode("utf-8")).digest()).decode()
        signed_info = (
            f'<SignedInfo xmlns="{NS_DS}">'
            '<CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></CanonicalizationMethod>'
            '<SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></SignatureMethod>'
            f'<Reference URI="{uri}"><Transforms>'
            '<Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></Transform>'
            '</Transforms>'
            '<DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></DigestMethod>'
            f"<DigestValue>{digest}</DigestValue></Reference></SignedInfo>"
        )
        firma = base64.b64encode(fiel.firmar_sha1(signed_info.encode("utf-8"))).decode()
        # Dentro de <Signature xmlns=ds> el xmlns del SignedInfo es redundante.
        signed_info = signed_info.replace(f'<SignedInfo xmlns="{NS_DS}">', "<SignedInfo>", 1)
        if not key_info:
            key_info = (
                "<KeyInfo><X509Data><X509IssuerSerial>"
                f"<X509IssuerName>{_x(fiel.emisor)}</X509IssuerName>"
                f"<X509SerialNumber>{fiel.numero_serie}</X509SerialNumber>"
                "</X509IssuerSerial>"
                f"<X509Certificate>{fiel.certificado_b64}</X509Certificate>"
                "</X509Data></KeyInfo>"
            )
        return (
            f'<Signature xmlns="{NS_DS}">{signed_info}'
            f"<SignatureValue>{firma}</SignatureValue>{key_info}</Signature>"
        )

    def _xml_autentica(self, creado: datetime, expira: datetime, token_id: str) -> str:
        c = creado.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        e = expira.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        timestamp = f"<u:Created>{c}</u:Created><u:Expires>{e}</u:Expires>"
        key_info = (
            "<KeyInfo><o:SecurityTokenReference>"
            f'<o:Reference URI="#{token_id}" ValueType="{_X509V3}"/>'
            "</o:SecurityTokenReference></KeyInfo>"
        )
        firma = self._firmar_soap_request(
            f'<u:Timestamp xmlns:u="{NS_WSU}" u:Id="_0">{timestamp}</u:Timestamp>', "#_0", key_info
        )
        return (
            f'<s:Envelope xmlns:s="{NS_SOAP}" xmlns:u="{NS_WSU}"><s:Header>'
            f'<o:Security xmlns:o="{NS_WSSE}" s:mustUnderstand="1">'
            f'<u:Timestamp u:Id="_0">{timestamp}</u:Timestamp>'
            f'<o:BinarySecurityToken u:Id="{token_id}" ValueType="{_X509V3}" EncodingType="{_B64BIN}">'
            f"{self._get_fiel().certificado_b64}</o:BinarySecurityToken>{firma}"
            f'</o:Security></s:Header><s:Body><Autentica xmlns="{NS_AUTH}"/></s:Body></s:Envelope>'
        )

    def _xml_firmado(self, operacion: str, nodo: str, attrs: dict[str, str], extra: str = "") -> str:
        """Envelope des:<operacion>/des:<nodo attrs> con la firma dentro de <nodo>."""
        a = " ".join(f'{k}="{_x(v)}"' for k, v in sorted(attrs.items()) if v)
        firma = self._firmar_soap_request(
            f'<des:{operacion} xmlns:des="{NS_DES}"><des:{nodo} {a}>{extra}</des:{nodo}></des:{operacion}>'
        )
        return (
            f'<s:Envelope xmlns:s="{NS_SOAP}" xmlns:des="{NS_DES}" xmlns:xd="{NS_DS}">'
            f"<s:Header/><s:Body><des:{operacion}><des:{nodo} {a}>{extra}{firma}</des:{nodo}>"
            f"</des:{operacion}></s:Body></s:Envelope>"
        )

    # ============================================================
    # Transporte SOAP
    # ============================================================

    def _post(self, url: str, accion: str, cuerpo: str, token: str | None = None) -> ET.Element:
        headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": accion}
        if token:
            headers["Authorization"] = f'WRAP access_token="{token}"'
        try:
            resp = httpx.post(url, content=cuerpo.encode("utf-8"), headers=headers, timeout=TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            raise handle_httpx_error(exc)
        try:
            raiz = ET.fromstring(resp.content)
        except ET.ParseError:
            raise UpstreamError(
                f"El SAT respondió HTTP {resp.status_code} sin XML válido.",
                {"http_status": resp.status_code, "body_preview": resp.text[:300]},
            )
        fault = raiz.find(f".//{{{NS_SOAP}}}Fault")
        if fault is not None:
            code = (fault.findtext("faultcode") or "").strip()
            msg = (fault.findtext("faultstring") or "").strip()
            cls = AuthError if "Security" in code else UpstreamError
            raise cls(f"SOAP Fault del SAT ({code}): {msg}", {"faultcode": code, "http_status": resp.status_code})
        if resp.status_code >= 400:
            raise UpstreamError(f"El SAT respondió HTTP {resp.status_code}.", {"http_status": resp.status_code})
        return raiz

    @staticmethod
    def _exigir_5000(nodo: ET.Element | None, operacion: str) -> dict[str, str]:
        if nodo is None:
            raise UpstreamError(f"Respuesta del SAT a {operacion} sin el nodo de resultado esperado.")
        cod = int(nodo.get("CodEstatus") or 0)
        if cod != 5000:
            raise UpstreamError(
                f"SAT rechazó {operacion}: CodEstatus {cod} — {nodo.get('Mensaje', '')}",
                {"cod_estatus_sat": cod, "mensaje_sat": nodo.get("Mensaje"), "descripcion": CODIGOS_SAT.get(cod)},
            )
        return dict(nodo.attrib)

    def _token(self) -> str:
        """Token de Autenticación (vigencia 5 min; se reutiliza 4 min)."""
        if self._token_cache and self._token_cache[1] > time.monotonic():
            return self._token_cache[0]
        creado = datetime.now(timezone.utc)
        cuerpo = self._xml_autentica(creado, creado + timedelta(minutes=5), f"uuid-{uuid.uuid4()}-1")
        raiz = self._post(URL_AUTENTICACION, ACCION_AUTENTICA, cuerpo)
        token = (raiz.findtext(f".//{{{NS_AUTH}}}AutenticaResult") or "").strip()
        if not token:
            raise AuthError("El SAT no devolvió token de autenticación.")
        self._token_cache = (token, time.monotonic() + 240)
        return token

    # ============================================================
    # Real path
    # ============================================================

    def _real_solicitud(self, sol: SolicitudDescarga) -> dict[str, Any]:
        rfc = self._get_fiel().rfc
        if sol.rfc_emisor.upper() != rfc:
            raise ValidationError(
                "rfc_emisor no coincide con el RFC de la e.firma cargada.",
                {"rfc_efirma": rfc},
            )
        emitidos = sol.tipo_descarga == "emitidos"
        attrs = {
            "RfcSolicitante": rfc,
            "TipoSolicitud": sol.tipo_solicitud,
            "FechaInicial": sol.fecha_inicial,
            "FechaFinal": sol.fecha_final,
            "RfcEmisor": rfc if emitidos else sol.rfc_emisor_filtro.upper(),
            "RfcReceptor": "" if emitidos else rfc,
            "TipoComprobante": sol.tipo_comprobante or "",
            # El SAT rechaza recibidos XML que incluyan cancelados.
            "EstadoComprobante": "Vigente" if not emitidos and sol.tipo_solicitud == "CFDI" else "Todos",
        }
        extra = ""
        if emitidos and sol.rfc_receptor:
            extra = f"<des:RfcReceptores><des:RfcReceptor>{_x(sol.rfc_receptor.upper())}</des:RfcReceptor></des:RfcReceptores>"
        operacion = "SolicitaDescargaEmitidos" if emitidos else "SolicitaDescargaRecibidos"
        raiz = self._post(
            URL_SOLICITAR_DESCARGA,
            f"{NS_DES}/ISolicitaDescargaService/{operacion}",
            self._xml_firmado(operacion, "solicitud", attrs, extra),
            self._token(),
        )
        r = self._exigir_5000(raiz.find(f".//{{{NS_DES}}}{operacion}Result"), operacion)
        return {
            "id_solicitud": r.get("IdSolicitud"),
            "cod_estatus": 5000,
            "mensaje": r.get("Mensaje"),
            "rfc_emisor": rfc,
            "rango": f"{sol.fecha_inicial} → {sol.fecha_final}",
            "tipo_solicitud": sol.tipo_solicitud,
            "tipo_descarga": sol.tipo_descarga,
            "fecha_solicitud": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def _real_verificar(self, id_solicitud: str, rfc: str) -> dict[str, Any]:
        rfc_fiel = self._get_fiel().rfc
        raiz = self._post(
            URL_VERIFICAR_SOLICITUD,
            ACCION_VERIFICA,
            self._xml_firmado(
                "VerificaSolicitudDescarga", "solicitud",
                {"IdSolicitud": id_solicitud, "RfcSolicitante": rfc_fiel},
            ),
            self._token(),
        )
        nodo = raiz.find(f".//{{{NS_DES}}}VerificaSolicitudDescargaResult")
        r = self._exigir_5000(nodo, "VerificaSolicitudDescarga")
        estado = int(r.get("EstadoSolicitud") or 0)
        codigo = int(r.get("CodigoEstadoSolicitud") or 0)
        return {
            "id_solicitud": id_solicitud,
            "cod_estatus_solicitud": estado,
            "estado_legible": parsear_estado_solicitud(estado),
            "es_terminal": estado_es_terminal(estado),
            "codigo_estado_solicitud": codigo,
            "descripcion_codigo": CODIGOS_SAT.get(codigo),
            "numero_cfdis": int(r.get("NumeroCFDIs") or 0),
            "paquetes": [p.text.strip() for p in nodo.findall(f"{{{NS_DES}}}IdsPaquetes") if p.text],
            "mensaje": r.get("Mensaje"),
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def _real_descargar(self, id_paquete: str, rfc: str) -> dict[str, Any]:
        rfc_fiel = self._get_fiel().rfc
        raiz = self._post(
            URL_DESCARGAR_MASIVA,
            ACCION_DESCARGA,
            self._xml_firmado(
                "PeticionDescargaMasivaTercerosEntrada", "peticionDescarga",
                {"IdPaquete": id_paquete, "RfcSolicitante": rfc_fiel},
            ),
            self._token(),
        )
        self._exigir_5000(raiz.find(f".//{{{NS_DES}}}respuesta"), "Descargar")
        zip_b64 = (raiz.findtext(f".//{{{NS_DES}}}Paquete") or "").strip()
        if not zip_b64:
            raise UpstreamError("El SAT aceptó la descarga pero no devolvió el paquete.", {"id_paquete": id_paquete})
        return {
            "id_paquete": id_paquete,
            "zip_base64": zip_b64,
            "tamano_bytes": len(base64.b64decode(zip_b64)),
            "fecha_descarga": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    # ============================================================
    # Mock path
    # ============================================================

    def _mock_solicitud(self, sol: SolicitudDescarga) -> dict[str, Any]:
        return mark_simulated({
            "id_solicitud": str(uuid.uuid4()),
            "cod_estatus": 5000,
            "mensaje": "Solicitud Aceptada (mock).",
            "rfc_emisor": sol.rfc_emisor,
            "rango": f"{sol.fecha_inicial} → {sol.fecha_final}",
            "tipo_solicitud": sol.tipo_solicitud,
            "tipo_descarga": sol.tipo_descarga,
            "fecha_solicitud": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_verificar(self, id_solicitud: str) -> dict[str, Any]:
        # Determinístico: id que termine en par → TERMINADA, impar → EN_PROCESO
        last = id_solicitud[-1].lower()
        if last in "02468ace":
            estado = ESTADO_TERMINADA
            paquetes = [f"{id_solicitud}_01", f"{id_solicitud}_02"]
            numero_cfdis = 1247
        elif last in "13579":
            estado = ESTADO_EN_PROCESO
            paquetes = []
            numero_cfdis = 0
        else:
            estado = ESTADO_ACEPTADA
            paquetes = []
            numero_cfdis = 0

        return mark_simulated({
            "id_solicitud": id_solicitud,
            "cod_estatus_solicitud": estado,
            "estado_legible": parsear_estado_solicitud(estado),
            "es_terminal": estado_es_terminal(estado),
            "numero_cfdis": numero_cfdis,
            "paquetes": paquetes,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_descargar(self, id_paquete: str) -> dict[str, Any]:
        # Base64 trivial de un "ZIP" simulado
        zip_b64_mock = "UEsDBBQAAAAIAA=="  # header de ZIP truncado
        return mark_simulated({
            "id_paquete": id_paquete,
            "zip_base64": zip_b64_mock,
            "cfdis_estimados": 1000,
            "fecha_descarga": datetime.now(timezone.utc).isoformat(),
        })
