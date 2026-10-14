"""Tests mp_cofepris_aviso_funcionamiento — reglas LGS (Arts. 197, 198, 200 Bis, 260)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_cofepris_aviso_funcionamiento.client import COFEPRISAvisoClient  # noqa: E402
from shared.errors import ValidationError  # noqa: E402


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_restaurante_aviso():
    r = COFEPRISAvisoClient().clasificar_giro("restaurante")
    assert r["tramite"] == "aviso_funcionamiento"
    assert r["requiere_aviso"] is True
    assert "200 Bis" in r["fundamento"]


def test_quirofano_y_rayos_x_licencia():
    c = COFEPRISAvisoClient()
    assert c.clasificar_giro("hospital_quirurgico")["requiere_licencia"] is True
    assert "fr. IV" in c.clasificar_giro("consultorio dental con rayos x")["fundamento"]


def test_farmacia_depende_de_controlados():
    c = COFEPRISAvisoClient()
    con = c.clasificar_giro("farmacia_con_controlados")
    sin = c.clasificar_giro("farmacia_sin_controlados")
    assert con["tramite"] == "licencia_sanitaria" and con["responsable_sanitario"] is True
    assert sin["tramite"] == "aviso_funcionamiento" and sin["responsable_sanitario"] is False


def test_tienda_requiere_verificar():
    r = COFEPRISAvisoClient().clasificar_giro("tienda_abarrotes")
    assert r["tramite"] == "verificar_acuerdo_ssa"
    assert r["requiere_aviso"] is None


def test_no_catalogado():
    assert COFEPRISAvisoClient().clasificar_giro("actividad_extrania")["tramite"] is None


def test_requisitos_art_200_bis():
    r = COFEPRISAvisoClient().requisitos_aviso("consultorio_medico", "cdmx")
    assert len(r["requisitos"]) == 6
    assert "30 días" in r["plazo"]


def test_requisitos_licencia_no_es_aviso():
    r = COFEPRISAvisoClient().requisitos_aviso("hemodialisis", "cdmx")
    assert r["requiere_aviso"] is False
    assert r["tramite"] == "licencia_sanitaria"


def test_consultar_aviso_handoff():
    r = COFEPRISAvisoClient().consultar_aviso("XAXX010101000")
    assert r["handoff_humano"] is True
    assert r["vigente"] is None
    with pytest.raises(ValidationError):
        COFEPRISAvisoClient().consultar_aviso("x")


def test_listar_giros():
    r = COFEPRISAvisoClient().listar_giros_catalogo()
    assert r["por_tramite"]["licencia_sanitaria"] == 7
    assert r["total"] == sum(r["por_tramite"].values())
