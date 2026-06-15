"""Tests mp_verificacion_vehicular_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestCalcularPeriodo:
    def test_terminacion_5_amarillo(self):
        from shared.verificacion_vehicular import calcular_proximo_periodo
        color, meses = calcular_proximo_periodo(5, 6)
        assert color == "amarillo"
        assert 3 in meses

    def test_terminacion_1_verde(self):
        from shared.verificacion_vehicular import calcular_proximo_periodo
        color, _ = calcular_proximo_periodo(1, 6)
        assert color == "verde"

    def test_terminacion_invalida(self):
        from shared.verificacion_vehicular import calcular_proximo_periodo
        with pytest.raises(ValueError):
            calcular_proximo_periodo(15, 6)


class TestConsultar:
    def test_consultar_estatus_cdmx(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        c = VerificacionVehicularClient()
        r = c.consultar_estatus("ABC1234", "cdmx")
        assert "holograma_actual" in r
        assert r["simulated"] is True

    def test_estado_inexistente(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        from shared.errors import NotFoundError
        c = VerificacionVehicularClient()
        with pytest.raises(NotFoundError):
            c.consultar_estatus("ABC1234", "xx")

    def test_placa_corta(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        from shared.errors import ValidationError
        c = VerificacionVehicularClient()
        with pytest.raises(ValidationError):
            c.consultar_estatus("A1", "cdmx")


class TestProximoPeriodo:
    def test_proximo_terminacion_5(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        c = VerificacionVehicularClient()
        r = c.proximo_periodo("ABC1235", "cdmx")  # terminacion 5
        assert r["color_engomado"] == "amarillo"
        assert r["terminacion"] == 5

    def test_listar_7_programas(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        c = VerificacionVehicularClient()
        r = c.listar_programas()
        assert r["total"] == 7


class TestSAFParser:
    """Calibrados en vivo con SAF CDMX 2026-06-15 — selectores reales del wizard."""

    def test_placa_no_localizada(self):
        """Caso: placa inválida → SAF muestra alert específico."""
        from mp_verificacion_vehicular_mx.client import _parse_saf_cdmx_html
        html = """<div class="alert alert-danger">El número de placa no se localizó en el padrón</div>"""
        r = _parse_saf_cdmx_html(html, "AAA0000")
        assert r["placa_localizada"] is False
        assert "padrón" in r["mensaje"]

    def test_parser_5_secciones_vehiculo_limpio(self):
        """Shape real del wizard SAF (5 spans nav_item_title)."""
        from mp_verificacion_vehicular_mx.client import _parse_saf_cdmx_html
        html = """
        <div class="kt-wizard-v1__nav">
          <span class="nav_item_title">Sin adeudos de tenencia</span>
          <span class="nav_item_title" id="infraccionesLbl">Sin infracciones</span>
          <span class="nav_item_title" id="sancionesLbl">Sin sanciones ambientales</span>
          <span class="nav_item_title">Fotocivicas 10 puntos</span>
          <span class="nav_item_title">Vigencia de licencia y tarjeta de circulación</span>
        </div>
        """
        r = _parse_saf_cdmx_html(html, "ABC1234")
        assert r["placa_localizada"] is True
        assert r["tenencia_adeudo"] is False
        assert r["infracciones_count"] == 0
        assert r["sanciones_ambientales_count"] == 0
        assert r["fotocivicas_puntos"] == 10
        assert r["vigente"] is True

    def test_parser_con_una_infraccion(self):
        """Caso real observado: 'Una infracción no pagada'."""
        from mp_verificacion_vehicular_mx.client import _parse_saf_cdmx_html
        html = """
        <span class="nav_item_title">Sin adeudos de tenencia</span>
        <span class="nav_item_title" id="infraccionesLbl">Una infracción no pagada</span>
        <span class="nav_item_title" id="sancionesLbl">Sin sanciones ambientales</span>
        <span class="nav_item_title">Fotocivicas 10 puntos</span>
        """
        r = _parse_saf_cdmx_html(html, "ABC1234")
        assert r["infracciones_count"] == 1
        assert r["vigente"] is False  # tiene infracción

    def test_parser_con_adeudo_tenencia(self):
        from mp_verificacion_vehicular_mx.client import _parse_saf_cdmx_html
        html = """
        <span class="nav_item_title">$ 3,245.50 adeudados de tenencia</span>
        <span class="nav_item_title" id="infraccionesLbl">Sin infracciones</span>
        <span class="nav_item_title" id="sancionesLbl">Sin sanciones ambientales</span>
        <span class="nav_item_title">Fotocivicas 8 puntos</span>
        """
        r = _parse_saf_cdmx_html(html, "ABC1234")
        assert r["tenencia_adeudo"] is True
        assert r["tenencia_monto_mxn"] == 3245.50
        assert r["fotocivicas_puntos"] == 8

    def test_parser_html_vacio_marca_partial(self):
        from mp_verificacion_vehicular_mx.client import _parse_saf_cdmx_html
        r = _parse_saf_cdmx_html("<html>sin datos</html>", "ABC1234")
        assert r.get("parse_partial") is True
        assert r["vigente"] is False


class TestLiveFlag:
    def test_live_flag_no_cdmx_se_queda_en_mock(self, monkeypatch):
        """LIVE flag activo pero estado != cdmx → mock (otros estados no implementados)."""
        monkeypatch.setenv("PLUGINS_MX_VERIFICACION_LIVE", "1")
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        c = VerificacionVehicularClient()
        r = c.consultar_estatus("ABC1234", "edomex")
        assert r["simulated"] is True

    def test_captcha_resolver_lee_env(self, tmp_path, monkeypatch):
        """_resolve_captcha lee de PLUGINS_MX_VERIFICACION_CAPTCHA."""
        from mp_verificacion_vehicular_mx.client import _resolve_captcha
        monkeypatch.setenv("PLUGINS_MX_VERIFICACION_CAPTCHA", "ABCDE5")
        fake_img = tmp_path / "cap.png"
        fake_img.write_bytes(b"")
        assert _resolve_captcha(fake_img, "ABC1234") == "ABCDE5"
