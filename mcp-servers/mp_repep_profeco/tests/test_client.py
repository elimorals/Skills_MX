"""Tests mp_repep_profeco."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_repep_profeco.client import REPEPClient, _normalizar_telefono  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_normaliza_formatos():
    assert _normalizar_telefono("+52 (55) 5568-8722") == "5555688722"
    assert _normalizar_telefono("525555688722") == "5555688722"
    with pytest.raises(ValidationError):
        _normalizar_telefono("123")


def test_consultar_es_handoff_sin_inventar():
    r = REPEPClient().consultar("5555688722")
    assert r["handoff_humano"] is True
    assert r["inscrito_repep"] is None
    assert r["simulated"] is False


def test_filtrar_sin_lista_no_afirma_contactable():
    r = REPEPClient().filtrar_lote(["5555688722"])
    assert r["filtrado"] is False
    assert "contactables" not in r


def test_filtrar_con_lista_oficial(tmp_path):
    lista = tmp_path / "repep.csv"
    lista.write_text("telefono,fecha\n5555688722,29/06/2021\n8112345678,01/01/2024\n")
    r = REPEPClient().filtrar_lote(["55 5568 8722", "3312345678", "abc"], str(lista))
    assert r["filtrado"] is True
    assert r["bloqueados_repep"] == ["5555688722"]
    assert r["contactables"] == ["3312345678"]
    assert r["invalidos"] == ["abc"]


def test_lista_ilegible_no_vuelve_todo_contactable(tmp_path):
    lista = tmp_path / "repep.csv"
    lista.write_text("lada,numero\n55,55688722\n")
    with pytest.raises(ValidationError):
        REPEPClient().filtrar_lote(["5555688722"], str(lista))


def test_inscribir_nunca_inscribe():
    r = REPEPClient().inscribir("5555688722")
    assert r["inscrito"] is False
    assert r["handoff_humano"] is True


def test_estadisticas_sin_cifras_inventadas():
    r = REPEPClient().estadisticas()
    assert r["inscritos_publicados"] is None


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    assert REPEPClient().consultar("5555688722")["simulated"] is True
