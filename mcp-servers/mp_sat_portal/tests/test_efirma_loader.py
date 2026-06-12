"""Tests del e.firma loader.

Genera certificados self-signed de prueba para no requerir la e.firma real.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Skip todos si cryptography no está instalado
crypto = pytest.importorskip("cryptography")

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mp_sat_portal.efirma_loader import EfirmaLoader, EfirmaMetadata
from shared.errors import ConfigError, ValidationError


def _gen_efirma_test(
    tmp_path: Path,
    *,
    rfc: str = "EKU9003173C9",
    nombre: str = "USUARIO PRUEBAS",
    valid_days_before: int = 30,
    valid_days_after: int = 365,
    password: str = "test1234",
    der: bool = True,
) -> tuple[Path, Path, str]:
    """Genera .cer + .key autofirmados para tests."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.now(timezone.utc)
    subject_attrs = [
        x509.NameAttribute(NameOID.COMMON_NAME, f"{nombre} {rfc}"),
        # OID 2.5.4.45 = uniqueIdentifier (SAT lo usa para RFC)
        x509.NameAttribute(x509.ObjectIdentifier("2.5.4.45"), rfc),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Servicio de Administración Tributaria"),
    ]
    subject = x509.Name(subject_attrs)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)  # self-signed para test
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=valid_days_before))
        .not_valid_after(now + timedelta(days=valid_days_after))
        .sign(key, hashes.SHA256())
    )

    cert_path = tmp_path / "test.cer"
    cert_path.write_bytes(
        cert.public_bytes(serialization.Encoding.DER if der else serialization.Encoding.PEM)
    )

    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
    )
    key_path = tmp_path / "test.key"
    key_path.write_bytes(key_bytes)
    return cert_path, key_path, password


def test_loader_extracts_metadata_der(tmp_path: Path):
    cert_path, key_path, pwd = _gen_efirma_test(tmp_path)
    loader = EfirmaLoader(cert_path=cert_path, key_path=key_path, password=pwd)
    meta = loader.metadata()
    assert isinstance(meta, EfirmaMetadata)
    assert meta.rfc == "EKU9003173C9"
    assert meta.is_valid_now is True
    assert meta.days_until_expiry > 300
    assert "EKU9003173C9" in meta.nombre or "USUARIO PRUEBAS" in (meta.nombre or "")


def test_loader_extracts_metadata_pem(tmp_path: Path):
    cert_path, key_path, pwd = _gen_efirma_test(tmp_path, der=False)
    loader = EfirmaLoader(cert_path=cert_path, key_path=key_path, password=pwd)
    meta = loader.metadata()
    assert meta.rfc == "EKU9003173C9"


def test_loader_detects_expired(tmp_path: Path):
    cert_path, key_path, pwd = _gen_efirma_test(
        tmp_path, valid_days_before=365, valid_days_after=-10
    )
    loader = EfirmaLoader(cert_path=cert_path, key_path=key_path, password=pwd)
    meta = loader.metadata()
    assert meta.is_valid_now is False
    assert meta.days_until_expiry < 0


def test_loader_validate_key_pair_ok(tmp_path: Path):
    cert_path, key_path, pwd = _gen_efirma_test(tmp_path)
    loader = EfirmaLoader(cert_path=cert_path, key_path=key_path, password=pwd)
    assert loader.validate_key_pair() is True


def test_loader_wrong_password_raises(tmp_path: Path):
    cert_path, key_path, pwd = _gen_efirma_test(tmp_path)
    loader = EfirmaLoader(cert_path=cert_path, key_path=key_path, password="wrong")
    with pytest.raises(ValidationError):
        loader.validate_key_pair()


def test_loader_missing_cert_raises_config_error(tmp_path: Path):
    with pytest.raises(ConfigError):
        EfirmaLoader(
            cert_path=tmp_path / "no_existe.cer",
            key_path=tmp_path / "no_existe.key",
            password="x",
        )


def test_loader_from_env_missing_vars(monkeypatch):
    for v in ["SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]:
        monkeypatch.delenv(v, raising=False)
    with pytest.raises(ConfigError) as exc_info:
        EfirmaLoader.from_env()
    assert "SAT_EFIRMA" in str(exc_info.value)


def test_loader_from_env_ok(tmp_path: Path, monkeypatch):
    cert_path, key_path, pwd = _gen_efirma_test(tmp_path)
    monkeypatch.setenv("SAT_EFIRMA_CERT", str(cert_path))
    monkeypatch.setenv("SAT_EFIRMA_KEY", str(key_path))
    monkeypatch.setenv("SAT_EFIRMA_PASSWORD", pwd)
    loader = EfirmaLoader.from_env()
    meta = loader.metadata()
    assert meta.rfc == "EKU9003173C9"


def test_loader_metadata_to_dict_no_secrets(tmp_path: Path):
    cert_path, key_path, pwd = _gen_efirma_test(tmp_path)
    loader = EfirmaLoader(cert_path=cert_path, key_path=key_path, password=pwd)
    d = loader.metadata().to_dict()
    # asegurarse de que no haya rastro de password ni private key
    assert "password" not in d
    assert "private_key" not in d
    assert "key" not in str(d).lower() or "rfc" in str(d).lower()
