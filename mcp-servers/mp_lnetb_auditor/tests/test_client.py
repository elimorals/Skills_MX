"""Tests mp_lnetb_auditor."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_lnetb_auditor.client import (
    EVALUACION_ESTADOS,
    INDICADORES_LNETB,
    LnetbAuditorClient,
    META_2030_PCT,
)
from shared.errors import ConfigError, ValidationError


@pytest.fixture(autouse=True)
def _mock_para_scores(monkeypatch, tmp_path):
    # Los scores por estado solo existen en mock; las clases de abajo los prueban así.
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


class TestIndicadores:
    def setup_method(self):
        self.c = LnetbAuditorClient()

    def test_10_indicadores_pesos_suman_100(self):
        r = self.c.listar_indicadores()
        assert r["total_indicadores"] == 10
        assert r["suma_pesos"] == 100


class TestEvaluarEstado:
    def setup_method(self):
        self.c = LnetbAuditorClient()

    def test_cdmx_es_lider_aproximado(self):
        r = self.c.evaluar_estado("cdmx")
        assert r["score_compuesto"] > 70
        assert r["nombre"] == "Ciudad de México"

    def test_score_oaxaca_bajo(self):
        r = self.c.evaluar_estado("oax")
        assert r["score_compuesto"] < 50
        assert r["alcanza_meta"] is False

    def test_brecha_calculada(self):
        r = self.c.evaluar_estado("cdmx")
        assert r["brecha_vs_meta_pct"] == round(META_2030_PCT - r["score_compuesto"], 2)

    def test_estado_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.evaluar_estado("xx")


class TestRanking:
    def setup_method(self):
        self.c = LnetbAuditorClient()

    def test_ranking_32_estados(self):
        r = self.c.ranking_nacional(top=32)
        assert r["total_estados"] == len(EVALUACION_ESTADOS)
        assert r["lider"]["score"] >= r["rezagado"]["score"]

    def test_top_5(self):
        r = self.c.ranking_nacional(top=5)
        assert len(r["ranking"]) == 5

    def test_promedio_nacional_bajo_80(self):
        r = self.c.ranking_nacional()
        # Realidad MX: promedio debería estar por debajo de la meta 2030
        assert r["promedio_nacional"] < META_2030_PCT
        assert r["brecha_promedio_vs_meta"] > 0

    def test_top_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.ranking_nacional(top=0)


class TestComparar:
    def setup_method(self):
        self.c = LnetbAuditorClient()

    def test_comparar_3_estados(self):
        r = self.c.comparar_estados(["cdmx", "nl", "oax"])
        assert len(r["comparativa"]) == 3
        assert r["lider_comparativa"]["score"] >= r["rezagado_comparativa"]["score"]

    def test_vacio_falla(self):
        with pytest.raises(ValidationError):
            self.c.comparar_estados([])

    def test_max_10_estados(self):
        with pytest.raises(ValidationError):
            self.c.comparar_estados(["cdmx"] * 11)


class TestReal:
    def setup_method(self):
        self.c = LnetbAuditorClient()

    def test_scores_bloqueados_fuera_de_mock(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
        with pytest.raises(ConfigError):
            self.c.evaluar_estado("cdmx")
        with pytest.raises(ConfigError):
            self.c.ranking_nacional()

    def test_plazos_transitorios(self, monkeypatch):
        monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
        r = self.c.plazos_legales("2026-01-13")
        assert r["entrada_en_vigor"] == "2025-07-17"
        p = {x["transitorio"]: x for x in r["plazos"]}
        assert p["Décimo Cuarto"]["vence"] == "2026-01-13"
        assert p["Décimo Cuarto"]["vencido"] is False
        assert p["Décimo Quinto"]["vence"] == "2026-02-12"
        assert p["Cuarto"]["vence"] is None  # días hábiles: no se inventa fecha
        assert self.c.plazos_legales("2026-10-14")["plazos"][6]["vencido"] is True

    def test_fecha_invalida(self):
        with pytest.raises(ValidationError):
            self.c.plazos_legales("14/10/2026")
