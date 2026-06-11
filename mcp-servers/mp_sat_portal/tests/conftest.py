"""Shared fixtures para mp_sat_portal."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Isola cache + audit y default a mock.

    Cualquier credencial SAT existente en el env del runner se borra para
    que los tests sean deterministas en el modo mock.
    """
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("SAT_RFC", raising=False)
    monkeypatch.delenv("SAT_CIEC", raising=False)
    monkeypatch.delenv("SAT_EFIRMA_CERT", raising=False)
    monkeypatch.delenv("PLUGINS_MX_SAT_PERMITIR_ESCRITURA", raising=False)


# Constantes de prueba (RFCs ficticios pero estructuralmente válidos)

DEMO_RFC_PF = "DEMA850101001"  # Persona Física (13 chars)
DEMO_RFC_PM = "DEMO850101AA1"  # Persona Moral (12 chars, sin homoclave PM)
DEMO_RFC_PM_CORTO = "DEM850101AA1"  # 12 chars típicos PM

# UUIDs de prueba (v4 random válidos estructuralmente)
DEMO_UUID_VALIDO = "A1B2C3D4-E5F6-4789-9ABC-DEF012345678"  # versión 4 en pos 14
DEMO_UUID_VALIDO_2 = "12345678-1234-4234-9234-123456789012"
DEMO_UUID_FORMATO_MAL = "12345-NO-ES-UUID"
DEMO_UUID_LONGITUD_MAL = "A1B2C3D4-E5F6-4789-9ABC-DEF01234"
