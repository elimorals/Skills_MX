import pytest

from mp_didi_food_partners.client import DidiFoodPartnersClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ["DIDI_FOOD_TOKEN", "DIDI_FOOD_RESTAURANT_ID"]:
        monkeypatch.delenv(v, raising=False)


def test_listar_ordenes_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = DidiFoodPartnersClient()
    r = c.listar_ordenes(limite=3)
    assert r.get("simulated") is True
    assert len(r["ordenes"]) == 3
    assert all(o["orden_id"].startswith("DDF-MOCK-") for o in r["ordenes"])


def test_listar_filtra_estado(clean_env):
    c = DidiFoodPartnersClient()
    r = c.listar_ordenes(estado="preparando")
    assert all(o["estado"] == "preparando" for o in r["ordenes"])


def test_consultar_orden_mock(clean_env):
    c = DidiFoodPartnersClient()
    r = c.consultar_orden("DDF-001")
    assert r["orden_id"] == "DDF-001"
    assert r.get("simulated") is True


def test_listar_menu(clean_env):
    c = DidiFoodPartnersClient()
    r = c.listar_productos_menu()
    assert r["total"] == 2


def test_actualizar_disponibilidad(clean_env):
    c = DidiFoodPartnersClient()
    r = c.actualizar_disponibilidad("PROD", False)
    assert r["disponible"] is False


def test_ranking(clean_env):
    c = DidiFoodPartnersClient()
    r = c.consultar_ranking_zona()
    assert "ranking_categoria" in r


def test_comisiones(clean_env):
    c = DidiFoodPartnersClient()
    r = c.estimar_comisiones_mes()
    assert r["comision_porcentaje"] == 30.0


def test_real_lanza_si_token(monkeypatch):
    monkeypatch.setenv("DIDI_FOOD_TOKEN", "x")
    monkeypatch.setenv("DIDI_FOOD_RESTAURANT_ID", "y")
    c = DidiFoodPartnersClient()
    with pytest.raises(McpError):
        c.listar_ordenes()
