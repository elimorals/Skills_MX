"""Tests del cliente mp_isn_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
if str(_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(_MCP_ROOT))

from mp_isn_mx.client import IsnMxClient  # noqa: E402
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.catalogo_isn_estatal import (  # noqa: E402
    CATALOGO_ISN,
    calcular_isn,
    estadisticas_catalogo,
    get_estado_config,
    listar_estados,
)
from shared.errors import NotFoundError, ValidationError  # noqa: E402


@pytest.fixture
def tmp_client(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    cache = FileCache("isn_mx_test", root=tmp_path / "cache")
    bit = Bitacora("isn_mx_test", root=tmp_path / "bita")
    return IsnMxClient(cache=cache, bitacora=bit)


class TestCatalogo:
    def test_32_estados(self):
        # MX tiene 32 entidades, esperamos al menos 30 en el catálogo
        assert len(CATALOGO_ISN) >= 30

    def test_cdmx_presente(self):
        cfg = get_estado_config("CDMX")
        assert cfg is not None
        assert cfg.estado_nombre == "Ciudad de México"
        assert cfg.tasa_pct == 3.0
        assert cfg.validado is True

    def test_busqueda_por_nombre(self):
        cfg = get_estado_config("Jalisco")
        assert cfg is not None
        assert cfg.estado_clave == "JAL"

    def test_estado_inexistente(self):
        assert get_estado_config("XXXXXX") is None

    def test_listar_solo_validados(self):
        todos = listar_estados()
        validados = listar_estados(solo_validados=True)
        assert len(validados) <= len(todos)
        assert all(e["validado"] for e in validados)

    def test_stats(self):
        s = estadisticas_catalogo()
        assert s["total_estados"] >= 30
        assert s["validados"] >= 5
        assert s["tasa_min"] < s["tasa_max"]


class TestCalcular:
    def test_cdmx_3pct(self, tmp_client):
        r = tmp_client.calcular(nomina_gravable=100_000, estado="CDMX")
        assert r["isn_a_pagar"] == 3000.0
        assert r["tasa_pct"] == 3.0
        assert r["estado_clave"] == "CDMX"

    def test_bc_1_8pct(self, tmp_client):
        r = tmp_client.calcular(nomina_gravable=100_000, estado="BC")
        assert r["isn_a_pagar"] == 1800.0
        assert r["tasa_pct"] == 1.8

    def test_gto_2pct(self, tmp_client):
        r = tmp_client.calcular(nomina_gravable=50_000, estado="GTO")
        assert r["isn_a_pagar"] == 1000.0

    def test_nomina_cero(self, tmp_client):
        r = tmp_client.calcular(nomina_gravable=0, estado="CDMX")
        assert r["isn_a_pagar"] == 0.0

    def test_nomina_negativa(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.calcular(nomina_gravable=-1, estado="CDMX")

    def test_estado_inexistente(self, tmp_client):
        with pytest.raises(NotFoundError):
            tmp_client.calcular(nomina_gravable=1000, estado="XXXXXX")


class TestInfoEstado:
    def test_cdmx_info(self, tmp_client):
        r = tmp_client.info_estado("CDMX")
        assert r["clave"] == "CDMX"
        assert r["tasa_pct"] == 3.0
        assert r["requiere_efirma"] is True
        assert "selectores_documentados" in r

    def test_jal_sin_efirma(self, tmp_client):
        r = tmp_client.info_estado("JAL")
        assert r["requiere_efirma"] is False

    def test_no_existe(self, tmp_client):
        with pytest.raises(NotFoundError):
            tmp_client.info_estado("ZZ")


class TestLineaCaptura:
    def test_genera_mock(self, tmp_client):
        r = tmp_client.generar_linea_captura(
            estado="CDMX",
            periodo="2026-05",
            rfc="ABC120101AB1",
            nomina_gravable=100_000,
        )
        assert "linea_captura" in r
        assert r["monto_a_pagar"] == 3000.0
        assert r["estado"] == "CDMX"
        assert r.get("simulated") is True

    def test_periodo_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.generar_linea_captura(
                estado="CDMX", periodo="2026-13",  # mes 13
                rfc="ABC120101AB1", nomina_gravable=100,
            )

    def test_rfc_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.generar_linea_captura(
                estado="CDMX", periodo="2026-05",
                rfc="INVALIDO", nomina_gravable=100,
            )

    def test_cache_reutilizado(self, tmp_client):
        r1 = tmp_client.generar_linea_captura(
            estado="CDMX", periodo="2026-05",
            rfc="ABC120101AB1", nomina_gravable=100_000,
        )
        r2 = tmp_client.generar_linea_captura(
            estado="CDMX", periodo="2026-05",
            rfc="ABC120101AB1", nomina_gravable=200_000,  # nomina diff pero key igual
        )
        # caché vence por (estado, periodo, rfc) — comparten línea
        assert r1["linea_captura"] == r2["linea_captura"]


class TestDescargarDeclaracion:
    def test_descarga_mock(self, tmp_client):
        r = tmp_client.descargar_declaracion(
            estado="JAL", periodo="2026-04", rfc="XYZ010101XX1",
        )
        assert "declaracion_pdf_path" in r
        assert r["estado"] == "JAL"

    def test_periodo_invalido(self, tmp_client):
        with pytest.raises(ValidationError):
            tmp_client.descargar_declaracion(
                estado="JAL", periodo="not-period", rfc="ABC120101AB1",
            )

    def test_estado_inexistente(self, tmp_client):
        with pytest.raises(NotFoundError):
            tmp_client.descargar_declaracion(
                estado="ZZ", periodo="2026-04", rfc="ABC120101AB1",
            )


class TestListar:
    def test_total(self, tmp_client):
        r = tmp_client.listar()
        assert r["total"] >= 30
        assert "stats" in r

    def test_solo_validados(self, tmp_client):
        r = tmp_client.listar(solo_validados=True)
        assert r["total"] < 32  # no todos están validados
        assert all(e["validado"] for e in r["estados"])
