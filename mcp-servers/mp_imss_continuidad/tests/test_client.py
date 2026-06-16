"""Tests mp_imss_continuidad."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_imss_continuidad.client import (
    ImssContinuidadClient,
    SISTEMAS_SUSTANTIVOS_IMSS,
)
from shared.errors import ValidationError


class TestSistemasSustantivos:
    def setup_method(self):
        self.c = ImssContinuidadClient()

    def test_8_sistemas(self):
        r = self.c.listar_sistemas_sustantivos()
        assert r["total"] == 8

    def test_idse_criticidad_muy_alta(self):
        r = self.c.listar_sistemas_sustantivos()
        idse = next(s for s in r["sistemas"] if s["clave"] == "idse")
        assert idse["criticidad"] == "muy_alta"
        assert idse["rto_horas"] == 4


class TestHealthCheck:
    def setup_method(self):
        self.c = ImssContinuidadClient()

    def test_idse_status_valido(self):
        r = self.c.health_check_sistema("idse")
        assert r["status_actual"] in ("verde", "amarillo", "rojo")
        assert "latencia_ms" in r

    def test_clave_invalida_falla(self):
        with pytest.raises(ValidationError):
            self.c.health_check_sistema("inexistente")


class TestPlanContinuidad:
    def setup_method(self):
        self.c = ImssContinuidadClient()

    def test_plan_idse_estrategia_activo_activo(self):
        r = self.c.plan_continuidad("idse")
        assert "activo-activo" in r["estrategia_recuperacion"]
        assert r["rto_objetivo_horas"] == 4

    def test_plan_alfresco_activo_pasivo(self):
        r = self.c.plan_continuidad("alfresco_documental")
        assert "activo-pasivo" in r["estrategia_recuperacion"]

    def test_plan_referencia_iso_22301(self):
        r = self.c.plan_continuidad("idse")
        assert any("22301" in f for f in r["fundamento_normativo"])

    def test_sla_uptime_99_95_para_muy_alta(self):
        r = self.c.plan_continuidad("sua")
        assert r["metricas_sla_mensual"]["uptime_objetivo_pct"] == 99.95


class TestReporteEjecutivo:
    def setup_method(self):
        self.c = ImssContinuidadClient()

    def test_reporte_estructura(self):
        r = self.c.reporte_ejecutivo("2026-05")
        assert r["periodo"] == "2026-05"
        assert r["formato_compatible_licitacion"] is True
        assert "detalle_por_sistema" in r

    def test_periodo_invalido_falla(self):
        with pytest.raises(ValidationError):
            self.c.reporte_ejecutivo("malformato")

    def test_uptime_promedio_entre_0_y_100(self):
        r = self.c.reporte_ejecutivo("2026-04")
        assert 0 <= r["uptime_promedio_periodo_pct"] <= 100
