"""Tests mp_ley_silla_nom037."""
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


def test_verificar_retail_5_empleados():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.verificar_compliance(rfc="XAXX010101000", num_empleados=5,
                                giro="retail_comercio")
    assert r["score_compliance"] == 100  # Sin faltas marcadas
    assert r["no_cumplidas"] == 0
    assert any(o["marco"] == "Ley Silla" for o in r["checklist"])
    assert r["riesgo_inspeccion_stps"] == "bajo"


def test_verificar_con_faltas():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.verificar_compliance(rfc="XAXX010101000", num_empleados=20,
                                giro="manufactura",
                                faltas_marcadas=["silla_ergonomica_disponible",
                                                  "evaluacion_ergonomica_puestos"])
    assert r["no_cumplidas"] == 2
    assert r["multa_potencial_min_mxn"] > 0
    assert r["riesgo_inspeccion_stps"] in ("medio", "medio_alto", "alto")


def test_modalidad_remota_dispara_nom037():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.verificar_compliance(rfc="XAXX010101000", num_empleados=10,
                                giro="oficina_administrativo", modalidad_remota=True)
    assert any(o["marco"] == "NOM-037" for o in r["checklist"])


def test_empresa_50_empleados_nom035_completo():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.verificar_compliance(rfc="XAXX010101000", num_empleados=75,
                                giro="oficina_administrativo")
    obligaciones_nom035 = [o for o in r["checklist"] if o["marco"] == "NOM-035"]
    # >50 empleados dispara Guía III + programa + capacitación
    claves = {o["clave"] for o in obligaciones_nom035}
    assert "cuestionario_entorno_organizacional_50" in claves
    assert "programa_prevencion_documentado" in claves


def test_rfc_invalido_lanza():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    from shared.errors import ValidationError
    c = LeySillaNomClient()
    with pytest.raises(ValidationError):
        c.verificar_compliance(rfc="XX", num_empleados=5, giro="retail_comercio")


def test_giro_invalido_lanza():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    from shared.errors import ValidationError
    c = LeySillaNomClient()
    with pytest.raises(ValidationError):
        c.verificar_compliance(rfc="XAXX010101000", num_empleados=5,
                                giro="giro_inventado")


def test_calcular_multa_grave():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.calcular_multa(severidad="grave")
    assert r["multa_min_mxn"] > 50_000
    assert r["multa_max_mxn"] < 1_000_000


def test_calcular_multa_reincidente_duplica():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    base = c.calcular_multa(severidad="muy_grave", reincidente=False)
    rein = c.calcular_multa(severidad="muy_grave", reincidente=True)
    assert rein["multa_max_mxn"] == base["multa_max_mxn"] * 2


def test_generar_politica_devuelve_markdown():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.generar_politica(rfc="XAXX010101000", razon_social="DEMO SA DE CV",
                            giro="retail_comercio", modalidad="presencial",
                            nombre_responsable_sst="Juan Pérez")
    assert "# Política" in r["contenido_md"]
    assert "DEMO SA DE CV" in r["contenido_md"]
    assert "Ley Silla" in r["contenido_md"]
    assert "Desconexión digital" in r["contenido_md"]
    assert r["longitud_chars"] > 500


def test_listar_obligaciones_ley_silla():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.listar_obligaciones(marco="ley_silla")
    assert r["total"] >= 5
    assert "obligaciones" in r


def test_listar_obligaciones_marco_invalido():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    from shared.errors import ValidationError
    c = LeySillaNomClient()
    with pytest.raises(ValidationError):
        c.listar_obligaciones(marco="inexistente")


def test_riesgo_critico_con_muy_grave():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    r = c.verificar_compliance(rfc="XAXX010101000", num_empleados=30,
                                giro="oficina_administrativo",
                                faltas_marcadas=["medidas_contra_violencia_laboral"])
    assert r["riesgo_inspeccion_stps"] == "critico"
