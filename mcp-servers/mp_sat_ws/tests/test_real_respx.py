"""Flujo real (Autenticación → Solicitud → Verificación → Descarga) contra respx.

Las respuestas son XML reales del SAT capturados por phpcfdi/sat-ws-descarga-masiva
(MIT) en sus pruebas de integración.
"""
from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

pytest.importorskip("cryptography")

from mp_sat_ws.client import SatWsClient  # noqa: E402
from mp_sat_ws.tests.test_firma import fiel_prueba  # noqa: E402
from shared.errors import AuthError, UpstreamError, ValidationError  # noqa: E402
from shared.sat_ws import (  # noqa: E402
    URL_AUTENTICACION,
    URL_DESCARGAR_MASIVA,
    URL_SOLICITAR_DESCARGA,
    URL_VERIFICAR_SOLICITUD,
    SolicitudDescarga,
)

FIX = Path(__file__).parent / "fixtures"
SOL = SolicitudDescarga(
    rfc_emisor="EKU9003173C9",
    fecha_inicial="2026-01-01T00:00:00",
    fecha_final="2026-01-31T23:59:59",
)


def _xml(nombre: str, status: int = 200) -> httpx.Response:
    return httpx.Response(status, content=(FIX / nombre).read_bytes())


@pytest.fixture(autouse=True)
def _aislado(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


@pytest.fixture
def cliente() -> SatWsClient:
    return SatWsClient(fiel=fiel_prueba())


@respx.mock
def test_flujo_completo(cliente):
    auth = respx.post(URL_AUTENTICACION).mock(return_value=_xml("autenticacion-token.xml"))
    sol = respx.post(URL_SOLICITAR_DESCARGA).mock(return_value=_xml("solicitud-emitidos.xml"))
    ver = respx.post(URL_VERIFICAR_SOLICITUD).mock(return_value=_xml("verificacion-2-paquetes.xml"))
    des = respx.post(URL_DESCARGAR_MASIVA).mock(return_value=_xml("descarga-paquete.xml"))

    r = cliente.solicitar_descarga(SOL)
    assert r["id_solicitud"] == "d49af78d-1c80-4221-a48d-345ace91626b"
    assert r["simulated"] is False

    req = sol.calls.last.request
    assert req.headers["SOAPAction"].endswith("/ISolicitaDescargaService/SolicitaDescargaEmitidos")
    assert req.headers["Authorization"].startswith('WRAP access_token="eyJhbGci')
    assert b'RfcSolicitante="EKU9003173C9"' in req.content
    assert auth.calls.last.request.headers["SOAPAction"].endswith("/IAutenticacion/Autentica")

    v = cliente.verificar_solicitud(r["id_solicitud"], "EKU9003173C9")
    assert v["cod_estatus_solicitud"] == 3 and v["es_terminal"] is True
    assert v["numero_cfdis"] == 12345
    assert v["paquetes"] == [
        "4e80345d-917f-40bb-a98f-4a73939343c5_01",
        "4e80345d-917f-40bb-a98f-4a73939343c5_02",
    ]

    d = cliente.descargar_paquete(v["paquetes"][0], "EKU9003173C9")
    assert d["zip_base64"].startswith("UEsDB")  # firma ZIP "PK\x03\x04"
    assert d["tamano_bytes"] > 0
    # El token se reutiliza dentro de su vigencia: una sola autenticación.
    assert auth.call_count == 1 and ver.call_count == 1 and des.call_count == 1


@respx.mock
def test_recibidos_xml_solo_vigentes(cliente):
    respx.post(URL_AUTENTICACION).mock(return_value=_xml("autenticacion-token.xml"))
    sol = respx.post(URL_SOLICITAR_DESCARGA).mock(return_value=httpx.Response(
        200,
        content=(FIX / "solicitud-emitidos.xml").read_text().replace("Emitidos", "Recibidos").encode(),
    ))
    SatWsClient(fiel=fiel_prueba()).solicitar_descarga({**SOL.__dict__, "tipo_descarga": "recibidos"})
    body = sol.calls.last.request.content
    assert b"<des:SolicitaDescargaRecibidos>" in body
    assert b'EstadoComprobante="Vigente"' in body and b'RfcReceptor="EKU9003173C9"' in body


@respx.mock
def test_verificacion_sin_paquetes_5004(cliente):
    respx.post(URL_AUTENTICACION).mock(return_value=_xml("autenticacion-token.xml"))
    respx.post(URL_VERIFICAR_SOLICITUD).mock(return_value=_xml("verificacion-0-paquetes.xml"))
    v = cliente.verificar_solicitud("abc12345", "EKU9003173C9")
    assert v["cod_estatus_solicitud"] == 5 and v["estado_legible"] == "RECHAZADA"
    assert v["codigo_estado_solicitud"] == 5004 and v["paquetes"] == []


@pytest.mark.parametrize("cod", [5002, 5005, 404, 305])
@respx.mock
def test_codigo_sat_distinto_de_5000_es_error_explicito(cliente, cod):
    respx.post(URL_AUTENTICACION).mock(return_value=_xml("autenticacion-token.xml"))
    respx.post(URL_SOLICITAR_DESCARGA).mock(return_value=httpx.Response(
        200,
        content=(FIX / "solicitud-emitidos.xml").read_text()
        .replace('CodEstatus="5000"', f'CodEstatus="{cod}"').encode(),
    ))
    with pytest.raises(UpstreamError) as exc:
        cliente.solicitar_descarga(SOL)
    assert exc.value.details["cod_estatus_sat"] == cod
    assert str(cod) in exc.value.message


@respx.mock
def test_fault_de_autenticacion(cliente):
    respx.post(URL_AUTENTICACION).mock(return_value=_xml("autenticacion-fault.xml", 500))
    with pytest.raises(AuthError) as exc:
        cliente.solicitar_descarga(SOL)
    assert "InvalidSecurity" in exc.value.details["faultcode"]


@respx.mock
def test_red_caida_no_cae_a_mock(cliente):
    respx.post(URL_AUTENTICACION).mock(side_effect=httpx.ConnectError("boom"))
    with pytest.raises(UpstreamError):
        cliente.solicitar_descarga(SOL)


def test_rfc_distinto_a_la_efirma(cliente):
    with pytest.raises(ValidationError):
        cliente.solicitar_descarga({**SOL.__dict__, "rfc_emisor": "AAA010101AAA"})


def test_credenciales_en_env_activan_modo_real(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("SAT_EFIRMA_CERT", str(FIX / "EKU9003173C9.cer"))
    monkeypatch.setenv("SAT_EFIRMA_KEY", str(FIX / "EKU9003173C9.key"))
    monkeypatch.setenv("SAT_EFIRMA_PASSWORD", "12345678a")
    c = SatWsClient()
    assert c._mock() is False
    assert c._get_fiel().rfc == "EKU9003173C9"
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert c._mock() is True
