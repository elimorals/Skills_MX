"""Tests mp_dof_api."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
if str(_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_ROOT))

from mp_dof_api.client import (  # noqa: E402
    DEPENDENCIAS,
    URL_BASE,
    URL_BUSQUEDA,
    URL_NOTA,
    URL_SUMARIO,
    DofApiClient,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture
def tmp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    cache = FileCache("dof_api_test", root=tmp_path / "cache")
    bit = Bitacora("dof_api_test", root=tmp_path / "bita")
    return DofApiClient(cache=cache, bitacora=bit)


class TestUrls:
    def test_base_correcta(self):
        assert URL_BASE == "https://www.dof.gob.mx"

    def test_sumario_template(self):
        assert "year={year}" in URL_SUMARIO
        assert "month={month:02d}" in URL_SUMARIO
        assert "index_111" in URL_SUMARIO

    def test_nota_template(self):
        assert "nota_detalle.php" in URL_NOTA
        assert "codigo={codigo}" in URL_NOTA


class TestParsearFecha:
    def test_formato_dof(self):
        d = DofApiClient._parsear_fecha("12/06/2026")
        assert d.year == 2026 and d.month == 6 and d.day == 12

    def test_formato_iso(self):
        d = DofApiClient._parsear_fecha("2026-06-12")
        assert d.year == 2026 and d.month == 6 and d.day == 12

    def test_invalida(self):
        with pytest.raises(ValidationError):
            DofApiClient._parsear_fecha("no-fecha")
        with pytest.raises(ValidationError):
            DofApiClient._parsear_fecha("")

    def test_dia_imposible(self):
        with pytest.raises(ValidationError):
            DofApiClient._parsear_fecha("32/06/2026")


class TestSumarioDia:
    def test_devuelve_notas(self, tmp_client):
        r = tmp_client.sumario_dia("12/06/2026")
        assert r["fecha"] == "12/06/2026"
        assert r["total_notas"] >= 1
        assert "url_consultado" in r
        assert r.get("simulated") is True

    def test_estructura_nota(self, tmp_client):
        r = tmp_client.sumario_dia("12/06/2026")
        nota = r["notas"][0]
        assert "codigo" in nota and "titulo" in nota
        assert "dependencia" in nota and "url_detalle" in nota

    def test_cache_reutilizado(self, tmp_client):
        r1 = tmp_client.sumario_dia("12/06/2026")
        r2 = tmp_client.sumario_dia("2026-06-12")  # iso equivalente
        # Misma fecha, mismo cache
        assert r1["fecha"] == r2["fecha"]


class TestBuscarTexto:
    def test_texto_corto(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.buscar_texto("ab")

    def test_periodo_invertido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.buscar_texto(
                "fintech", desde="01/01/2026", hasta="01/01/2020",
            )

    def test_limite_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.buscar_texto("fintech", limite=0)
        with pytest.raises(ValidationError):
            tmp_client.buscar_texto("fintech", limite=200)

    def test_busqueda_ok(self, tmp_client):
        r = tmp_client.buscar_texto("fintech")
        assert r["total_resultados"] >= 1
        assert "periodo" in r
        assert len(r["resultados"]) >= 1


class TestDetalleNota:
    def test_codigo_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.detalle_nota(codigo="ABC", fecha="12/06/2026")
        with pytest.raises(ValidationError):
            tmp_client.detalle_nota(codigo="123", fecha="12/06/2026")  # muy corto

    def test_fecha_invalida(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.detalle_nota(codigo="5790442", fecha="invalida")

    def test_detalle_ok(self, tmp_client):
        r = tmp_client.detalle_nota(codigo="5790442", fecha="12/06/2026")
        assert r["codigo"] == "5790442"
        assert "titulo" in r
        assert "texto_completo" in r
        assert "url_detalle" in r


class TestMonitorearKeywords:
    def test_keywords_vacio(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.monitorear_por_keyword(keywords=[])

    def test_dias_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.monitorear_por_keyword(keywords=["fintech"], dias_atras=0)

    def test_multiple_keywords(self, tmp_client):
        r = tmp_client.monitorear_por_keyword(
            keywords=["fintech", "RMF", "NOM"], dias_atras=30,
        )
        assert "hallazgos_por_keyword" in r
        assert len(r["keywords"]) == 3
        assert r["total_hallazgos"] >= 0


class TestDependencias:
    def test_listar(self, tmp_client):
        r = tmp_client.listar_dependencias_comunes()
        assert r["total"] >= 10
        assert "SAT" in r["dependencias"]
        assert "BANXICO" in r["dependencias"]


class TestCatalogoDependencias:
    def test_completo(self):
        assert len(DEPENDENCIAS) >= 10
        assert "SHCP" in DEPENDENCIAS
        assert "CNBV" in DEPENDENCIAS
