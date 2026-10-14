"""Tests mp_ine_verificacion — formatos, regla de vigencia y handoff (reCAPTCHA)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

from mp_ine_verificacion.client import INEVerificacionClient  # noqa: E402
from shared.errors import ValidationError  # noqa: E402

AUT = "autorizacion-firmada-" + "0001"  # referencia de prueba, no es credencial


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "0")
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_verificar_modelo_g_es_handoff():
    r = INEVerificacionClient().verificar_datos("G", AUT, cic="012345678", id_ciudadano="000123456")
    assert r["requiere_humano"] is True
    assert r["en_lista_nominal"] is None
    assert r["campos_a_capturar"] == ["cic", "id_ciudadano"]


def test_cic_de_13_digitos_rechazado():
    with pytest.raises(ValidationError):
        INEVerificacionClient().verificar_datos("E", AUT, cic="1234567890123", id_ciudadano="000123456")


def test_modelo_c_pide_clave_elector():
    c = INEVerificacionClient()
    r = c.verificar_datos("C", AUT, clave_elector="GOMZJN80010109H400", numero_emision="03",
                          ocr="1234567890123")
    assert r["campos_a_capturar"] == ["clave_elector", "numero_emision", "ocr"]
    with pytest.raises(ValidationError):
        c.verificar_datos("C", AUT, cic="012345678")


def test_sin_autorizacion_falla():
    with pytest.raises(ValidationError):
        INEVerificacionClient().verificar_datos("G", "", cic="012345678", id_ciudadano="000123456")


def test_vigencia_regla_10_anios():
    c = INEVerificacionClient()
    assert c.consultar_vigencia("G", 2020)["vigente_por_regla"] is True
    viejo = c.consultar_vigencia("E", 2014)
    assert viejo["vence_fin_de_anio"] == 2024
    assert viejo["vigente_por_regla"] is False
    assert c.consultar_vigencia("D", 2025)["vigente_por_regla"] is False  # modelo no vigente


def test_qr_no_se_afirma():
    r = INEVerificacionClient().verificar_qr("INE.MX.QR." + "x" * 40)
    assert r["autentica"] is None


def test_modelos_publicados():
    r = INEVerificacionClient().listar_modelos_credencial()
    vigentes = [m["clave"] for m in r["modelos"] if m["vigente_segun_ine"]]
    assert vigentes == ["E", "F", "G", "H", "I", "J"]


def test_autorizacion_template():
    r = INEVerificacionClient().generar_autorizacion("GOMJ800101HDFRNN09", "Alta de cliente en fintech")
    assert "AUTORIZO" in r["texto_autorizacion"]
    assert "simulated" not in r


def test_mock_solo_con_flag(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = INEVerificacionClient().verificar_datos("G", AUT, cic="012345678", id_ciudadano="000123456")
    assert r["simulated"] is True
