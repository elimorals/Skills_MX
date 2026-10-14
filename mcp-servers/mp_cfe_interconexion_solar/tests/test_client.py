"""Tests mp_cfe_interconexion_solar — umbrales LSE, handoffs y modelo de ahorro."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_cfe_interconexion_solar.client import CFEInterconexionClient, clasificar_central  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_umbral_generadora_exenta_0_7_mw():
    assert clasificar_central(699.9)["categoria"] == "generacion_distribuida_exenta"
    assert clasificar_central(700)["requiere_permiso_cne"] is True
    assert clasificar_central(20_000)["categoria"] == "autoconsumo_permiso_simplificado"
    assert clasificar_central(20_001)["categoria"] == "central_con_permiso"


def test_solicitar_es_handoff_sin_folio():
    r = CFEInterconexionClient().solicitar_interconexion("123456789012", 5.5, "PDBT")
    assert r["enviada"] is False
    assert r["handoff_humano"] is True
    assert "folio" not in r
    assert r["categoria"] == "generacion_distribuida_exenta"


def test_solicitar_validaciones():
    c = CFEInterconexionClient()
    with pytest.raises(ValidationError):
        c.solicitar_interconexion("123", 5, "PDBT")
    with pytest.raises(ValidationError):
        c.solicitar_interconexion("123456789012", 5, "TARIFA_X")


def test_estatus_handoff():
    r = CFEInterconexionClient().consultar_estatus_solicitud("SOL-ABC123")
    assert r["estatus"] is None and r["handoff_humano"] is True


def test_medicion_neta_compensa_hasta_consumo():
    r = CFEInterconexionClient().simular_ahorro_prosumidor(4.0, 500, 650)
    assert r["kwh_compensados"] == 500
    assert r["kwh_saldo_a_favor"] == 150
    assert r["ahorro_mensual_mxn"] == 2000.0


def test_facturacion_neta_requiere_precio():
    c = CFEInterconexionClient()
    with pytest.raises(ValidationError):
        c.simular_ahorro_prosumidor(4.0, 500, 650, esquema="facturacion_neta")
    r = c.simular_ahorro_prosumidor(4.0, 500, 650, esquema="facturacion_neta", precio_exportacion_mxn_kwh=1.5)
    assert r["ahorro_mensual_mxn"] == 500 * 4.0 + 150 * 1.5


def test_tarifas_sin_precios_inventados():
    r = CFEInterconexionClient().listar_tarifas()
    assert all("costo_kwh_promedio_mxn" not in t for t in r["tarifas"])
