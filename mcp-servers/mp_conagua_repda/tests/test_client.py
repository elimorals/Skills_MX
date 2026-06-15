"""Tests mp_conagua_repda."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_consultar_titular_rfc():
    from mp_conagua_repda.client import CONAGUARepdaClient
    c = CONAGUARepdaClient()
    r = c.consultar_titular(identificador="XAXX010101000")
    assert r["total_permisos"] >= 1


def test_consultar_titular_corto():
    from mp_conagua_repda.client import CONAGUARepdaClient
    from shared.errors import ValidationError
    c = CONAGUARepdaClient()
    with pytest.raises(ValidationError):
        c.consultar_titular(identificador="XX")


def test_estado_reporte_semestral():
    from mp_conagua_repda.client import CONAGUARepdaClient
    c = CONAGUARepdaClient()
    r = c.estado_reporte_semestral(num_titulo="02SON100002/22HSGS02",
                                     periodo="1er_semestre")
    assert "presentado" in r


def test_estado_reporte_periodo_invalido():
    from mp_conagua_repda.client import CONAGUARepdaClient
    from shared.errors import ValidationError
    c = CONAGUARepdaClient()
    with pytest.raises(ValidationError):
        c.estado_reporte_semestral(num_titulo="02SON100000/20HSGS00",
                                     periodo="3er_trimestre")


def test_calcular_lfd_zona_alta_escasez():
    from mp_conagua_repda.client import CONAGUARepdaClient
    c = CONAGUARepdaClient()
    r = c.calcular_lfd_pago = c.calcular_pago_lfd(num_titulo="02SON100000/20HSGS00",
                                                    m3_extraidos=100_000, zona_disponibilidad=1)
    assert r["cuota_m3_mxn"] == 27.50
    assert r["cuota_total_mxn"] == 2_750_000.0


def test_calcular_lfd_zona_invalida():
    from mp_conagua_repda.client import CONAGUARepdaClient
    from shared.errors import ValidationError
    c = CONAGUARepdaClient()
    with pytest.raises(ValidationError):
        c.calcular_pago_lfd(num_titulo="02SON100000/20HSGS00",
                              m3_extraidos=100, zona_disponibilidad=10)


def test_vigencia_titulo():
    from mp_conagua_repda.client import CONAGUARepdaClient
    c = CONAGUARepdaClient()
    r = c.consultar_vigencia(num_titulo="02SON100000/20HSGS00")
    assert r["vigente"] is True


def test_requiere_medidor_arriba_umbral():
    from mp_conagua_repda.client import CONAGUARepdaClient
    c = CONAGUARepdaClient()
    r = c.requiere_medidor(volumen_anual_m3=200_000)
    assert r["requiere_medidor_obligatorio"] is True


def test_requiere_medidor_debajo_umbral():
    from mp_conagua_repda.client import CONAGUARepdaClient
    c = CONAGUARepdaClient()
    r = c.requiere_medidor(volumen_anual_m3=10_000)
    assert r["requiere_medidor_obligatorio"] is False


def test_listar_tipos_uso():
    from mp_conagua_repda.client import CONAGUARepdaClient
    c = CONAGUARepdaClient()
    r = c.listar_tipos_uso()
    assert "industrial" in r["tipos_uso"]
    assert len(r["tipos_uso"]) >= 10
