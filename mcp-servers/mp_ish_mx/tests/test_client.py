"""Tests mp_ish_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestCalcular:
    def test_cdmx_35pct(self):
        from shared.ish_mx import calcular_ish
        r = calcular_ish("cdmx", 1000)
        assert r["tasa_pct"] == 3.5
        assert r["ish_mxn"] == 35.0
        assert r["monto_total_con_ish"] == 1035.0

    def test_qroo_5pct(self):
        from shared.ish_mx import calcular_ish
        r = calcular_ish("qroo", 2000)
        assert r["tasa_pct"] == 5.0
        assert r["ish_mxn"] == 100.0

    def test_edomex_cobra_4pct(self):
        """Corregido 2026-10-14: EdoMex SÍ cobra ISH (4%)."""
        from shared.ish_mx import calcular_ish
        r = calcular_ish("edomex", 1000)
        assert r["cobra_ish"] is True
        assert r["ish_mxn"] == 40.0
        assert r["simulated"] is False

    def test_plataformas_cdmx_5pct(self):
        from shared.ish_mx import calcular_ish
        assert calcular_ish("cdmx", 1000, plataforma_digital=True)["ish_mxn"] == 50.0
        assert calcular_ish("qroo", 1000, plataforma_digital=True)["tasa_pct"] == 6.0
        # sin tasa especial → tasa general
        assert calcular_ish("nl", 1000, plataforma_digital=True)["tasa_pct"] == 3.0

    def test_todas_con_fuente(self):
        from shared.ish_mx import CATALOGO_ISH
        assert all(e.fuentes for e in CATALOGO_ISH)

    def test_estado_invalido(self):
        from shared.ish_mx import calcular_ish
        with pytest.raises(ValueError):
            calcular_ish("xx", 100)

    def test_monto_negativo(self):
        from shared.ish_mx import calcular_ish
        with pytest.raises(ValueError):
            calcular_ish("cdmx", -100)


class TestCatalogo:
    def test_listar_32_estados(self):
        from shared.ish_mx import listar_ish
        assert len(listar_ish()) == 32

    def test_solo_aplicables_27(self):
        from shared.ish_mx import listar_ish
        aplicables = listar_ish(solo_aplicables=True)
        assert len(aplicables) == 32  # 2026: las 32 entidades lo cobran


class TestClientCompara:
    def test_compara_3_estados(self):
        from mp_ish_mx.client import IshMxClient
        c = IshMxClient()
        r = c.comparar_estados(["cdmx", "qroo", "edomex"], 1000)
        assert r["comparados"] == 3
        assert [x["estado"] for x in r["barato_a_caro"]] == ["cdmx", "edomex", "qroo"]

    def test_compara_lista_vacia(self):
        from mp_ish_mx.client import IshMxClient
        from shared.errors import ValidationError
        c = IshMxClient()
        with pytest.raises(ValidationError):
            c.comparar_estados([], 1000)


class TestClientInfo:
    def test_info_qroo(self):
        from mp_ish_mx.client import IshMxClient
        c = IshMxClient()
        r = c.info_estado("qroo")
        assert r["tasa_pct"] == 5.0
        assert r["cobra_ish"] is True
