"""verificar_cfdi_uuid contra ConsultaCFDIService (SOAP público del SAT).

Fixtures `consulta_cfdi_*.xml`: respuestas reales del SAT capturadas el
2026-10-14 con CFDI públicos usados en las pruebas de phpcfdi/sat-estado-cfdi.
"""
from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from mp_sat_portal.client import URL_CONSULTA_CFDI, SatPortalClient
from shared.errors import UpstreamError, ValidationError

FIX = Path(__file__).parent / "fixtures"
VIGENTE = ("CEE4BE01-ADFA-4DEB-8421-ADD60F0BEDAC", "POT9207213D6", "DIM8701081LA", "2010.01")


def _resp(nombre: str) -> httpx.Response:
    return httpx.Response(200, content=(FIX / f"consulta_cfdi_{nombre}.xml").read_bytes())


@respx.mock
def test_vigente():
    ruta = respx.post(URL_CONSULTA_CFDI).mock(return_value=_resp("vigente"))
    r = SatPortalClient().verificar_cfdi_uuid(*VIGENTE)
    assert r["simulated"] is False and r["encontrado"] is True
    assert r["estado_cfdi"] == "Vigente"
    assert r["es_cancelable"] == "Cancelable con aceptación"
    assert r["validacion_efos"] == "200"
    req = ruta.calls.last.request
    assert req.headers["SOAPAction"] == "http://tempuri.org/IConsultaCFDIService/Consulta"
    assert (
        b"?re=POT9207213D6&amp;rr=DIM8701081LA&amp;tt=2010.010000"
        b"&amp;id=CEE4BE01-ADFA-4DEB-8421-ADD60F0BEDAC" in req.content
    )


@respx.mock
def test_cancelado():
    respx.post(URL_CONSULTA_CFDI).mock(return_value=_resp("cancelado"))
    r = SatPortalClient().verificar_cfdi_uuid(
        "3be40815-916c-4c91-84e2-6070d4bc3949", "DIM8701081LA", "XEXX010101000", "8413.00"
    )
    assert r["estado_cfdi"] == "Cancelado" and r["es_cancelable"] is None


@respx.mock
def test_no_encontrado():
    respx.post(URL_CONSULTA_CFDI).mock(return_value=_resp("no_encontrado"))
    r = SatPortalClient().verificar_cfdi_uuid(
        "3be40815-916c-4c91-84e2-6070d4bc3948", "AAA010101AAA", "XEXX010101000", "1"
    )
    assert r["encontrado"] is False
    assert r["estado_cfdi"] == "No Encontrado"
    assert r["codigo_estatus"].startswith("N - 602")


@respx.mock
def test_sat_caido_no_devuelve_mock():
    respx.post(URL_CONSULTA_CFDI).mock(return_value=httpx.Response(503))
    with pytest.raises(UpstreamError):
        SatPortalClient().verificar_cfdi_uuid(*VIGENTE)


def test_total_no_numerico():
    with pytest.raises(ValidationError):
        SatPortalClient().verificar_cfdi_uuid(*VIGENTE[:3], "mil pesos")


@pytest.mark.live
def test_live_consulta_cfdi_vigente():
    r = SatPortalClient().verificar_cfdi_uuid(*VIGENTE)
    assert r["simulated"] is False
    assert r["estado_cfdi"] == "Vigente"
