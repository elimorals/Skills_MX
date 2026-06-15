"""Tests mp_resico_sat."""
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


def test_calcular_isr_tramo_1():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.calcular_isr_mes(ingreso_mes_mxn=20_000)
    assert r["tasa_aplicada"] == 0.01
    assert r["isr_mxn"] == 200.0


def test_calcular_isr_tramo_5():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.calcular_isr_mes(ingreso_mes_mxn=250_000)
    assert r["tasa_aplicada"] == 0.025
    assert r["isr_mxn"] == 6250.0


def test_calcular_isr_supera_tope():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.calcular_isr_mes(ingreso_mes_mxn=300_000)
    assert r["supera_tope_mensual"] is True


def test_estatus_al_corriente():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.evaluar_estatus(rfc="XAXX010101000", periodos_omitidos=0,
                           declaracion_anual_presentada=True,
                           ingresos_anuales_mxn=500_000)
    assert r["estatus"] == "al_corriente"
    assert r["score_riesgo"] == 0


def test_estatus_expulsion_automatica_3_omisiones():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.evaluar_estatus(rfc="XAXX010101000", periodos_omitidos=3,
                           declaracion_anual_presentada=True,
                           ingresos_anuales_mxn=500_000)
    assert r["estatus"] == "expulsion_automatica"
    assert len(r["causas_expulsion"]) >= 1


def test_estatus_expulsion_por_rebasar_tope():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.evaluar_estatus(rfc="XAXX010101000", periodos_omitidos=0,
                           declaracion_anual_presentada=True,
                           ingresos_anuales_mxn=4_000_000)
    assert r["estatus"] == "expulsion_automatica"


def test_estatus_alerta_temprana():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.evaluar_estatus(rfc="XAXX010101000", periodos_omitidos=1,
                           declaracion_anual_presentada=True,
                           ingresos_anuales_mxn=500_000)
    assert r["estatus"] == "alerta_temprana"


def test_calendario_12_meses():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.calendario_declaraciones(anio=2026, mes_actual=6)
    assert len(r["proximas_declaraciones"]) == 12
    assert r["proximas_declaraciones"][0]["periodo"] == "2026-06"
    assert r["proximas_declaraciones"][0]["vencimiento"] == "2026-07-17"


def test_retencion_uber():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.retencion_plataforma(plataforma="uber", ingreso_bruto_mxn=10_000)
    assert r["tasa_retencion"] == 0.025
    assert r["retencion_isr_mxn"] == 250.0


def test_retencion_plataforma_invalida():
    from mp_resico_sat.client import RESICOClient
    from shared.errors import ValidationError
    c = RESICOClient()
    with pytest.raises(ValidationError):
        c.retencion_plataforma(plataforma="inexistente", ingreso_bruto_mxn=1000)


def test_solicitar_devolucion_genera_folio():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.solicitar_devolucion_mensual(rfc="XAXX010101000", periodo="2026-05",
                                         monto_solicitado_mxn=2500, plataforma="uber")
    assert r["folio_solicitud"].startswith("DEV-")
    assert r["monto_solicitado_mxn"] == 2500


def test_solicitar_devolucion_periodo_invalido():
    from mp_resico_sat.client import RESICOClient
    from shared.errors import ValidationError
    c = RESICOClient()
    with pytest.raises(ValidationError):
        c.solicitar_devolucion_mensual(rfc="XAXX010101000", periodo="2026/05",
                                         monto_solicitado_mxn=2500)


def test_listar_tasas_5_tramos():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.listar_tasas()
    assert len(r["tramos_mensuales"]) == 5
    assert r["tope_anual_mxn"] == 3_500_000.0


def test_listar_plataformas_12_categorias():
    from mp_resico_sat.client import RESICOClient
    c = RESICOClient()
    r = c.listar_plataformas()
    assert r["total"] == 12
    assert r["tasa_unica"] == 0.025
