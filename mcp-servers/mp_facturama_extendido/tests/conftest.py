"""Shared fixtures for mp_facturama_extendido tests.

Every test runs with isolated cache + audit dirs and no real Facturama creds.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Isolate cache + audit log per test so they never collide."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("FACTURAMA_USER", raising=False)
    monkeypatch.delenv("FACTURAMA_PASSWORD", raising=False)
    monkeypatch.delenv("FACTURAMA_API_KEY", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


@pytest.fixture
def valid_payload() -> dict:
    """A minimal payload that should pass validation.

    PFAE freelance → PM client, single concept, MXN, PUE+SPEI.
    Fecha calculated dynamically to stay within the ±72h window.
    """
    now = datetime.now(timezone(__import__("datetime").timedelta(hours=-6)))
    fecha_iso = now.replace(microsecond=0).isoformat()

    return {
        "emisor": {
            "rfc": "MAJG800101XYZ",
            "razon_social": "Juan Martínez Gómez",
            "regimen_fiscal": "612",
            "cp_lugar_expedicion": "06700",
        },
        "receptor": {
            "rfc": "IBM970131DRA",
            "nombre": "IBM de México SA",
            "regimen_fiscal": "601",
            "cp_domicilio": "11520",
            "uso_cfdi": "G03",
        },
        "comprobante": {
            "tipo_comprobante": "I",
            "moneda": "MXN",
            "metodo_pago": "PUE",
            "forma_pago": "03",
            "exportacion": "01",
            "fecha": fecha_iso,
        },
        "conceptos": [
            {
                "clave_prod_serv": "80141600",
                "descripcion": "Servicios de consultoría empresarial — marzo 2026",
                "clave_unidad": "E48",
                "cantidad": 1,
                "valor_unitario": 10000.00,
                "importe": 10000.00,
                "objeto_imp": "02",
            }
        ],
        "subtotal": 10000.00,
        "impuestos": {
            "total_trasladados": 1600.00,
            "total_retenidos": 2066.67,
        },
        "total": 9533.33,
    }
