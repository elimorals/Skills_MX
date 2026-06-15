"""Tests mp_agua_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.delenv("PLUGINS_MX_AGUA_LIVE", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestCatalogo:
    def test_catalogo_no_vacio(self):
        from shared.agua_mx import CATALOGO_AGUA
        assert len(CATALOGO_AGUA) >= 10

    def test_sacmex_existe(self):
        from shared.agua_mx import buscar_organismo
        org = buscar_organismo("sacmex")
        assert org is not None
        assert org.estado == "CDMX"
        assert org.poblacion_aprox > 9_000_000

    def test_buscar_no_existe(self):
        from shared.agua_mx import buscar_organismo
        assert buscar_organismo("inexistente") is None

    def test_listar_solo_consultables(self):
        from shared.agua_mx import listar_organismos
        todos = listar_organismos(solo_consultables=False)
        consultables = listar_organismos(solo_consultables=True)
        assert len(consultables) <= len(todos)
        assert all(o.consultable for o in consultables)

    def test_buscar_por_estado(self):
        from shared.agua_mx import buscar_por_estado
        cdmx = buscar_por_estado("CDMX")
        assert any(o.clave == "sacmex" for o in cdmx)
        nl = buscar_por_estado("NL")
        assert any(o.clave == "sadm" for o in nl)

    def test_estadisticas_consistencia(self):
        from shared.agua_mx import estadisticas
        stats = estadisticas()
        assert stats["total_organismos"] >= 10
        assert 0 <= stats["consultables"] <= stats["total_organismos"]
        assert stats["poblacion_consultable_aprox"] <= stats["poblacion_total_cubierta"]


class TestConsultarAdeudo:
    def test_organismo_inexistente(self):
        from mp_agua_mx.client import AguaMxClient
        from shared.errors import NotFoundError
        c = AguaMxClient()
        with pytest.raises(NotFoundError):
            c.consultar_adeudo("inexistente", "12345678")

    def test_cuenta_formato_invalido(self):
        from mp_agua_mx.client import AguaMxClient
        from shared.errors import ValidationError
        c = AguaMxClient()
        with pytest.raises(ValidationError):
            c.consultar_adeudo("sacmex", "X")

    def test_consultar_sacmex_par_al_dia(self):
        from mp_agua_mx.client import AguaMxClient
        c = AguaMxClient()
        r = c.consultar_adeudo("sacmex", "12345678902")
        assert r["consultado"] is True
        assert r["estatus"] == "AL DIA"
        assert r["adeudo_mxn"] == 0.0
        assert r["simulated"] is True

    def test_consultar_siapa_impar_adeudo(self):
        from mp_agua_mx.client import AguaMxClient
        c = AguaMxClient()
        r = c.consultar_adeudo("siapa", "1234567")  # ends in 7 (impar)
        assert r["estatus"] in ("PENDIENTE", "VENCIDO")
        assert r["adeudo_mxn"] > 0
        assert any("recargos" in adv.lower() or "pendiente" in adv.lower() or "vencido" in adv.lower() for adv in r["advertencias"])

    def test_organismo_no_consultable(self):
        from mp_agua_mx.client import AguaMxClient
        c = AguaMxClient()
        r = c.consultar_adeudo("japay", "12345")
        assert r["estatus"] == "NO_IMPLEMENTADO"
        assert r["consultado"] is False
        assert any("no está implementado" in adv.lower() or "scraper" in adv.lower() for adv in r["advertencias"])


class TestServerTools:
    def test_listar_devuelve_estructura(self):
        from mp_agua_mx.client import AguaMxClient
        c = AguaMxClient()
        r = c.listar_organismos()
        assert r["total"] >= 10
        assert len(r["organismos"]) == r["total"]
        sacmex = next((o for o in r["organismos"] if o["clave"] == "sacmex"), None)
        assert sacmex is not None
        assert sacmex["estado"] == "CDMX"

    def test_buscar_por_estado_jal(self):
        from mp_agua_mx.client import AguaMxClient
        c = AguaMxClient()
        r = c.buscar_por_estado("JAL")
        assert r["encontrados"] >= 1
        assert any(o["clave"] == "siapa" for o in r["organismos"])

    def test_estadisticas(self):
        from mp_agua_mx.client import AguaMxClient
        c = AguaMxClient()
        r = c.estadisticas_catalogo()
        assert "total_organismos" in r
        assert "porcentaje_pob_nacional_consultable" in r
        assert 0 < r["porcentaje_pob_nacional_consultable"] < 100
