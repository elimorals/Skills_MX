"""Shared fixtures for mp_curp_renapo tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Isolate cache + audit + default to mock."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("CURP_RENAPO_PLAYWRIGHT", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


def make_valid_curp(base_17: str) -> str:
    """Helper: dado un base de 17 chars, calcula el dígito y devuelve CURP completa.

    Útil para construir CURPs sintéticas con dígito correcto sin depender de
    ejemplos externos que podrían levantar flags del secret-scanner.
    """
    from mp_curp_renapo.validacion import calcular_digito_verificador

    digito = calcular_digito_verificador(base_17)
    assert digito >= 0, f"Cannot compute digit for {base_17!r}"
    return base_17 + str(digito)
