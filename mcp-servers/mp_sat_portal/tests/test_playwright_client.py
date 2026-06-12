"""Tests del SatPlaywrightClient (esqueleto path real)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

crypto = pytest.importorskip("cryptography")

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mp_sat_portal.efirma_loader import EfirmaLoader
from mp_sat_portal.playwright_client import (
    EfirmaVencidaError,
    SatPlaywrightClient,
    detector_breakage,
)


def _gen_efirma(tmp_path: Path, *, expired: bool = False) -> EfirmaLoader:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    not_before = now - timedelta(days=30)
    not_after = now - timedelta(days=10) if expired else now + timedelta(days=365)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "PRUEBA EKU9003173C9"),
            x509.NameAttribute(x509.ObjectIdentifier("2.5.4.45"), "EKU9003173C9"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .sign(key, hashes.SHA256())
    )

    cert_p = tmp_path / "x.cer"
    cert_p.write_bytes(cert.public_bytes(serialization.Encoding.DER))
    key_p = tmp_path / "x.key"
    key_p.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(b"pwd"),
        )
    )
    return EfirmaLoader(cert_path=cert_p, key_path=key_p, password="pwd")


def test_get_mode_mock_sin_credenciales(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
    client = SatPlaywrightClient(efirma=None)
    assert client.get_mode() == "mock"


def test_get_mode_blocked_con_credenciales_sin_optin(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    efirma = _gen_efirma(tmp_path)
    client = SatPlaywrightClient(efirma=efirma)
    assert client.get_mode() == "blocked"


def test_descargar_csf_modo_mock_retorna_simulated(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_PLAYWRIGHT_REAL", raising=False)
    client = SatPlaywrightClient(efirma=None)
    r = client.descargar_csf("ABC010101AA1")
    assert r["operation"] == "descargar_csf"
    assert r["data"]["rfc"] == "ABC010101AA1"
    assert r.get("simulated") is True


def test_descargar_buzon_modo_mock(tmp_path: Path):
    client = SatPlaywrightClient(efirma=None)
    r = client.descargar_buzon_tributario("ABC010101AA1")
    assert r["data"]["no_leidas"] == 0
    assert r.get("simulated") is True


def test_descargar_cfdi_masivo_modo_mock(tmp_path: Path):
    client = SatPlaywrightClient(efirma=None)
    r = client.descargar_cfdi_masivo("ABC010101AA1", 2025, 1, "emitidos")
    assert r["data"]["estado"] == "solicitada"
    assert r["data"]["solicitud_id"]


def test_verificar_efirma_local_si_loader_disponible(tmp_path: Path):
    efirma = _gen_efirma(tmp_path)
    client = SatPlaywrightClient(efirma=efirma)
    r = client.verificar_efirma_vigente("EKU9003173C9")
    # como tenemos loader, retorna data del .cer local sin marcar simulated
    assert r["data"]["rfc"] == "EKU9003173C9"
    assert r.get("simulated") is False


def test_precheck_efirma_vencida_lanza(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_PLAYWRIGHT_REAL", "1")
    # Aún sin playwright instalado get_mode() devolvería "blocked" no "real",
    # pero precheck_efirma() solo se llama desde _dispatch en modo "real".
    # Testeamos el método directamente.
    efirma = _gen_efirma(tmp_path, expired=True)
    client = SatPlaywrightClient(efirma=efirma)
    with pytest.raises(EfirmaVencidaError):
        client.precheck_efirma()


def test_from_env_sin_vars_devuelve_cliente_mock(monkeypatch):
    for v in ["SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]:
        monkeypatch.delenv(v, raising=False)
    client = SatPlaywrightClient.from_env()
    assert client.efirma is None
    assert client.get_mode() == "mock"


def test_detector_breakage_todos_presentes():
    html = "<html><div class='csf-rfc'>ABC010101AA1</div></html>"
    r = detector_breakage(["csf-rfc"], html)
    assert r["ok"] is True
    assert r["missing"] == []


def test_detector_breakage_uno_falta():
    html = "<html><div class='csf-rfc'>...</div></html>"
    r = detector_breakage(["csf-rfc", "csf-razon-social"], html)
    assert r["ok"] is False
    assert "csf-razon-social" in r["missing"]
    assert r["encontrados"] == 1


def test_descargar_csf_mock_no_loguea_rfc_en_claro(tmp_path: Path, monkeypatch):
    """El RFC NUNCA debe quedar en claro en la bitácora."""
    from shared.bitacora import Bitacora

    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    bitacora = Bitacora("sat_portal_pw")
    client = SatPlaywrightClient(efirma=None, bitacora=bitacora)
    client.descargar_csf("ABC010101AA1")
    entries = bitacora.tail(5)
    # asegurarse de que el RFC en claro no aparece en el log
    for entry in entries:
        params = entry.get("params", {})
        assert "ABC010101AA1" not in str(params)
        assert params.get("rfc_hash")  # sí debe haber hash
