"""Tests mp_verificacion_vehicular_mx."""
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
    yield


class TestCalcularPeriodo:
    def test_terminacion_5_amarillo(self):
        from shared.verificacion_vehicular import calcular_proximo_periodo
        color, meses = calcular_proximo_periodo(5, 6)
        assert color == "amarillo"
        assert 3 in meses

    def test_terminacion_1_verde(self):
        from shared.verificacion_vehicular import calcular_proximo_periodo
        color, _ = calcular_proximo_periodo(1, 6)
        assert color == "verde"

    def test_terminacion_invalida(self):
        from shared.verificacion_vehicular import calcular_proximo_periodo
        with pytest.raises(ValueError):
            calcular_proximo_periodo(15, 6)


class TestConsultar:
    def test_consultar_estatus_cdmx(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        c = VerificacionVehicularClient()
        r = c.consultar_estatus("ABC1234", "cdmx")
        assert "holograma_actual" in r
        assert r["simulated"] is True

    def test_estado_inexistente(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        from shared.errors import NotFoundError
        c = VerificacionVehicularClient()
        with pytest.raises(NotFoundError):
            c.consultar_estatus("ABC1234", "xx")

    def test_placa_corta(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        from shared.errors import ValidationError
        c = VerificacionVehicularClient()
        with pytest.raises(ValidationError):
            c.consultar_estatus("A1", "cdmx")


class TestProximoPeriodo:
    def test_proximo_terminacion_5(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        c = VerificacionVehicularClient()
        r = c.proximo_periodo("ABC1235", "cdmx")  # terminacion 5
        assert r["color_engomado"] == "amarillo"
        assert r["terminacion"] == 5

    def test_listar_7_programas(self):
        from mp_verificacion_vehicular_mx.client import VerificacionVehicularClient
        c = VerificacionVehicularClient()
        r = c.listar_programas()
        assert r["total"] == 7
