"""Tests mp_ine_verificacion."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

AUTH = "auth-token-" + ("x" * 16)


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_verificar_sin_autorizacion_lanza():
    from mp_ine_verificacion.client import INEVerificacionClient
    from shared.errors import ValidationError
    c = INEVerificacionClient()
    with pytest.raises(ValidationError):
        c.verificar_datos(cic="1234567890123", clave_elector="ABCDEF12345678H123",
                           anio_emision=2020, autorizacion_token="")


def test_verificar_cic_invalido():
    from mp_ine_verificacion.client import INEVerificacionClient
    from shared.errors import ValidationError
    c = INEVerificacionClient()
    with pytest.raises(ValidationError):
        c.verificar_datos(cic="123", clave_elector="ABCDEF12345678H123",
                           anio_emision=2020, autorizacion_token=AUTH)


def test_verificar_clave_elector_invalida():
    from mp_ine_verificacion.client import INEVerificacionClient
    from shared.errors import ValidationError
    c = INEVerificacionClient()
    with pytest.raises(ValidationError):
        c.verificar_datos(cic="1234567890127", clave_elector="malo",
                           anio_emision=2020, autorizacion_token=AUTH)


def test_verificar_autentica_alta_similitud():
    from mp_ine_verificacion.client import INEVerificacionClient
    c = INEVerificacionClient()
    r = c.verificar_datos(cic="1234567890127", clave_elector="ABCDEF12345678H123",
                           anio_emision=2024, autorizacion_token=AUTH)
    assert r["autentica"] is True
    assert r["similitud_huellas_pct"] >= 90.0
    assert "F" in r["modelo_credencial"]


def test_verificar_qr_invalido():
    from mp_ine_verificacion.client import INEVerificacionClient
    c = INEVerificacionClient()
    r = c.verificar_qr(qr_payload="x" * 64)
    assert r["autentica"] is False


def test_verificar_qr_valido():
    from mp_ine_verificacion.client import INEVerificacionClient
    c = INEVerificacionClient()
    r = c.verificar_qr(qr_payload="INE.MX.QR.abcd" + "x" * 64)
    assert r["autentica"] is True
    assert r["datos_extraidos"] is not None


def test_consultar_vigencia_ok():
    from mp_ine_verificacion.client import INEVerificacionClient
    c = INEVerificacionClient()
    r = c.consultar_vigencia(cic="1234567890121", autorizacion_token=AUTH)
    assert r["vigente"] in (True, False)


def test_generar_autorizacion_ok():
    from mp_ine_verificacion.client import INEVerificacionClient
    c = INEVerificacionClient()
    r = c.generar_autorizacion(curp="HEGJ900101HDFRRN09",
                                proposito="Onboarding KYC en plataforma fintech")
    assert len(r["token_referencia"]) >= 8
    assert "AUTORIZO" in r["texto_autorizacion"]


def test_generar_autorizacion_proposito_corto():
    from mp_ine_verificacion.client import INEVerificacionClient
    from shared.errors import ValidationError
    c = INEVerificacionClient()
    with pytest.raises(ValidationError):
        c.generar_autorizacion(curp="HEGJ900101HDFRRN09", proposito="x")


def test_listar_modelos_5_modelos():
    from mp_ine_verificacion.client import INEVerificacionClient
    c = INEVerificacionClient()
    r = c.listar_modelos_credencial()
    assert len(r["modelos"]) == 5
    assert r["modelo_actual_vigente"].startswith("F")
