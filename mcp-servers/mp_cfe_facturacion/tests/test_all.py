"""Tests mp_cfe_facturacion v2 — Playwright + human-in-loop."""
import pytest

from mp_cfe_facturacion.client import CfeFactClient, validar_rpu
from shared.errors import McpError, ValidationError


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    for v in ['CFE_RPU', 'CFE_PASSWORD']:
        monkeypatch.delenv(v, raising=False)
    monkeypatch.delenv("PLUGINS_MX_CFE_LIVE", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


# ============================================================
# Validador RPU
# ============================================================

class TestValidarRPU:
    def test_rpu_valido(self):
        assert validar_rpu("123456789012") == "123456789012"

    def test_rpu_normalize_spaces(self):
        assert validar_rpu("1234 5678 9012") == "123456789012"

    def test_rpu_strip_dashes(self):
        assert validar_rpu("1234-5678-9012") == "123456789012"

    def test_rpu_corto(self):
        with pytest.raises(ValidationError):
            validar_rpu("123")

    def test_rpu_no_numerico(self):
        with pytest.raises(ValidationError):
            validar_rpu("ABC123456789")


# ============================================================
# Descargar factura — mock mode
# ============================================================

class TestDescargarFacturaMock:
    def test_factura_par_pagada(self, clean_env):
        c = CfeFactClient()
        r = c.descargar_factura_mes(rpu="123456789010")  # ends in 0 → PAGADA
        assert r["simulated"] is True
        assert r["estatus"] == "PAGADA"
        assert r["consumo_kwh"] > 0
        assert r["monto_total"] > 0
        assert r["session_used"] == "mock"

    def test_factura_3_vencida(self, clean_env):
        c = CfeFactClient()
        r = c.descargar_factura_mes(rpu="123456789013")  # ends in 3 → VENCIDA
        assert r["estatus"] == "VENCIDA"

    def test_periodo_invalido(self, clean_env):
        c = CfeFactClient()
        with pytest.raises(ValidationError):
            c.descargar_factura_mes(rpu="123456789012", periodo="2026/04")

    def test_periodo_valido(self, clean_env):
        c = CfeFactClient()
        r = c.descargar_factura_mes(rpu="123456789012", periodo="2026-03")
        assert r["periodo"] == "2026-03"

    def test_rpu_invalido(self, clean_env):
        c = CfeFactClient()
        with pytest.raises(ValidationError):
            c.descargar_factura_mes(rpu="X")


# ============================================================
# Consumo histórico — mock mode
# ============================================================

class TestConsumoHistorico:
    def test_meses_default_12(self, clean_env):
        c = CfeFactClient()
        r = c.consumo_historico(rpu="123456789012")
        assert len(r["consumo_kwh_por_mes"]) == 12
        assert r["promedio_kwh_mensual"] > 0
        assert r["tendencia"] in ("ESTABLE", "AUMENTO", "DISMINUCION")

    def test_meses_personalizado(self, clean_env):
        c = CfeFactClient()
        r = c.consumo_historico(rpu="123456789012", meses=6)
        assert len(r["consumo_kwh_por_mes"]) == 6

    def test_meses_fuera_rango(self, clean_env):
        c = CfeFactClient()
        with pytest.raises(ValidationError):
            c.consumo_historico(rpu="123456789012", meses=0)
        with pytest.raises(ValidationError):
            c.consumo_historico(rpu="123456789012", meses=25)


# ============================================================
# Validar session
# ============================================================

class TestValidarSession:
    def test_sin_session_cacheada(self, clean_env):
        c = CfeFactClient()
        r = c.validar_session(rpu="123456789012")
        assert r["session_cached"] is False
        assert r["minutes_until_expiry"] == 0
        assert r["expires_at"] is None


# ============================================================
# Real path — falla esperada en v1 (human-in-loop pendiente)
# ============================================================

class TestRealPath:
    def test_parser_factura_extrae_monto_y_consumo(self):
        from mp_cfe_facturacion.client import _parse_cfe_factura_html
        html = """
        <html><body>
          <table>
            <tr><td>Total a pagar:</td><td>$ 1,245.50</td></tr>
            <tr><td>Consumo:</td><td>245 kWh</td></tr>
            <tr><td>Vencimiento:</td><td>30/06/2026</td></tr>
            <tr><td>Estatus:</td><td>PENDIENTE</td></tr>
            <tr><td>Periodo:</td><td>2026-05</td></tr>
          </table>
        </body></html>
        """
        r = _parse_cfe_factura_html(html, "123456789012")
        assert r["monto_total_mxn"] == 1245.50
        assert r["consumo_kwh"] == 245
        assert r["vencimiento"] == "30/06/2026"
        assert r["estatus"] == "PENDIENTE"
        assert "parse_partial" not in r

    def test_parser_consumo_extrae_meses(self):
        from mp_cfe_facturacion.client import _parse_cfe_consumo_html
        html = """
        <table>
          <tr><td>Mayo 2026</td><td>245 kWh</td><td>$ 698.25</td></tr>
          <tr><td>Abril 2026</td><td>231 kWh</td><td>$ 658.35</td></tr>
          <tr><td>Marzo 2026</td><td>218 kWh</td><td>$ 621.30</td></tr>
        </table>
        """
        r = _parse_cfe_consumo_html(html, "123456789012", meses=3)
        assert len(r["consumo_kwh_por_mes"]) == 3
        assert r["consumo_kwh_por_mes"][0]["kwh"] == 245
        assert r["promedio_kwh_mensual"] > 200

    def test_captcha_resolver_lee_env(self, tmp_path, monkeypatch):
        from mp_cfe_facturacion.client import _resolve_cfe_captcha
        monkeypatch.setenv("PLUGINS_MX_CFE_CAPTCHA", "AB12CD")
        fake_img = tmp_path / "cap.png"
        fake_img.write_bytes(b"")
        assert _resolve_cfe_captcha(fake_img, "123456789012") == "AB12CD"
