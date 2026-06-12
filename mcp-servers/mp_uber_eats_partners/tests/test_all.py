import pytest

from mp_uber_eats_partners.client import UberEatsPartnersClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ["UBER_EATS_CLIENT_ID", "UBER_EATS_CLIENT_SECRET", "UBER_EATS_STORE_ID"]:
        monkeypatch.delenv(v, raising=False)


def test_listar_ordenes_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = UberEatsPartnersClient()
    r = c.listar_ordenes(limite=4)
    assert r.get("simulated") is True
    assert len(r["ordenes"]) == 4
    assert all(o["orden_id"].startswith("UE-MOCK-") for o in r["ordenes"])


def test_uber_estados_uppercase(clean_env):
    """Uber Eats usa estados en MAYÚSCULAS — DELIVERED, IN_PROGRESS."""
    c = UberEatsPartnersClient()
    r = c.listar_ordenes(limite=10)
    estados = {o["estado"] for o in r["ordenes"]}
    assert all(e == e.upper() for e in estados)


def test_listar_filtra_estado_case_insensitive(clean_env):
    c = UberEatsPartnersClient()
    r = c.listar_ordenes(estado="delivered")  # lowercase
    assert all(o["estado"] == "DELIVERED" for o in r["ordenes"])


def test_consultar_orden_mock(clean_env):
    c = UberEatsPartnersClient()
    r = c.consultar_orden("UE-001")
    assert r["orden_id"] == "UE-001"
    assert r["estado"] == "DELIVERED"


def test_listar_menu(clean_env):
    c = UberEatsPartnersClient()
    r = c.listar_productos_menu()
    assert r["total"] == 2


def test_actualizar_disponibilidad(clean_env):
    c = UberEatsPartnersClient()
    r = c.actualizar_disponibilidad("PROD", True)
    assert r["disponible"] is True


def test_ranking(clean_env):
    c = UberEatsPartnersClient()
    r = c.consultar_ranking_zona()
    assert "rating_promedio" in r


def test_comisiones(clean_env):
    c = UberEatsPartnersClient()
    r = c.estimar_comisiones_mes()
    assert r["comision_porcentaje"] == 30.0


def test_real_lanza_si_credenciales(monkeypatch):
    monkeypatch.setenv("UBER_EATS_CLIENT_ID", "x")
    monkeypatch.setenv("UBER_EATS_CLIENT_SECRET", "y")
    monkeypatch.setenv("UBER_EATS_STORE_ID", "z")
    c = UberEatsPartnersClient()
    with pytest.raises(McpError):
        c.listar_ordenes()
