"""Tests para mp_sat_opinion_32d.

Fixtures capturados con Playwright MCP el 2026-06-14 del portal SAT 32-D real.
NO golpea el SAT en tests — uses mock + fixtures determinísticas.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Patch sys.path para importar shared/ y el cliente
_HERE = Path(__file__).resolve().parent
_MCP_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_MCP_ROOT))


# ---- Fixtures: respuestas reales del SAT ----
# Capturadas con Playwright MCP el 2026-06-14 contra el portal SAT 32-D.

FIXTURE_HTML_POSITIVA = """<div class="row" id="mensaje">
    <div class="col-sm-4"></div>
    <div class="col-sm-4">
        <div class="alert alert-success" id="dvMsjessuccess" style="text-align:center;">
            <label>Opinión Positiva.<br />* Información a la fecha de la consulta.</label>
        </div>
    </div>
    <div class="col-sm-4"></div>
</div>
<div id="showPdf" style="display:none;" class="row">
    <div class="col-12" style="height:600px;" id="dvReporteOpinion" />
</div>
<div id="contenidoBase64" style="display:none">JVBERi0xLjQKJaqrrK0KMSAwIG9iago8PAovQ3JlYXRvciAoQXBhY2hlIEZPUCBWZXJzaW9uIDIuMTEpCi9Qcm9kdWNlciAoQXBhY2hlIEZPUCBWZXJzaW9uIDIuMTEpCi9DcmVhdGlvbkRhdGUgKEQ6MjAyNjA2MTUwNDAzMDBaKQo+PgplbmRvYmoK</div>
"""

FIXTURE_HTML_NEGATIVA = """<div class="row" id="mensaje">
    <div class="col-sm-4"></div>
    <div class="col-sm-4">
        <div class="alert alert-danger" id="dvMsjesError" style="text-align:center;">
            <label>Opinión Negativa.<br />* Información a la fecha de la consulta.</label>
        </div>
    </div>
    <div class="col-sm-4"></div>
</div>
<div id="contenidoBase64" style="display:none">JVBERi0xLjQKJaqrrK0KMSAwIG9iago8PAovQ3JlYXRvciAoQXBhY2hlIEZPUCBWZXJzaW9uIDIuMTEpCj4+CmVuZG9iagoK</div>
"""

FIXTURE_JSON_NO_AUTORIZADO = {
    "MsjeIformativo": "El RFC o CURP consultado no se encuentra autorizado para hacerse público.<br>* Información a la fecha de la consulta."
}


# ============================================================
# Tests de validación estructural
# ============================================================

class TestValidacionRFC:
    """Tests de la regex RFC que copia 1:1 la del portal SAT."""

    def test_rfc_pm_valido(self):
        from shared.sat_opinion_32d import validar_estructura_rfc
        assert validar_estructura_rfc("PEP970814SF3")  # 12 chars PM
        assert validar_estructura_rfc("BBA830831LJ2")
        assert validar_estructura_rfc("SAT970701NN3")

    def test_rfc_pf_valido(self):
        from shared.sat_opinion_32d import validar_estructura_rfc
        # 13 chars: 4 letras + 6 fecha + 3 homoclave
        assert validar_estructura_rfc("MELO850115ABC")
        assert validar_estructura_rfc("XAXX010101000")  # RFC genérico

    def test_rfc_estructura_invalida(self):
        from shared.sat_opinion_32d import validar_estructura_rfc
        assert not validar_estructura_rfc("")
        assert not validar_estructura_rfc("ABC")
        assert not validar_estructura_rfc("XAXX99999ABC")    # mes 99 inválido
        assert not validar_estructura_rfc("XAXX011301000")   # mes 13 inválido
        assert not validar_estructura_rfc("XAXX010132000")   # día 32 inválido
        assert not validar_estructura_rfc("INVALIDO")        # solo letras
        assert not validar_estructura_rfc("AAA01010")        # corto

    def test_rfc_normalizacion_uppercase(self):
        from shared.sat_opinion_32d import validar_estructura_rfc
        assert validar_estructura_rfc("pep970814sf3")  # se debe upper

    def test_rfc_bisiesto_29_feb(self):
        from shared.sat_opinion_32d import validar_estructura_rfc
        # 2024 fue bisiesto → 29 feb válido
        assert validar_estructura_rfc("XYZ240229AB1")
        # 2023 no bisiesto → 29 feb inválido
        assert not validar_estructura_rfc("XYZ230229AB1")


class TestValidacionCURP:
    """Tests de la regex CURP idéntica al portal SAT."""

    def test_curp_valida(self):
        from shared.sat_opinion_32d import validar_estructura_curp
        assert validar_estructura_curp("PERD850301HDFRZG02")

    def test_curp_invalida(self):
        from shared.sat_opinion_32d import validar_estructura_curp
        assert not validar_estructura_curp("")
        assert not validar_estructura_curp("PERD850301HDFRZG0")  # falta dígito
        assert not validar_estructura_curp("XXXXXXXXXXXXXXXXXX")  # estado inválido


# ============================================================
# Tests de parsing HTML/JSON (con fixtures reales)
# ============================================================

class TestParsearRespuestaHTML:
    def test_positiva_extrae_estado_y_pdf(self):
        from shared.sat_opinion_32d import parsear_respuesta_html
        r = parsear_respuesta_html(FIXTURE_HTML_POSITIVA)
        assert r["estado"] == "positiva"
        assert "Opinión Positiva" in r["mensaje_oficial"]
        assert r["pdf_base64"] is not None
        assert r["pdf_base64"].startswith("JVBERi0")

    def test_negativa_extrae_estado(self):
        from shared.sat_opinion_32d import parsear_respuesta_html
        r = parsear_respuesta_html(FIXTURE_HTML_NEGATIVA)
        assert r["estado"] == "negativa"
        assert "Opinión Negativa" in r["mensaje_oficial"]
        assert r["pdf_base64"] is not None

    def test_html_vacio_devuelve_error(self):
        from shared.sat_opinion_32d import parsear_respuesta_html
        r = parsear_respuesta_html("<html></html>")
        assert r["estado"] == "error"


class TestParsearRespuestaJSON:
    def test_no_autorizado(self):
        from shared.sat_opinion_32d import parsear_respuesta_json
        r = parsear_respuesta_json(FIXTURE_JSON_NO_AUTORIZADO)
        assert r["estado"] == "no_autorizado"
        assert "no se encuentra autorizado" in r["mensaje_oficial"].lower()
        assert r["pdf_base64"] is None

    def test_no_inscrito_se_detecta_por_mensaje(self):
        from shared.sat_opinion_32d import parsear_respuesta_json
        r = parsear_respuesta_json({"MsjeIformativo": "El RFC no se encuentra inscrito en el padrón."})
        assert r["estado"] == "no_inscrito"


# ============================================================
# Tests del cliente (modo mock)
# ============================================================

@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch, tmp_path):
    """Default a mock mode + tmpdir para evitar contaminación cross-test."""
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))
    yield


class TestSatOpinion32DClient:
    def test_consultar_rfc_par_devuelve_positiva(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        # Mock determinístico: último char par → positiva
        r = c.consultar(rfc="PEP970814SF2")
        assert r["estado"] == "positiva"
        assert r["puede_contratar_con_gobierno"] is True
        assert r["simulated"] is True
        assert r["pdf_base64"] is not None

    def test_consultar_rfc_negativa(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        # mock: último char 7 o 9 → negativa
        r = c.consultar(rfc="PEP970814SF9")
        assert r["estado"] == "negativa"
        assert r["puede_contratar_con_gobierno"] is False

    def test_consultar_rfc_no_autorizado(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        # mock: último char 1,3,5 → no_autorizado
        r = c.consultar(rfc="PEP970814SF1")
        assert r["estado"] == "no_autorizado"
        assert r["puede_contratar_con_gobierno"] is False
        assert r["pdf_base64"] is None

    def test_consultar_rfc_invalido_lanza_validation_error(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        from shared.errors import ValidationError
        c = SatOpinion32DClient()
        with pytest.raises(ValidationError) as exc:
            c.consultar(rfc="INVALIDO")
        assert "inválida" in str(exc.value).lower() or "invalid" in str(exc.value).lower()

    def test_consultar_sin_rfc_ni_curp_lanza_error(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        from shared.errors import ValidationError
        c = SatOpinion32DClient()
        with pytest.raises(ValidationError):
            c.consultar()

    def test_curp_solo_funciona(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        r = c.consultar(curp="PERD850301HDFRZG02")
        assert r["estado"] in ("positiva", "negativa", "no_autorizado")

    def test_incluir_pdf_false_omite_pdf(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        r = c.consultar(rfc="PEP970814SF2", incluir_pdf=False)
        assert r["pdf_base64"] is None


class TestVerificarProveedor:
    def test_positiva_permite_contratar(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        r = c.verificar_proveedor("PEP970814SF2")
        assert r["puede_contratar_con_gobierno"] is True
        assert r["estado"] == "positiva"
        assert r["advertencias"] == []

    def test_negativa_genera_advertencia(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        r = c.verificar_proveedor("PEP970814SF9")
        assert r["puede_contratar_con_gobierno"] is False
        assert r["estado"] == "negativa"
        assert any("NEGATIVA" in adv for adv in r["advertencias"])

    def test_no_autorizado_explica_que_hacer(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        r = c.verificar_proveedor("PEP970814SF1")
        assert r["puede_contratar_con_gobierno"] is False
        assert any("Buzón" in adv for adv in r["advertencias"])

    def test_detalle_no_incluye_pdf(self):
        """verificar_proveedor llama consultar(incluir_pdf=False) para ahorrar payload."""
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        r = c.verificar_proveedor("PEP970814SF2")
        assert r["detalle"]["pdf_base64"] is None


# ============================================================
# Tests de la capa HTTP (parsing puro, sin red)
# ============================================================

class TestParseRespuestaHTTP:
    def test_json_no_autorizado(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        resp = MagicMock()
        resp.headers = {"content-type": "application/json; charset=utf-8"}
        resp.json.return_value = FIXTURE_JSON_NO_AUTORIZADO
        resp.text = ""
        r = c._parsear_respuesta(resp, rfc="XXX010101001", curp="")
        assert r["estado"] == "no_autorizado"
        assert r["puede_contratar_con_gobierno"] is False
        assert r["pdf_base64"] is None
        assert r["simulated"] is False

    def test_html_positiva(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        resp = MagicMock()
        resp.headers = {"content-type": "text/html; charset=utf-8"}
        resp.text = FIXTURE_HTML_POSITIVA
        r = c._parsear_respuesta(resp, rfc="BBA830831LJ2", curp="")
        assert r["estado"] == "positiva"
        assert r["puede_contratar_con_gobierno"] is True
        assert r["pdf_base64"].startswith("JVBERi0")

    def test_html_negativa(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        resp = MagicMock()
        resp.headers = {"content-type": "text/html; charset=utf-8"}
        resp.text = FIXTURE_HTML_NEGATIVA
        r = c._parsear_respuesta(resp, rfc="XYZ000000XX1", curp="")
        assert r["estado"] == "negativa"
        assert r["puede_contratar_con_gobierno"] is False

    def test_content_type_inesperado_devuelve_error(self):
        from mp_sat_opinion_32d.client import SatOpinion32DClient
        c = SatOpinion32DClient()
        resp = MagicMock()
        resp.headers = {"content-type": "text/plain"}
        resp.text = "wat"
        r = c._parsear_respuesta(resp, rfc="X", curp="")
        assert r["estado"] == "error"
