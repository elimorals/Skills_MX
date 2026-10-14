"""sat_descargar_cfdi_masivo conectado a mp_sat_ws (e.firma de prueba + respx)."""
from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

pytest.importorskip("cryptography")

from mp_sat_portal.client import SatPortalClient  # noqa: E402
from mp_sat_portal.server import DescargaMasivaInput, sat_descargar_cfdi_masivo  # noqa: E402
from shared.sat_ws import URL_AUTENTICACION, URL_SOLICITAR_DESCARGA  # noqa: E402

WS_FIX = Path(__file__).resolve().parents[2] / "mp_sat_ws" / "tests" / "fixtures"


@pytest.fixture
def efirma_prueba(monkeypatch):
    monkeypatch.setenv("SAT_EFIRMA_CERT", str(WS_FIX / "EKU9003173C9.cer"))
    monkeypatch.setenv("SAT_EFIRMA_KEY", str(WS_FIX / "EKU9003173C9.key"))
    monkeypatch.setenv("SAT_EFIRMA_PASSWORD", "12345678a")


@respx.mock
def test_solicitud_real_recibidos_del_mes(efirma_prueba):
    respx.post(URL_AUTENTICACION).mock(
        return_value=httpx.Response(200, content=(WS_FIX / "autenticacion-token.xml").read_bytes())
    )
    sol = respx.post(URL_SOLICITAR_DESCARGA).mock(return_value=httpx.Response(
        200,
        content=(WS_FIX / "solicitud-emitidos.xml").read_text().replace("Emitidos", "Recibidos").encode(),
    ))
    r = SatPortalClient().descargar_cfdi_masivo("EKU9003173C9", 2026, 2, "recibidos")
    assert r["simulated"] is False
    assert r["solicitud_id"] == "d49af78d-1c80-4221-a48d-345ace91626b"
    body = sol.calls.last.request.content
    assert b'FechaInicial="2026-02-01T00:00:00"' in body and b'FechaFinal="2026-02-28T23:59:59"' in body
    assert b"<des:SolicitaDescargaRecibidos>" in body


@respx.mock
async def test_tool_devuelve_codigo_sat_en_error(efirma_prueba):
    respx.post(URL_AUTENTICACION).mock(
        return_value=httpx.Response(200, content=(WS_FIX / "autenticacion-token.xml").read_bytes())
    )
    respx.post(URL_SOLICITAR_DESCARGA).mock(return_value=httpx.Response(
        200,
        content=(WS_FIX / "solicitud-emitidos.xml").read_text()
        .replace('CodEstatus="5000"', 'CodEstatus="5005"').encode(),
    ))
    r = await sat_descargar_cfdi_masivo(
        DescargaMasivaInput(rfc="EKU9003173C9", ejercicio=2026, mes=1, tipo="emitidos")
    )
    assert r["error"] is True
    assert r["details"]["cod_estatus_sat"] == 5005


async def test_sin_efirma_completa_es_error_no_mock(monkeypatch):
    monkeypatch.setenv("SAT_RFC", "EKU9003173C9")  # credencial parcial → modo real
    r = await sat_descargar_cfdi_masivo(
        DescargaMasivaInput(rfc="EKU9003173C9", ejercicio=2026, mes=1, tipo="emitidos")
    )
    assert r["error"] is True and r["code"] == "config_error"
