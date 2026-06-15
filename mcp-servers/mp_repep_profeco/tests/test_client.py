"""Tests mp_repep_profeco."""
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


def test_consultar_normaliza_telefono():
    from mp_repep_profeco.client import REPEPClient
    c = REPEPClient()
    r = c.consultar(telefono="+52 55-1234-5678")
    assert r["telefono"] == "5512345678"


def test_consultar_tel_invalido():
    from mp_repep_profeco.client import REPEPClient
    from shared.errors import ValidationError
    c = REPEPClient()
    with pytest.raises(ValidationError):
        c.consultar(telefono="abc")


def test_filtrar_lote_basico():
    from mp_repep_profeco.client import REPEPClient
    c = REPEPClient()
    r = c.filtrar_lote(telefonos=["5512345670", "5512345671", "5512345672"])
    assert r["total_input"] == 3
    assert r["stats"]["contactables_count"] + r["stats"]["bloqueados_count"] == 3


def test_filtrar_lote_vacio():
    from mp_repep_profeco.client import REPEPClient
    from shared.errors import ValidationError
    c = REPEPClient()
    with pytest.raises(ValidationError):
        c.filtrar_lote(telefonos=[])


def test_inscribir():
    from mp_repep_profeco.client import REPEPClient
    c = REPEPClient()
    r = c.inscribir(telefono="5512345678")
    assert r["inscripcion_exitosa"] is True


def test_estadisticas():
    from mp_repep_profeco.client import REPEPClient
    c = REPEPClient()
    r = c.estadisticas()
    assert r["multa_min_uma"] == 100
    assert r["multa_max_uma"] == 5000
