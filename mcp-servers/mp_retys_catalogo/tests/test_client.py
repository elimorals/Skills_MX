"""Tests mp_retys_catalogo."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_retys_catalogo.client import (
    RetysCatalogoClient,
    SECTORES_CONAMER,
    TRAMITES_DEMANDA_ALTA,
)
from mp_retys_catalogo.client import parse_resultados
from shared.errors import ConfigError, ValidationError

FX = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(autouse=True)
def _mock_por_defecto(monkeypatch, tmp_path):
    # El catálogo curado solo existe en mock; las clases de abajo lo prueban así.
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


class TestSectores:
    def setup_method(self):
        self.c = RetysCatalogoClient()

    def test_27_temas_portada(self):
        r = self.c.listar_sectores()
        assert r["total_sectores"] == 27
        assert "agua" in {s["clave"] for s in r["sectores"]}
        assert "transformacion_digital" in {s["clave"] for s in r["sectores"]}


class TestBusqueda:
    def setup_method(self):
        self.c = RetysCatalogoClient()

    def test_buscar_csf(self):
        r = self.c.buscar_tramite("constancia")
        assert r["total_resultados"] >= 1
        assert any("Constancia" in t["nombre"] for t in r["resultados"])

    def test_buscar_por_dependencia(self):
        r = self.c.buscar_tramite("SAT")
        assert r["total_resultados"] >= 2

    def test_query_corto_falla(self):
        with pytest.raises(ValidationError):
            self.c.buscar_tramite("a")

    def test_filtrar_sector_valido(self):
        r = self.c.buscar_tramite("SAT", sector="hacienda_finanzas")
        for t in r["resultados"]:
            assert t["sector"] == "hacienda_finanzas"

    def test_sector_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.buscar_tramite("SAT", sector="inexistente")


class TestDetalle:
    def setup_method(self):
        self.c = RetysCatalogoClient()

    def test_detalle_csf(self):
        r = self.c.detalle_tramite("SAT-04-022")
        assert r["nombre"] == "Constancia de Situación Fiscal"
        assert r["dependencia"] == "SAT"

    def test_homoclave_normaliza_a_upper(self):
        r = self.c.detalle_tramite("sat-04-022")
        assert r["homoclave"] == "SAT-04-022"

    def test_homoclave_inexistente_falla(self):
        with pytest.raises(ValidationError):
            self.c.detalle_tramite("XYZ-99")


class TestDcat:
    def setup_method(self):
        self.c = RetysCatalogoClient()

    def test_dcat_valido(self):
        r = self.c.exportar_dcat()
        assert r["@type"] == "Catalog"
        assert r["@context"] == "https://www.w3.org/ns/dcat"
        assert len(r["dataset"]) == len(TRAMITES_DEMANDA_ALTA)
        assert r["license"].startswith("https://creativecommons.org/")


class TestEnVivo:
    def setup_method(self):
        self.c = RetysCatalogoClient()

    def test_mock_marcado(self):
        r = self.c.buscar_en_vivo("constancia")
        assert r["simulated"] is True


class TestReal:
    """Fuera de mock: parser con fragmentos reales y catálogo curado bloqueado."""

    def setup_method(self):
        self.c = RetysCatalogoClient()

    def test_parse_inspecciones_reales(self):
        r = parse_resultados((FX / "inspecciones_cofepris.html").read_text())
        assert r["en_pagina"] == 7
        primero = r["resultados"][0]
        assert primero["homoclave"] == "I-COFEPRIS-002"
        assert primero["titulo"] == "AUTOEVALUACIÓN DE FARMACIAS"
        assert primero["dependencia"] == "Comisión Federal para la Protección contra Riesgos Sanitarios"
        assert primero["tipo"] == "Inspección"
        assert primero["url_ficha"].endswith("FichaInspeccion?homoClave=I-COFEPRIS-002")

    def test_parse_regulaciones_reales(self):
        r = parse_resultados((FX / "regulaciones_salud.html").read_text())
        assert r["en_pagina"] == 10
        assert r["resultados"][0]["homoclave"] == "R-SEGOB-0173"
        assert r["resultados"][0]["tipo"] == "Regulación"

    def test_error_servidor_se_reporta(self):
        r = parse_resultados((FX / "regulaciones_error_42601.html").read_text())
        assert r["resultados"] == []
        assert r["error"].startswith("42601")

    def test_dcat_bloqueado_fuera_de_mock(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
        with pytest.raises(ConfigError):
            self.c.exportar_dcat()

    def test_detalle_fuera_de_mock_da_url_oficial(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
        r = self.c.detalle_tramite("i-cofepris-002")
        assert r["url_ficha"] == "https://www.catalogonacional.gob.mx/FichaInspeccion?homoClave=I-COFEPRIS-002"
        with pytest.raises(ValidationError):
            self.c.detalle_tramite("SAT-04-022")


@pytest.mark.live
def test_live_buscar_en_vivo(monkeypatch):
    """Akamai bloquea headless: correr con MP_PLAYWRIGHT_HEADLESS=0."""
    pytest.importorskip("playwright")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    r = RetysCatalogoClient().buscar_en_vivo("cofepris")
    assert r["simulated"] is False
    assert r["inspecciones"]["en_pagina"] > 0
