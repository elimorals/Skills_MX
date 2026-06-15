"""Tests mp_telmex_facturacion."""
from __future__ import annotations

import pytest

from mp_telmex_facturacion.client import TelmexFactClient
from shared.errors import McpError, ValidationError


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    for v in ["TELMEX_TELEFONO", "TELMEX_PASSWORD", "PLUGINS_MX_TELMEX_LIVE"]:
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


def test_descargar_factura_mock_default():
    c = TelmexFactClient()
    r = c.descargar_factura_mes("5512345678")
    assert r["simulated"] is True
    assert "monto_total_mxn" in r
    assert r["telefono"] == "5512345678"


def test_descargar_factura_con_periodo():
    c = TelmexFactClient()
    r = c.descargar_factura_mes("5512345678", periodo="2026-03")
    assert r["periodo"] == "2026-03"
    assert "url_pdf" in r and "url_xml" in r


def test_telefono_normalizacion():
    c = TelmexFactClient()
    r1 = c.descargar_factura_mes("+5255-1234-5678")
    r2 = c.descargar_factura_mes("5551234578")  # otro distinto
    assert r1["telefono"] == "5512345678"
    assert r2["telefono"] == "5551234578"


def test_telefono_invalido_lanza():
    c = TelmexFactClient()
    with pytest.raises(ValueError):
        c.descargar_factura_mes("123")


def test_consumo_historico_mock():
    c = TelmexFactClient()
    r = c.consumo_historico("5512345678", meses=6)
    assert r["simulated"] is True
    assert len(r["consumos"]) >= 1


def test_consumo_meses_invalido():
    c = TelmexFactClient()
    with pytest.raises(ValidationError):
        c.consumo_historico("5512345678", meses=100)


def test_listar_facturas_mock():
    c = TelmexFactClient()
    r = c.listar_facturas("5512345678")
    assert r["simulated"] is True
    assert len(r["facturas_disponibles"]) >= 1


def test_live_flag_sin_creds_se_queda_en_mock(monkeypatch):
    """LIVE flag activo pero sin credenciales → cae a mock por is_mock_mode."""
    monkeypatch.setenv("PLUGINS_MX_TELMEX_LIVE", "1")
    c = TelmexFactClient()
    r = c.descargar_factura_mes("5512345678")
    assert r["simulated"] is True


def test_live_flag_con_creds_lanza_error_real_pendiente(monkeypatch):
    """LIVE + creds → entra a path real, que lanza McpError porque selectores TBD."""
    monkeypatch.setenv("PLUGINS_MX_TELMEX_LIVE", "1")
    monkeypatch.setenv("TELMEX_TELEFONO", "5512345678")
    monkeypatch.setenv("TELMEX_PASSWORD", "xxx")
    c = TelmexFactClient()
    with pytest.raises(McpError):
        c.descargar_factura_mes("5512345678")
