"""Tests Sprint F INFONAVIT: descuento, créditos sin reporte, EMIS histórico, conciliación nómina."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_infonavit_patronal.client import InfonavitPatronalClient
from shared.errors import ValidationError


class TestDescuentoCalcular:
    def setup_method(self):
        self.c = InfonavitPatronalClient()

    def test_pesos_normal_factor_default(self):
        # SBC $500/d * 30 días = $15,000 mensual, factor 0.20 = $3,000
        r = self.c.descuento_calcular(500.0, "PESOS_NORMAL")
        assert r["sbc_mensual_mxn"] == 15000.0
        assert r["descuento_calculado_mxn"] == 3000.0
        assert r["descuento_final_mensual_mxn"] == 3000.0
        assert r["aplicado_cap_lft_art110"] is False

    def test_factor_excede_max_falla(self):
        with pytest.raises(ValidationError):
            self.c.descuento_calcular(500.0, "PESOS_NORMAL", factor_o_monto=0.50)

    def test_cuota_fija_pesos_usa_monto(self):
        r = self.c.descuento_calcular(500.0, "CUOTA_FIJA_PESOS", factor_o_monto=2500.0)
        assert r["descuento_final_mensual_mxn"] == 2500.0
        assert r["factor_aplicado"] is None

    def test_cap_lft_30pct(self):
        # Si descuento > 30% SBC mensual, se topa
        # Forzamos con factor 0.30 (que es el max) — debería estar exactamente en cap
        r = self.c.descuento_calcular(500.0, "PESOS_NORMAL", factor_o_monto=0.30)
        # Cap = 15000 * 0.30 = 4500, descuento = 15000 * 0.30 = 4500 — empate, no aplica cap
        assert r["aplicado_cap_lft_art110"] is False
        assert r["descuento_final_mensual_mxn"] == 4500.0

    def test_tipo_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.descuento_calcular(500.0, "TIPO_INEXISTENTE")

    def test_sbc_negativo_falla(self):
        with pytest.raises(ValidationError):
            self.c.descuento_calcular(-1.0, "PESOS_NORMAL")


class TestCreditosSinReporte:
    def setup_method(self):
        self.c = InfonavitPatronalClient()

    def test_devuelve_estructura_esperada(self):
        r = self.c.creditos_sin_reporte("Y123456789")
        assert "total_creditos_sin_reporte" in r
        assert "omisiones" in r
        assert isinstance(r["requiere_regularizacion"], bool)
        assert "fundamento" in r

    def test_rp_hasheado(self):
        r = self.c.creditos_sin_reporte("Y123456789")
        assert "registro_patronal_hash" in r
        assert len(r["registro_patronal_hash"]) >= 8

    def test_intereses_proporcionales_a_meses(self):
        r = self.c.creditos_sin_reporte("Y987654321")
        for o in r["omisiones"]:
            # Intereses ≈ descuento * meses * 0.018
            esperado = round(o["descuento_esperado_mensual_mxn"] * o["meses_omiso"] * 0.018, 2)
            assert abs(o["intereses_moratorios_estimados_mxn"] - esperado) < 0.05


class TestEmisHistorico:
    def setup_method(self):
        self.c = InfonavitPatronalClient()

    def test_3_anios_18_bimestres(self):
        r = self.c.emis_historico("Y123456789", anios=3)
        assert r["total_registros"] == 18
        assert r["anios_consultados"] == 3

    def test_anios_fuera_rango_falla(self):
        with pytest.raises(ValidationError):
            self.c.emis_historico("Y123456789", anios=0)
        with pytest.raises(ValidationError):
            self.c.emis_historico("Y123456789", anios=11)

    def test_monto_total_pagado_consistente(self):
        r = self.c.emis_historico("Y111111111", anios=2)
        pagados = [reg for reg in r["registros"] if reg["status"] == "PAGADO"]
        suma_manual = round(sum(reg["cuota_pagada_mxn"] for reg in pagados), 2)
        assert r["monto_total_pagado_mxn"] == suma_manual


class TestConciliacionNomina:
    def setup_method(self):
        self.c = InfonavitPatronalClient()

    def test_vacio_falla(self):
        with pytest.raises(ValidationError):
            self.c.conciliacion_nomina("Y123456789", [])

    def test_excede_5000_falla(self):
        big = [{"nss": "1234567890", "monto_mxn": 100.0, "periodo": "2026-01"}] * 5001
        with pytest.raises(ValidationError):
            self.c.conciliacion_nomina("Y123456789", big)

    def test_nss_invalido_detectado(self):
        r = self.c.conciliacion_nomina(
            "Y123456789",
            [
                {"nss": "12345", "monto_mxn": 100.0, "periodo": "2026-01"},
                {"nss": "1234567890", "monto_mxn": 100.0, "periodo": "2026-01"},
            ],
        )
        tipos = [d["tipo"] for d in r["diferencias"]]
        assert "NSS_INVALIDO" in tipos

    def test_devuelve_porcentaje_match(self):
        r = self.c.conciliacion_nomina(
            "Y123456789",
            [{"nss": "1234567890", "monto_mxn": 100.0, "periodo": "2026-01"}],
        )
        assert 0 <= r["porcentaje_match"] <= 100
