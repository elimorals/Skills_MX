"""Tests mp_no_antecedentes_penales_mx."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


class TestValidaciones:
    def test_curp_valida(self):
        from shared.no_antecedentes import validar_curp
        assert validar_curp("PERD850301HDFRZG02") == "PERD850301HDFRZG02"

    def test_curp_normaliza(self):
        from shared.no_antecedentes import validar_curp
        assert validar_curp("perd850301hdfrzg02") == "PERD850301HDFRZG02"

    def test_curp_invalida(self):
        from shared.no_antecedentes import validar_curp
        with pytest.raises(ValueError):
            validar_curp("INVALIDO")

    def test_folio_corto(self):
        from shared.no_antecedentes import validar_folio
        with pytest.raises(ValueError):
            validar_folio("XYZ")

    def test_entidad_cdmx_alias(self):
        from shared.no_antecedentes import validar_entidad
        assert validar_entidad("cdmx") == "cdmx"
        assert validar_entidad("Ciudad de México") == "cdmx"
        assert validar_entidad("DF") == "cdmx"

    def test_entidad_edomex_alias(self):
        from shared.no_antecedentes import validar_entidad
        assert validar_entidad("edomex") == "edomex"
        assert validar_entidad("Estado de México") == "edomex"
        assert validar_entidad("MEX") == "edomex"

    def test_entidad_no_soportada(self):
        from shared.no_antecedentes import validar_entidad
        with pytest.raises(ValueError):
            validar_entidad("jalisco")


@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.delenv("PLUGINS_MX_NOANT_LIVE", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestVerificarConstancia:
    def test_folio_par_vigente_sin_antecedentes(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_constancia("PERD850301HDFRZG02", "ABC1234", "cdmx")
        assert r["estado"] == "VIGENTE"
        assert r["tiene_antecedentes"] is False
        assert r["es_apta_para_contratacion"] is True

    def test_folio_impar_vigente_con_antecedentes(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_constancia("PERD850301HDFRZG02", "ABC1235", "cdmx")
        assert r["estado"] == "VIGENTE"
        assert r["tiene_antecedentes"] is True
        assert r["es_apta_para_contratacion"] is False

    def test_folio_terminado_x_expirada(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_constancia("PERD850301HDFRZG02", "FOLIOX", "edomex")
        assert r["estado"] == "EXPIRADA"

    def test_folio_terminado_z_anulada(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_constancia("PERD850301HDFRZG02", "FOLIOZ", "cdmx")
        assert r["estado"] == "ANULADA"

    def test_folio_fake_no_encontrada(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_constancia("PERD850301HDFRZG02", "FAKE1234", "cdmx")
        assert r["estado"] == "NO_ENCONTRADA"


class TestVerificarApto:
    def test_apto_sin_antecedentes(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_apto_contratacion("PERD850301HDFRZG02", "ABC1234", "cdmx")
        assert r["apto_para_contratacion"] is True
        assert "apto" in r["razon"].lower()

    def test_no_apto_con_antecedentes(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_apto_contratacion("PERD850301HDFRZG02", "ABC1235", "cdmx")
        assert r["apto_para_contratacion"] is False
        assert "antecedentes" in r["razon"].lower()

    def test_no_apto_constancia_fake(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_apto_contratacion("PERD850301HDFRZG02", "FAKE1234", "cdmx")
        assert r["apto_para_contratacion"] is False
        assert "no encontrada" in r["razon"].lower() or "falso" in r["razon"].lower()

    def test_no_apto_constancia_expirada(self):
        from mp_no_antecedentes_penales_mx.client import NoAntecedentesClient
        c = NoAntecedentesClient()
        r = c.verificar_apto_contratacion("PERD850301HDFRZG02", "FOLIOX", "cdmx")
        assert r["apto_para_contratacion"] is False
        assert "expirada" in r["razon"].lower() or "vigencia" in r["razon"].lower()
