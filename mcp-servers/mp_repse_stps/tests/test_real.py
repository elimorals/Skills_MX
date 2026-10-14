"""Path real REPSE (httpx) con respuestas reales capturadas 2026-10-14 (persona moral pública)."""

from pathlib import Path

import pytest
import respx

from mp_repse_stps.client import RepseStpsClient
from shared.errors import NotFoundError, UpstreamError

FX = Path(__file__).parent / "fixtures"
BASE = "https://repse.stps.gob.mx"
HOME = '<html><head><meta name="csrf-token" content="TOKEN123"></head></html>'


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    return RepseStpsClient()


def _portal(router, padron="padron_2235_2026-10-14.json"):
    router.get(f"{BASE}/").respond(200, text=HOME)
    router.get(f"{BASE}/busca_razon_social").respond(
        200, content=(FX / "busca_bimbo_2026-10-14.json").read_bytes(),
        headers={"content-type": "application/json"})
    return router.post(f"{BASE}/buscar-padron").respond(
        200, content=(FX / padron).read_bytes(), headers={"content-type": "application/json"})


def test_busqueda_real(client):
    with respx.mock(assert_all_called=False) as router:
        _portal(router)
        r = client.consultar_por_razon_social("bimbo")
    assert r["simulated"] is False
    assert r["encontrados"][0] == {"razon_social": "BIMBO SA DE CV", "id_padron": 2235, "numero_registro": None}


def test_detalle_por_folio(client):
    with respx.mock(assert_all_called=False) as router:
        post = _portal(router)
        r = client.consultar_por_numero_registro("2775")
        assert post.calls[0].request.headers["X-CSRF-TOKEN"] == "TOKEN123"
    assert r["rfc"] == "BIM011108DJ5"
    assert r["vigencia"] == "2027-05-09"
    assert r["aviso_registro"] == "ARRMGST-6/2024"
    assert len(r["servicios"]) == 6


def test_verificar_proveedor_real(client):
    with respx.mock(assert_all_called=False) as router:
        _portal(router)
        r = client.verificar_proveedor("BIMBO SA DE CV")
    assert r["registrado"] is True
    assert r["numero_registro"] == "2775"


def test_folio_inexistente(client):
    with respx.mock(assert_all_called=False) as router:
        _portal(router, "padron_inexistente_2026-10-14.json")
        with pytest.raises(NotFoundError):
            client.consultar_por_numero_registro("123456")


def test_portal_caido(client):
    with respx.mock(assert_all_called=False) as router:
        router.get(f"{BASE}/").respond(502)
        with pytest.raises(UpstreamError):
            client.consultar_por_razon_social("bimbo")


@pytest.mark.live
def test_live_repse(client):
    r = client.consultar_por_razon_social("BIMBO")
    assert r["encontrados"]
    det = client.verificar_proveedor("BIMBO SA DE CV")
    assert det["registrado"] is True
