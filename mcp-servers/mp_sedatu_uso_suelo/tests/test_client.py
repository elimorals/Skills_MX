"""Tests mp_sedatu_uso_suelo."""
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


def test_buscar_licencia_uso_suelo():
    from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient
    c = SEDATUUsoSueloClient()
    r = c.buscar_tramite(estado="cdmx", municipio="Cuauhtemoc",
                           clave_tramite="licencia_uso_suelo")
    assert "Licencia" in r["nombre"]
    assert len(r["requisitos"]) >= 4


def test_buscar_tramite_inexistente():
    from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient
    from shared.errors import NotFoundError
    c = SEDATUUsoSueloClient()
    with pytest.raises(NotFoundError):
        c.buscar_tramite(estado="cdmx", municipio="x", clave_tramite="inventado")


def test_consultar_uso_industrial():
    from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient
    c = SEDATUUsoSueloClient()
    r = c.consultar_uso_suelo_permitido(estado="edomex", municipio="Toluca",
                                          giro_propuesto="industrial plástico")
    assert "industrial_ligero" in r["usos_suelo_compatibles"]


def test_consultar_uso_comercio():
    from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient
    c = SEDATUUsoSueloClient()
    r = c.consultar_uso_suelo_permitido(estado="jal", municipio="Guadalajara",
                                          giro_propuesto="restaurante de comida rapida")
    assert any("comercial" in u or "mixto" in u for u in r["usos_suelo_compatibles"])


def test_estimar_construccion_pequena():
    from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient
    c = SEDATUUsoSueloClient()
    r = c.estimar_construccion(estado="cdmx", municipio="MH", m2_construir=200,
                                 uso="habitacional")
    assert "pequena_escala" in r["categoria_regulatoria"]


def test_estimar_construccion_gran_escala():
    from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient
    c = SEDATUUsoSueloClient()
    r = c.estimar_construccion(estado="cdmx", municipio="MH", m2_construir=15000,
                                 uso="comercial")
    assert "gran_escala" in r["categoria_regulatoria"]
    assert any("MIA" in e for e in r["estudios_requeridos"])


def test_listar_tramites_6():
    from mp_sedatu_uso_suelo.client import SEDATUUsoSueloClient
    c = SEDATUUsoSueloClient()
    r = c.listar_tramites()
    assert r["total"] >= 6
    assert len(r["usos_suelo_catalogo"]) >= 10
