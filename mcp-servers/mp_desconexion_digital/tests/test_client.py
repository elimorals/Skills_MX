"""Tests mp_desconexion_digital."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_checklist_sin_faltas():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    c = DesconexionDigitalClient()
    r = c.checklist_cumplimiento(rfc="XAXX010101000")
    assert r["score_cumplimiento"] == 100


def test_checklist_con_faltas():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    c = DesconexionDigitalClient()
    r = c.checklist_cumplimiento(rfc="XAXX010101000",
                                   faltas_marcadas=["politica_teletrabajo_con_desconexion"])
    assert r["score_cumplimiento"] < 100
    assert r["no_cumplidas"] == 1


def test_checklist_rfc_invalido():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    from shared.errors import ValidationError
    c = DesconexionDigitalClient()
    with pytest.raises(ValidationError):
        c.checklist_cumplimiento(rfc="XX")


def test_generar_politica_default():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    c = DesconexionDigitalClient()
    r = c.generar_politica(rfc="XAXX010101000", razon_social="DEMO SA",
                             jornada_inicio="09:00", jornada_fin="18:00")
    assert "DEMO SA" in r["contenido_md"]
    assert "Desconexión Digital" in r["contenido_md"]
    assert r["longitud_chars"] > 500


def test_generar_politica_canal_custom():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    c = DesconexionDigitalClient()
    r = c.generar_politica(rfc="XAXX010101000", razon_social="DEMO",
                             jornada_inicio="09", jornada_fin="18",
                             canal_denuncia_email="rh@demo.mx")
    assert "rh@demo.mx" in r["contenido_md"]


def test_template_capacitacion():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    c = DesconexionDigitalClient()
    r = c.template_capacitacion()
    assert len(r["agenda"]) == 5
    assert r["duracion_estimada_min"] == 45


def test_sin_teletrabajo_no_hay_obligacion_legal():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    r = DesconexionDigitalClient().checklist_cumplimiento(rfc="XAXX010101000", modalidad_teletrabajo=False)
    assert all(not c["obligatorio"] for c in r["checklist"])
    assert "330-A" in r["nota"]


def test_base_legal_real_sin_reforma_inventada():
    from mp_desconexion_digital.client import DesconexionDigitalClient
    c = DesconexionDigitalClient()
    r = c.checklist_cumplimiento(rfc="XAXX010101000")
    assert "330-E" in r["base_legal"] and "marzo" not in r["base_legal"]
    pol = c.generar_politica(rfc="XAXX010101000", razon_social="DEMO SA",
                             jornada_inicio="09:00", jornada_fin="18:00")
    assert "marzo 2026" not in pol["contenido_md"]
