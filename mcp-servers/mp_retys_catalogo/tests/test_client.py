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
from shared.errors import ValidationError


class TestSectores:
    def setup_method(self):
        self.c = RetysCatalogoClient()

    def test_24_sectores_minimo(self):
        r = self.c.listar_sectores()
        assert r["total_sectores"] >= 24
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

    def test_sin_flag_devuelve_mock(self, monkeypatch):
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        r = self.c.buscar_en_vivo("constancia")
        assert r["simulated"] is True
