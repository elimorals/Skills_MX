"""e.firma para tests, sin credenciales en el repo.

- `generada()`: .cer DER + .key PKCS#8 cifrado autofirmados, creados al vuelo (una vez por sesión).
- `eku()`: la e.firma de prueba EKU9003173C9 del SAT, solo si `SAT_EFIRMA_PRUEBA_DIR` apunta a una
  carpeta fuera del repo con `EKU9003173C9.cer`, `.key` y `-password.txt` (p.ej. de phpcfdi). La usan
  los tests que comparan byte a byte contra requests de phpcfdi; sin ella se saltan.
"""
from __future__ import annotations

import os
import secrets
import tempfile
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

RFC = "EKU9003173C9"


class Efirma(NamedTuple):
    cer: Path
    key: Path
    password: str


@lru_cache(maxsize=1)
def generada() -> Efirma:
    llave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ahora = datetime.now(timezone.utc)
    nombre = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "PRUEBA PLUGINS MX"),
        x509.NameAttribute(x509.ObjectIdentifier("2.5.4.45"), RFC),
    ])
    cert = (
        x509.CertificateBuilder().subject_name(nombre).issuer_name(nombre)
        .public_key(llave.public_key()).serial_number(x509.random_serial_number())
        .not_valid_before(ahora - timedelta(days=1)).not_valid_after(ahora + timedelta(days=365))
        .sign(llave, hashes.SHA256())
    )
    password = secrets.token_urlsafe(12)
    d = Path(tempfile.mkdtemp(prefix="efirma-prueba-"))
    (d / "prueba.cer").write_bytes(cert.public_bytes(serialization.Encoding.DER))
    (d / "prueba.key").write_bytes(llave.private_bytes(
        serialization.Encoding.DER, serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode()),
    ))
    return Efirma(d / "prueba.cer", d / "prueba.key", password)


def eku() -> Efirma:
    d = os.environ.get("SAT_EFIRMA_PRUEBA_DIR", "").strip()
    if not d or not (Path(d) / f"{RFC}.cer").exists():
        pytest.skip("requiere SAT_EFIRMA_PRUEBA_DIR con la e.firma de prueba EKU9003173C9 (fuera del repo)")
    p = Path(d)
    return Efirma(p / f"{RFC}.cer", p / f"{RFC}.key", (p / f"{RFC}-password.txt").read_text().strip())
