"""Tests mp_cfe_interconexion_solar."""
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


def test_solicitar_pyme_pdbt():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    c = CFEInterconexionClient()
    r = c.solicitar_interconexion(rpu="123456789012", kw_instalados=5.0,
                                    tarifa_actual="PDBT")
    assert r["folio"].startswith("SOL-")
    assert r["costo_solicitud"] == 0.0
    assert r["kw_instalados"] == 5.0
    assert len(r["documentos_requeridos"]) >= 4


def test_solicitar_kw_fuera_rango():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    from shared.errors import ValidationError
    c = CFEInterconexionClient()
    with pytest.raises(ValidationError):
        c.solicitar_interconexion(rpu="123456789012", kw_instalados=600,
                                    tarifa_actual="PDBT")


def test_solicitar_tarifa_invalida():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    from shared.errors import ValidationError
    c = CFEInterconexionClient()
    with pytest.raises(ValidationError):
        c.solicitar_interconexion(rpu="123456789012", kw_instalados=5.0,
                                    tarifa_actual="XXX")


def test_solicitar_pequena_escala():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    c = CFEInterconexionClient()
    r = c.solicitar_interconexion(rpu="123456789012", kw_instalados=0.3,
                                    tarifa_actual="DAC")
    assert "Pequeña escala" in r["categoria_regulatoria"]


def test_consultar_estatus_devuelve_avance():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    c = CFEInterconexionClient()
    r = c.consultar_estatus_solicitud(folio="SOL-ABC1234567B")  # ends in B → contrato_firmado
    assert r["porcentaje_avance"] == 100


def test_consultar_estatus_folio_invalido():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    from shared.errors import ValidationError
    c = CFEInterconexionClient()
    with pytest.raises(ValidationError):
        c.consultar_estatus_solicitud(folio="BAD")


def test_simular_ahorro_dac():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    c = CFEInterconexionClient()
    r = c.simular_ahorro_prosumidor(tarifa_actual="DAC",
                                     kwh_consumo_promedio_mensual=400,
                                     kwh_generacion_solar_estimada=350)
    assert r["ahorro_mensual_mxn"] > 0
    assert r["ahorro_anual_mxn"] > r["ahorro_mensual_mxn"]


def test_simular_exportacion_vale_menos_2026():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    c = CFEInterconexionClient()
    r = c.simular_ahorro_prosumidor(tarifa_actual="DAC",
                                     kwh_consumo_promedio_mensual=100,
                                     kwh_generacion_solar_estimada=500)
    # 100 autoconsumo + 400 exportación * 0.70
    assert r["factor_exportacion_2026"] == 0.70
    assert r["exportacion_kwh"] == 400.0


def test_listar_tarifas_5_disponibles():
    from mp_cfe_interconexion_solar.client import CFEInterconexionClient
    c = CFEInterconexionClient()
    r = c.listar_tarifas()
    assert r["total"] == 5
