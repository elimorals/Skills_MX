"""Shared fixtures for mp_banxico_cep tests."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_state(monkeypatch, tmp_path: Path) -> None:
    """Isolate cache + audit + default to mock."""
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.delenv("BANXICO_CEP_PLAYWRIGHT", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)


def make_valid_clabe(base_17: str) -> str:
    """Helper: dado un base de 17 dígitos, calcula el dígito y devuelve CLABE de 18.

    Igual que el helper de make_valid_curp pero para CLABE — para construir
    CLABEs sintéticas sin depender de ejemplos externos.
    """
    from mp_banxico_cep.clabe import calcular_digito_control_clabe

    assert len(base_17) == 17 and base_17.isdigit(), f"Bad base: {base_17!r}"
    d = calcular_digito_control_clabe(base_17)
    assert d >= 0
    return base_17 + str(d)
