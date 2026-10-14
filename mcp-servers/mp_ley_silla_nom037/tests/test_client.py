"""Tests mp_ley_silla_nom037."""
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
                                faltas_marcadas=["sillas_industria_si_lo_permite",
                                                  "no_obligar_estar_de_pie"])
    assert r["no_cumplidas"] == 2
    # Ambas por Art. 1002 LFT: 50-5000 UMA cada una, UMA 2026 = 117.31
    assert r["multa_potencial_min_mxn"] == round(2 * 50 * 117.31, 2)
    assert r["multa_potencial_max_mxn"] == round(2 * 5000 * 117.31, 2)
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
    # NOM-035 numeral 2 c): >50 → 5.1, 5.3-5.8 (sin 5.2)
    claves = {o["clave"] for o in obligaciones_nom035}
    assert "identificar_factores_y_entorno_mas_50" in claves
    assert "identificar_factores_riesgo_16_50" not in claves
    assert "identificar_acontecimientos_traumaticos" in claves


def test_nom035_hasta_15_solo_numerales_basicos():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    r = LeySillaNomClient().verificar_compliance(rfc="XAXX010101000", num_empleados=15,
                                                 giro="oficina_administrativo")
    claves = {o["clave"] for o in r["checklist"] if o["marco"] == "NOM-035"}
    # numeral 2 a): 5.1, 5.4, 5.5, 5.7
    assert claves == {"politica_prevencion_psicosociales", "medidas_prevencion_control",
                      "identificar_acontecimientos_traumaticos", "difundir_informacion"}


def test_desconexion_solo_teletrabajo():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    presencial = c.verificar_compliance(rfc="XAXX010101000", num_empleados=5, giro="retail_comercio")
    assert not any(o["marco"] == "Desconexión digital" for o in presencial["checklist"])
    remoto = c.verificar_compliance(rfc="XAXX010101000", num_empleados=5, giro="oficina_administrativo",
                                    modalidad_remota=True)
    assert any(o["base_legal"].startswith("LFT Art. 330-E") for o in remoto["checklist"])


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
    r = c.calcular_multa(fundamento="lft_994_v")
    assert r["rango_uma"] == [250, 5000]
    assert r["multa_min_mxn"] == round(250 * 117.31, 2)
    assert r["multa_max_mxn"] == round(5000 * 117.31, 2)


def test_calcular_multa_reincidente_duplica():
    from mp_ley_silla_nom037.client import LeySillaNomClient
    c = LeySillaNomClient()
    base = c.calcular_multa(fundamento="lft_1002", reincidente=False)
    rein = c.calcular_multa(fundamento="lft_1002", reincidente=True)
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
    assert "marzo 2026" not in r["contenido_md"]
    assert "XVII Bis" in r["contenido_md"]
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
                                modalidad_remota=True,
                                faltas_marcadas=["contrato_escrito"])
    assert r["riesgo_inspeccion_stps"] == "critico"
