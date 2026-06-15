"""Tests mp_simplifica_ciudadano."""
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


def test_estado_cdmx():
    from mp_simplifica_ciudadano.client import SimplificaCiudadanoClient
    c = SimplificaCiudadanoClient()
    r = c.estado(estado_clave="cdmx")
    assert r["avance_pct"] > 50
    assert len(r["destacados"]) >= 1


def test_estado_inexistente():
    from mp_simplifica_ciudadano.client import SimplificaCiudadanoClient
    from shared.errors import ValidationError
    c = SimplificaCiudadanoClient()
    with pytest.raises(ValidationError):
        c.estado(estado_clave="xx99")


def test_tracker_nacional_32_estados():
    from mp_simplifica_ciudadano.client import SimplificaCiudadanoClient
    c = SimplificaCiudadanoClient()
    r = c.tracker_nacional()
    assert r["total_estados_monitoreados"] == 32
    assert len(r["estados_top_3"]) == 3


def test_comparar_estados():
    from mp_simplifica_ciudadano.client import SimplificaCiudadanoClient
    c = SimplificaCiudadanoClient()
    r = c.comparar_estados(estados_claves=["cdmx", "edomex", "jal", "oax"])
    assert len(r["comparacion"]) == 4
    assert r["lider"]["avance_pct"] >= r["rezagado"]["avance_pct"]


def test_comparar_lista_vacia():
    from mp_simplifica_ciudadano.client import SimplificaCiudadanoClient
    from shared.errors import ValidationError
    c = SimplificaCiudadanoClient()
    with pytest.raises(ValidationError):
        c.comparar_estados(estados_claves=[])
