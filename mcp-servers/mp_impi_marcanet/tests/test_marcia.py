"""Path real IMPI (MARCia) con respuestas reales capturadas 2026-10-14 (titulares personas morales)."""

from pathlib import Path

import httpx
import pytest
import respx

from mp_impi_marcanet import marcia
from mp_impi_marcanet.client import ImpiMarcanetClient
from shared.errors import UpstreamError

FX = Path(__file__).parent / "fixtures"
JSON = {"content-type": "application/json"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    return ImpiMarcanetClient()


def _portal(router, xsrf=True):
    headers = {"set-cookie": "XSRF-TOKEN=tok-123; Path=/marcas"} if xsrf else {}
    router.get(marcia.PORTAL_URL).respond(200, text="<html></html>", headers=headers)
    rec = router.post(f"{marcia.BASE}/marcas/search/internal/record").respond(
        200, content=(FX / "marcia_record_telmex_2026-10-14.json").read_bytes(), headers=JSON)
    router.post(f"{marcia.BASE}/marcas/search/internal/result").respond(
        200, content=(FX / "marcia_result_telmex_2026-10-14.json").read_bytes(), headers=JSON)
    return rec


def test_buscar_real(client):
    with respx.mock() as router:
        rec = _portal(router)
        r = client.buscar("telmex", limite=5)
        assert rec.calls[0].request.headers["X-XSRF-TOKEN"] == "tok-123"
    assert r["simulated"] is False
    assert r["total_encontrados"] == 5305
    m = r["resultados"][0]
    assert m["denominacion"] == "TELMEX"
    assert m["numero_registro"] == "340988"
    assert m["estatus"] == "REGISTRADO"
    assert m["titular"] == "MARTEX POTOSI, S.A. DE C.V."


def test_verificar_denominacion_real(client):
    with respx.mock() as router:
        _portal(router)
        r = client.verificar_denominacion("TELMEX")
    assert r["coincidencias_exactas"] == 5


def test_sin_xsrf_es_upstream(client):
    with respx.mock(assert_all_called=False) as router:
        _portal(router, xsrf=False)
        with pytest.raises(UpstreamError):
            client.buscar("telmex")


def test_marcia_caido(client):
    with respx.mock() as router:
        router.get(marcia.PORTAL_URL).mock(side_effect=httpx.ConnectError("down"))
        with pytest.raises(UpstreamError):
            client.buscar("telmex")


@pytest.mark.live
def test_live_marcia(client):
    r = client.buscar("TELMEX", limite=5)
    assert r["total_encontrados"] > 0
    assert any("TELMEX" in m["denominacion"] for m in r["resultados"])
