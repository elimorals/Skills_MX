"""Tests cliente mp_donatarias_sat."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
if str(_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_ROOT))

from mp_donatarias_sat.client import (  # noqa: E402
    ESTADOS_MX,
    RUBROS_DONATARIA,
    DonatariasSatClient,
    _normalizar,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture
def tmp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    cache = FileCache("donatarias_sat_test", root=tmp_path / "cache")
    bit = Bitacora("donatarias_sat_test", root=tmp_path / "bita")
    return DonatariasSatClient(cache=cache, bitacora=bit)


class TestNormalizar:
    def test_quita_acentos(self):
        assert _normalizar("Fundación Educación") == "fundacion educacion"

    def test_lowercase(self):
        assert _normalizar("FUNDACIÓN ABC") == "fundacion abc"

    def test_vacio(self):
        assert _normalizar("") == ""
        assert _normalizar(None) == ""


class TestConsultarDonataria:
    def test_rfc_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.consultar_donataria("INVALIDO")
        with pytest.raises(ValidationError):
            tmp_client.consultar_donataria("123")

    def test_autorizada_mock(self, tmp_client):
        # RFC que NO empieza con X o Z → autorizada en mock
        r = tmp_client.consultar_donataria("FUN010101AB1")
        assert r["rfc"] == "FUN010101AB1"
        assert r["autorizada"] is True
        assert r["puede_emitir_recibo_deducible"] is True
        assert r["rubro"] in RUBROS_DONATARIA
        assert r.get("simulated") is True

    def test_no_autorizada_mock(self, tmp_client):
        # RFC que EMPIEZA con X → no autorizada en mock
        r = tmp_client.consultar_donataria("XXX010101AB1")
        assert r["autorizada"] is False
        assert r["puede_emitir_recibo_deducible"] is False
        assert len(r["advertencias"]) >= 1

    def test_cache_reutilizado(self, tmp_client):
        r1 = tmp_client.consultar_donataria("FUN010101AB1")
        r2 = tmp_client.consultar_donataria("fun010101ab1")  # case
        assert r1["rfc"] == r2["rfc"]


class TestBuscar:
    def test_razon_social_corta(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.buscar_donatarias("ab")

    def test_entidad_invalida(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.buscar_donatarias("FUNDACION", entidad="XX")

    def test_limite_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.buscar_donatarias("FUNDACION", limite=0)

    def test_busqueda_ok(self, tmp_client):
        r = tmp_client.buscar_donatarias("EDUCACION")
        assert r["total_encontrados"] >= 1
        assert len(r["donatarias"]) >= 1

    def test_busqueda_con_entidad(self, tmp_client):
        r = tmp_client.buscar_donatarias("AYUDA", entidad="JAL")
        assert r["entidad_filtro"] == "JAL"


class TestListarPorEntidad:
    def test_estado_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.listar_por_entidad("XXX")

    def test_cdmx_grande(self, tmp_client):
        r = tmp_client.listar_por_entidad("CDMX")
        assert r["total"] > 100
        assert len(r["donatarias"]) >= 1


class TestEstadisticas:
    def test_stats_ok(self, tmp_client):
        r = tmp_client.estadisticas_padron()
        assert r["total_donatarias"] > 1000
        assert "por_entidad_top10" in r
        assert "por_rubro" in r
        assert r["por_entidad_top10"]["CDMX"] > r["por_entidad_top10"]["BC"]


class TestRubros:
    def test_listar_rubros(self, tmp_client):
        r = tmp_client.listar_rubros()
        assert r["total"] == 10
        assert "asistencia_social" in r["rubros"]
        assert "educacion" in r["rubros"]


class TestCatalogoEstados:
    def test_estados_mx_completos(self):
        assert len(ESTADOS_MX) >= 30
        assert "CDMX" in ESTADOS_MX
        assert "EDOMEX" in ESTADOS_MX
        assert "JAL" in ESTADOS_MX
