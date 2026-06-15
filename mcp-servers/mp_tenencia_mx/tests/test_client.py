"""Tests mp_tenencia_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestCatalogo:
    def test_catalogo_min_18(self):
        from shared.tenencia_mx import CATALOGO_TENENCIA
        assert len(CATALOGO_TENENCIA) >= 18

    def test_edomex_cobra_tenencia(self):
        from shared.tenencia_mx import buscar_estado
        e = buscar_estado("edomex")
        assert e is not None
        assert e.cobra_tenencia is True
        assert e.tasa_tenencia_pct > 0

    def test_nl_no_cobra_tenencia(self):
        from shared.tenencia_mx import buscar_estado
        e = buscar_estado("nl")
        assert e.cobra_tenencia is False
        assert e.cobra_refrendo is True

    def test_listar_solo_con_tenencia(self):
        from shared.tenencia_mx import listar_estados
        con_tenencia = listar_estados(solo_con_tenencia=True)
        assert len(con_tenencia) >= 2  # al menos EdoMex y Jalisco
        assert all(e.cobra_tenencia for e in con_tenencia)


class TestCalcularTenencia:
    def test_auto_exento_por_valor(self):
        from shared.tenencia_mx import calcular_tenencia
        # EdoMex exento < $400K
        r = calcular_tenencia("edomex", 300000, 2024, anio_actual=2026)
        assert r["exento_de_tenencia"] is True
        assert r["tenencia_mxn"] == 0
        assert r["refrendo_mxn"] > 0

    def test_auto_caro_paga_tenencia(self):
        from shared.tenencia_mx import calcular_tenencia
        # EdoMex auto $800K, 2 años antig → factor 0.70
        r = calcular_tenencia("edomex", 800000, 2024, anio_actual=2026)
        assert r["exento_de_tenencia"] is False
        assert r["tenencia_mxn"] > 0
        # Valor depreciado: 800K × 0.70 = 560K. Tenencia 3% = 16,800
        assert abs(r["tenencia_mxn"] - 16800) < 50
        assert r["factor_depreciacion"] == 0.70

    def test_nl_no_calcula_tenencia(self):
        from shared.tenencia_mx import calcular_tenencia
        r = calcular_tenencia("nl", 1000000, 2024, anio_actual=2026)
        assert r["tenencia_mxn"] == 0
        assert r["cobra_tenencia"] is False
        assert r["refrendo_mxn"] > 0

    def test_auto_viejo_depreciacion_minima(self):
        from shared.tenencia_mx import calcular_tenencia
        # Auto de 12 años → factor 0.10 (mínimo)
        r = calcular_tenencia("edomex", 500000, 2014, anio_actual=2026)
        assert r["antiguedad_anios"] == 12
        assert r["factor_depreciacion"] == 0.10

    def test_estado_no_existe(self):
        from shared.tenencia_mx import calcular_tenencia
        with pytest.raises(ValueError):
            calcular_tenencia("xx", 100000, 2024)

    def test_anio_modelo_invalido(self):
        from shared.tenencia_mx import calcular_tenencia
        with pytest.raises(ValueError):
            calcular_tenencia("edomex", 100000, 1950)


class TestClientComparar:
    def test_compara_3_estados(self):
        from mp_tenencia_mx.client import TenenciaMxClient
        c = TenenciaMxClient()
        r = c.comparar_estados(
            estados_claves=["edomex", "jal", "nl"],
            valor_factura=500000,
            anio_modelo=2023,
        )
        assert r["comparados"] == 3
        assert len(r["barato_a_caro"]) == 3
        # NL no cobra tenencia → suele ser el más barato para autos > umbral
        # (pero depende del valor_factura — para 500K, jal y edomex pueden estar exentos)
        # Verificamos solo orden monotónico
        montos = [x["subtotal_mxn"] for x in r["barato_a_caro"]]
        assert montos == sorted(montos)

    def test_compara_con_estado_inexistente(self):
        from mp_tenencia_mx.client import TenenciaMxClient
        c = TenenciaMxClient()
        r = c.comparar_estados(
            estados_claves=["edomex", "xx", "nl"],
            valor_factura=500000,
            anio_modelo=2023,
        )
        assert len(r["errores"]) == 1
        assert r["errores"][0]["estado"] == "xx"

    def test_compara_lista_vacia(self):
        from mp_tenencia_mx.client import TenenciaMxClient
        from shared.errors import ValidationError
        c = TenenciaMxClient()
        with pytest.raises(ValidationError):
            c.comparar_estados([], 100000, 2024)


class TestClientInfo:
    def test_info_estado_devuelve_config(self):
        from mp_tenencia_mx.client import TenenciaMxClient
        c = TenenciaMxClient()
        r = c.info_estado("edomex")
        assert r["clave"] == "edomex"
        assert "tasa_tenencia_pct" in r
        assert "portal_url" in r

    def test_info_no_existe(self):
        from mp_tenencia_mx.client import TenenciaMxClient
        from shared.errors import NotFoundError
        c = TenenciaMxClient()
        with pytest.raises(NotFoundError):
            c.info_estado("xx")

    def test_listar_20_estados(self):
        from mp_tenencia_mx.client import TenenciaMxClient
        c = TenenciaMxClient()
        r = c.listar_estados()
        assert r["total"] >= 18
