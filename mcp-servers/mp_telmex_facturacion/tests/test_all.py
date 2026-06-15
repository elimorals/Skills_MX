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


def test_live_flag_off_mantiene_mock(monkeypatch):
    """Sin PLUGINS_MX_TELMEX_LIVE → siempre mock."""
    monkeypatch.delenv("PLUGINS_MX_TELMEX_LIVE", raising=False)
    c = TelmexFactClient()
    r = c.descargar_factura_mes("5512345678")
    assert r["simulated"] is True


def test_consumo_real_path_requiere_login(monkeypatch):
    """Consumo histórico real requiere Mi Telmex login → lanza McpError."""
    monkeypatch.setenv("PLUGINS_MX_TELMEX_LIVE", "1")
    c = TelmexFactClient()
    # Necesitamos vaciar cache para que entre al path real
    c._cache.clear() if hasattr(c._cache, "clear") else None
    with pytest.raises(McpError):
        c.consumo_historico("5599887766", meses=6)


def test_parser_extrae_monto():
    """El parser de HTML extrae monto, vencimiento, num_servicio."""
    from mp_telmex_facturacion.client import _parse_telmex_factura_html
    html = """
    <html><body>
      <h2>Tu Recibo Telmex</h2>
      <p>Total a pagar: $ 689.50</p>
      <p>Fecha de vencimiento: 30/06/2026</p>
      <p>Número de servicio: 5512345678</p>
      <p>Periodo: 2026-05</p>
    </body></html>
    """
    r = _parse_telmex_factura_html(html, "5512345678")
    assert r["monto_total_mxn"] == 689.50
    assert r["fecha_vencimiento"] == "30/06/2026"
    assert r["numero_servicio"] == "5512345678"
    assert r["periodo_detectado"] == "2026-05"
    assert "parse_partial" not in r


def test_parser_html_sin_monto_marca_partial():
    from mp_telmex_facturacion.client import _parse_telmex_factura_html
    r = _parse_telmex_factura_html("<html>Sin datos relevantes</html>", "5512345678")
    assert r.get("parse_partial") is True
