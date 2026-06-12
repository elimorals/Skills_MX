"""Tests para mp_aspel_contpaqi/client.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from mp_aspel_contpaqi.client import AspelContpaqiClient
from mp_aspel_contpaqi.tests.conftest import (
    CSV_BALANZA_DEMO,
    CSV_CATALOGO_DEMO,
    CSV_POLIZAS_DEMO,
)
from shared.errors import McpError


@pytest.fixture
def client() -> AspelContpaqiClient:
    return AspelContpaqiClient()


# ---------- mock mode ----------


def test_listar_polizas_mock(client: AspelContpaqiClient) -> None:
    r = client.listar_polizas(2026, 3)
    assert r["simulated"] is True
    assert r["total_polizas"] >= 1
    assert r["ejercicio"] == 2026


def test_listar_polizas_filtra_por_tipo(client: AspelContpaqiClient) -> None:
    r = client.listar_polizas(2026, 3, tipo="INGRESOS")
    assert all(p["tipo"] == "INGRESOS" for p in r["polizas"])


def test_get_poliza_mock(client: AspelContpaqiClient) -> None:
    r = client.get_poliza("D-001")
    assert r["simulated"] is True
    assert r["numero"] == "D-001"


def test_balanza_mock(client: AspelContpaqiClient) -> None:
    r = client.obtener_balanza_comprobacion(2026, 3)
    assert r["simulated"] is True
    assert len(r["cuentas"]) > 0


def test_catalogo_cuentas_mock(client: AspelContpaqiClient) -> None:
    r = client.obtener_catalogo_cuentas()
    assert r["simulated"] is True
    assert r["total_cuentas"] > 0


def test_estado_resultados_mock(client: AspelContpaqiClient) -> None:
    r = client.obtener_estado_resultados(2026, 3)
    assert r["simulated"] is True
    assert "utilidad_neta" in r


def test_balance_general_mock(client: AspelContpaqiClient) -> None:
    r = client.obtener_balance_general(2026, 3)
    assert r["simulated"] is True
    assert "activo" in r
    assert "pasivo" in r
    assert "capital" in r


# ---------- export mode (con ASPEL_EXPORTS_DIR) ----------


@pytest.fixture
def exports_dir(tmp_path: Path, monkeypatch) -> Path:
    """Crea un directorio con exports CSV demo."""
    exports = tmp_path / "exports"
    exports.mkdir()
    (exports / "polizas_202603.csv").write_text(CSV_POLIZAS_DEMO, encoding="utf-8")
    (exports / "balanza_202603.csv").write_text(CSV_BALANZA_DEMO, encoding="utf-8")
    (exports / "catalogo_cuentas.csv").write_text(CSV_CATALOGO_DEMO, encoding="utf-8")
    monkeypatch.setenv("ASPEL_EXPORTS_DIR", str(exports))
    return exports


def test_listar_polizas_real(exports_dir: Path) -> None:
    client = AspelContpaqiClient()
    r = client.listar_polizas(2026, 3)
    assert r.get("simulated") is False
    # Debe haber 2 pólizas según CSV_POLIZAS_DEMO (D-001 e I-002)
    assert r["total_polizas"] == 2


def test_balanza_real(exports_dir: Path) -> None:
    client = AspelContpaqiClient()
    r = client.obtener_balanza_comprobacion(2026, 3)
    assert r.get("simulated") is False
    assert r["total_cuentas"] == 3


def test_catalogo_cuentas_real(exports_dir: Path) -> None:
    client = AspelContpaqiClient()
    r = client.obtener_catalogo_cuentas()
    assert r.get("simulated") is False
    assert r["total_cuentas"] == 3


def test_get_poliza_real_encontrada(exports_dir: Path) -> None:
    client = AspelContpaqiClient()
    r = client.get_poliza("D-001")
    assert r.get("simulated") is False
    assert r["numero"] == "D-001"


def test_get_poliza_real_no_encontrada(exports_dir: Path) -> None:
    client = AspelContpaqiClient()
    with pytest.raises(McpError):
        client.get_poliza("ZZZ-999")


def test_get_poliza_sin_exports_dir() -> None:
    """Sin ASPEL_EXPORTS_DIR ni mock (path imposible — fixture autouse fuerza mock)."""
    # Como conftest fuerza mock por default, este test verifica que mock funciona
    client = AspelContpaqiClient()
    r = client.get_poliza("X-001")
    assert r["simulated"] is True


# ---------- parsear_export utility ----------


def test_parsear_export_polizas_inline(client: AspelContpaqiClient) -> None:
    r = client.parsear_export("polizas", CSV_POLIZAS_DEMO)
    assert r["tipo"] == "polizas"
    assert r["total"] == 2


def test_parsear_export_balanza_inline(client: AspelContpaqiClient) -> None:
    r = client.parsear_export("balanza", CSV_BALANZA_DEMO)
    assert r["tipo"] == "balanza"
    assert r["total"] == 3


def test_parsear_export_tipo_desconocido(client: AspelContpaqiClient) -> None:
    with pytest.raises(McpError):
        client.parsear_export("xxx_desconocido", "data,1\n")
