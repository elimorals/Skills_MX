"""Tests mp_cofepris_aviso_funcionamiento."""
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


def test_clasificar_restaurante_giro_b():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    c = COFEPRISAvisoClient()
    r = c.clasificar_giro(actividad="restaurante")
    assert r["giro_cofepris"] == "B"
    assert r["requiere_aviso"] is True


def test_clasificar_farmacia_giro_c():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    c = COFEPRISAvisoClient()
    r = c.clasificar_giro(actividad="farmacia")
    assert r["giro_cofepris"] == "C"
    assert r["requiere_responsable_sanitario"] is True


def test_clasificar_tienda_giro_a():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    c = COFEPRISAvisoClient()
    r = c.clasificar_giro(actividad="tienda_abarrotes")
    assert r["giro_cofepris"] == "A"
    assert r["requiere_aviso"] is False


def test_clasificar_no_catalogado():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    c = COFEPRISAvisoClient()
    r = c.clasificar_giro(actividad="actividad_extrania")
    assert r["giro_cofepris"] == "no_clasificado"


def test_requisitos_giro_c_incluye_responsable():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    c = COFEPRISAvisoClient()
    r = c.requisitos_aviso(actividad="consultorio_medico", estado="cdmx")
    assert any("responsable" in req.lower() for req in r["requisitos"])


def test_requisitos_giro_a_no_aviso():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    c = COFEPRISAvisoClient()
    r = c.requisitos_aviso(actividad="papeleria", estado="cdmx")
    assert r["requiere_aviso"] is False


def test_consultar_aviso_corto():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    from shared.errors import ValidationError
    c = COFEPRISAvisoClient()
    with pytest.raises(ValidationError):
        c.consultar_aviso(identificador="x")


def test_listar_giros_clasificacion():
    from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient
    c = COFEPRISAvisoClient()
    r = c.listar_giros_catalogo()
    assert r["por_clasificacion"]["A"] >= 1
    assert r["por_clasificacion"]["B"] >= 5
    assert r["por_clasificacion"]["C"] >= 5
