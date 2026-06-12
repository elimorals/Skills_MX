"""Tests mp_rappi_partners — mock-first."""

import pytest

from mp_rappi_partners.client import RappiPartnersClient
from shared.errors import McpError


@pytest.fixture
def clean_env(monkeypatch):
    for v in ["RAPPI_PARTNERS_TOKEN", "RAPPI_STORE_ID"]:
        monkeypatch.delenv(v, raising=False)


def test_listar_ordenes_mock(clean_env, tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    c = RappiPartnersClient()
    r = c.listar_ordenes(estado="all", limite=5)
    assert r.get("simulated") is True
    assert len(r["ordenes"]) == 5
    assert all("orden_id" in o for o in r["ordenes"])
    assert all(o["orden_id"].startswith("RAP-MOCK-") for o in r["ordenes"])


def test_listar_ordenes_filtra_por_estado(clean_env):
    c = RappiPartnersClient()
    r = c.listar_ordenes(estado="en_camino", limite=10)
    assert all(o["estado"] == "en_camino" for o in r["ordenes"])


def test_consultar_orden_mock(clean_env):
    c = RappiPartnersClient()
    r = c.consultar_orden("RAP-001")
    assert r["orden_id"] == "RAP-001"
    assert r.get("simulated") is True
    assert "items" in r and len(r["items"]) > 0
    assert r["cliente_hash"] != "MOCK_CLIENT"  # debe estar hasheado


def test_listar_menu_mock(clean_env):
    c = RappiPartnersClient()
    r = c.listar_productos_menu()
    assert r["total"] == 3
    assert any(p["disponible"] for p in r["productos"])


def test_actualizar_disponibilidad_mock(clean_env):
    c = RappiPartnersClient()
    r = c.actualizar_disponibilidad("PROD-001", disponible=False)
    assert r["sku"] == "PROD-001"
    assert r["disponible"] is False
    assert "actualizado_en" in r


def test_ranking_zona_mock(clean_env):
    c = RappiPartnersClient()
    r = c.consultar_ranking_zona()
    assert "ranking_categoria" in r
    assert "rating_promedio" in r


def test_comisiones_mes_mock(clean_env):
    c = RappiPartnersClient()
    r = c.estimar_comisiones_mes("2026-06")
    assert r["mes"] == "2026-06"
    assert "neto_mxn" in r
    assert r["comision_porcentaje"] == 30.0


def test_real_path_lanza_error_si_token_seteado(monkeypatch):
    monkeypatch.setenv("RAPPI_PARTNERS_TOKEN", "fake-token")
    monkeypatch.setenv("RAPPI_STORE_ID", "store-123")
    c = RappiPartnersClient()
    with pytest.raises(McpError):
        c.listar_ordenes()


def test_store_id_hasheado_en_logs(tmp_path, monkeypatch):
    from shared.bitacora import Bitacora

    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.setenv("RAPPI_STORE_ID", "store-SECRETO-123")
    monkeypatch.delenv("RAPPI_PARTNERS_TOKEN", raising=False)
    # Forzar mock incluso con store_id presente
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    bita = Bitacora("rappi_partners")
    c = RappiPartnersClient(bitacora=bita)
    r = c.listar_ordenes(limite=1)
    assert "store-SECRETO-123" not in str(r)
    assert r["store_id_hash"]  # hash sí presente
