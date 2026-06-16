"""Tests Sprint F IMSS: SBC, EMA/EBA, calendario, costo patronal, prima RT."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_imss_patronal.client import ImssPatronalClient
from shared.errors import ValidationError


class TestSbcCalcular:
    def setup_method(self):
        self.c = ImssPatronalClient()

    def test_sbc_minimo_factor_15_aguinaldo(self):
        # Salario base $500/día, sin bono, 15d aguinaldo, 25% prima vac
        r = self.c.sbc_calcular(500.0)
        # Factor mínimo: 1 + (15/365) + (0.25 * 12 / 365) ≈ 1.0493
        assert 1.04 <= r["factor_integracion"] <= 1.06
        assert r["sbc_final_mxn"] == round(500 * r["factor_integracion"], 2)
        assert r["aplicado_tope_25_umas"] is False
        assert r["uma_2026_diaria"] == 113.07

    def test_tope_25_umas_aplica(self):
        # Salario muy alto debe topar a 25 UMAs
        r = self.c.sbc_calcular(5000.0)
        assert r["aplicado_tope_25_umas"] is True
        assert r["sbc_final_mxn"] == 113.07 * 25

    def test_smg_advertencia(self):
        r = self.c.sbc_calcular(200.0)
        assert "Por debajo de SMG" in r["advertencia_smg"]

    def test_salario_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.sbc_calcular(-100.0)

    def test_aguinaldo_menor_15_falla(self):
        with pytest.raises(ValidationError):
            self.c.sbc_calcular(500.0, dias_aguinaldo=10)


class TestEmaEba:
    def setup_method(self):
        self.c = ImssPatronalClient()

    def test_devuelve_ema_eba_diferencia(self):
        r = self.c.ema_vs_eba_diferencias("Y123456789", "2026-05")
        assert r["ema_total_mxn"] > 0
        assert r["eba_total_mxn"] > 0
        assert "inconsistencias" in r
        assert isinstance(r["requiere_aclaracion"], bool)

    def test_determinismo(self):
        r1 = self.c.ema_vs_eba_diferencias("Y999999999", "2026-01")
        r2 = self.c.ema_vs_eba_diferencias("Y999999999", "2026-01")
        assert r1["ema_total_mxn"] == r2["ema_total_mxn"]


class TestCalendarioObligaciones:
    def setup_method(self):
        self.c = ImssPatronalClient()

    def test_devuelve_12_mensuales_6_bimestrales_1_anual(self):
        r = self.c.calendario_obligaciones("comercio", "I")
        assert len(r["obligaciones_mensuales"]) == 12
        assert len(r["obligaciones_bimestrales"]) == 6
        assert r["obligacion_anual"]["concepto"] == "DETERMINACION_PRIMA_RIESGO_TRABAJO"

    def test_clase_riesgo_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.calendario_obligaciones("comercio", "VI")

    def test_prima_rt_clase_i_correcta(self):
        r = self.c.calendario_obligaciones("comercio", "I")
        assert r["prima_riesgo_trabajo_pct"] == pytest.approx(0.54355, abs=0.001)


class TestSimuladorCostoPatronal:
    def setup_method(self):
        self.c = ImssPatronalClient()

    def test_factor_costo_sobre_salario_realista(self):
        r = self.c.simulador_costo_patronal(500.0, clase_riesgo="I")
        # Factor típico patronal MX: 1.3 a 1.5
        assert 1.20 <= r["factor_costo_sobre_salario"] <= 1.65

    def test_clase_riesgo_v_aumenta_costo(self):
        r_i = self.c.simulador_costo_patronal(500.0, clase_riesgo="I")
        r_v = self.c.simulador_costo_patronal(500.0, clase_riesgo="V")
        assert r_v["cuotas_imss_mensuales_mxn"]["riesgo_trabajo"] > r_i["cuotas_imss_mensuales_mxn"]["riesgo_trabajo"]
        assert r_v["costo_total_anual_estimado_mxn"] > r_i["costo_total_anual_estimado_mxn"]

    def test_clase_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.simulador_costo_patronal(500.0, clase_riesgo="X")


class TestPrimaRiesgoTrabajo:
    def setup_method(self):
        self.c = ImssPatronalClient()

    def test_sin_siniestralidad_prima_minima(self):
        r = self.c.riesgo_trabajo_prima_cambio(
            prima_actual=0.025, n_total_trabajadores=10
        )
        # Siniestralidad = 0, prima_calculada = M = 0.005, pero topada a -1% del actual
        assert r["aplicado_tope"] == "decremento_topado_1pct"
        assert r["prima_proxima_anio_pct"] == pytest.approx(1.5, abs=0.01)

    def test_siniestralidad_alta_topada_1pct(self):
        r = self.c.riesgo_trabajo_prima_cambio(
            prima_actual=0.025,
            s_dias_subsidiados=500,
            n_total_trabajadores=5,
            d_casos_defuncion=2,
        )
        assert r["aplicado_tope"] == "incremento_topado_1pct"
        assert r["prima_proxima_anio_pct"] == pytest.approx(3.5, abs=0.01)

    def test_prima_actual_fuera_rango_falla(self):
        with pytest.raises(ValidationError):
            self.c.riesgo_trabajo_prima_cambio(prima_actual=0.001, n_total_trabajadores=1)
        with pytest.raises(ValidationError):
            self.c.riesgo_trabajo_prima_cambio(prima_actual=0.20, n_total_trabajadores=1)

    def test_n_trabajadores_cero_falla(self):
        with pytest.raises(ValidationError):
            self.c.riesgo_trabajo_prima_cambio(prima_actual=0.025, n_total_trabajadores=0)
