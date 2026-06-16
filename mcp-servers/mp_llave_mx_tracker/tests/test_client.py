"""Tests mp_llave_mx_tracker."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_llave_mx_tracker.client import (
    DEPENDENCIAS_MONITOREADAS,
    LlaveMxTrackerClient,
    STATUS_VALIDOS,
)
from shared.errors import ValidationError


class TestListar:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_listar_todas(self):
        r = self.c.listar_dependencias()
        assert r["total"] == len(DEPENDENCIAS_MONITOREADAS)
        assert "fuente_oficial_llave" in r

    def test_filtrar_federal(self):
        r = self.c.listar_dependencias(nivel="federal")
        for d in r["dependencias"]:
            assert d["nivel"] == "federal"

    def test_filtrar_estatal(self):
        r = self.c.listar_dependencias(nivel="estatal")
        for d in r["dependencias"]:
            assert d["nivel"] == "estatal"


class TestEstatusDependencia:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_atdt_integrado(self):
        r = self.c.estatus_dependencia("atdt")
        assert r["status_2026_06"] == "integrado"
        assert r["simulated"] is True

    def test_sat_no_integrado(self):
        r = self.c.estatus_dependencia("sat")
        assert r["status_2026_06"] == "no_integrado"

    def test_clave_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.estatus_dependencia("inexistente")


class TestEstadisticas:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_estadisticas_suman_total(self):
        r = self.c.estadisticas_nacionales()
        assert r["total_dependencias_monitoreadas"] == len(DEPENDENCIAS_MONITOREADAS)
        assert sum(r["por_status"].values()) == r["total_dependencias_monitoreadas"]

    def test_brecha_vs_meta_positiva(self):
        r = self.c.estadisticas_nacionales()
        # La brecha real es muy alta porque solo ATDT+gobmx están integrados
        assert r["brecha_vs_meta_pct"] > 0
        assert r["meta_lnetb_2030_pct"] == 80.0

    def test_status_validos_completos(self):
        r = self.c.estadisticas_nacionales()
        for s in STATUS_VALIDOS:
            assert s in r["por_status"]


class TestVerificarEnVivo:
    def setup_method(self):
        self.c = LlaveMxTrackerClient()

    def test_sin_playwright_publica_devuelve_mock(self, monkeypatch):
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        r = self.c.verificar_en_vivo("sat")
        assert r["simulated"] is True
        assert r["verificacion_metodo"] == "mock"

    def test_clave_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.verificar_en_vivo("inexistente")
