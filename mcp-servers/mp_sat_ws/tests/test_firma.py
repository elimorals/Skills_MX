"""Firma XMLDSig del WS Descarga Masiva con la e.firma de PRUEBA del SAT.

Sin credenciales en el repo: la mayoría de los tests usan una e.firma autofirmada
generada al vuelo (tests/efirma_prueba.py). Los que comparan contra requests de
phpcfdi necesitan la e.firma de prueba EKU9003173C9 vía SAT_EFIRMA_PRUEBA_DIR.

La firma RSA PKCS#1 v1.5 es determinística, así que comparar DigestValue y
SignatureValue contra los requests que generó phpcfdi (ya aceptados por el SAT
en su integración) valida el port byte a byte. Además se verifica la firma con
la llave pública del certificado.
"""
from __future__ import annotations

import base64
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import pytest

pytest.importorskip("cryptography")

from cryptography import x509  # noqa: E402
from cryptography.hazmat.primitives import hashes  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import padding  # noqa: E402

from mp_sat_ws.client import NS_DS, Fiel, SatWsClient  # noqa: E402
from mp_sat_ws.tests.efirma_prueba import Efirma, eku, generada  # noqa: E402
from shared.errors import ConfigError  # noqa: E402

FIX = Path(__file__).parent / "fixtures"


def fiel_prueba(e: Efirma | None = None) -> Fiel:
    e = e or generada()
    return Fiel(e.cer.read_bytes(), e.key.read_bytes(), e.password)


def _valor(xml: str, tag: str) -> str:
    return re.search(rf"<{tag}>([^<]+)</{tag}>", xml).group(1)


def _verificar_firma(xml: str, e: Efirma | None = None) -> None:
    """Recalcula SignedInfo canónico y verifica SignatureValue con el .cer."""
    signed_info = re.search(r"<SignedInfo>.*?</SignedInfo>", xml).group(0)
    signed_info = signed_info.replace("<SignedInfo>", f'<SignedInfo xmlns="{NS_DS}">', 1)
    firma = base64.b64decode(_valor(xml, "SignatureValue"))
    cert = x509.load_der_x509_certificate((e or generada()).cer.read_bytes())
    cert.public_key().verify(firma, signed_info.encode(), padding.PKCS1v15(), hashes.SHA1())


def test_fiel_metadatos():
    f = fiel_prueba()
    assert f.rfc == "EKU9003173C9"


def test_fiel_metadatos_eku():
    f = fiel_prueba(eku())
    assert f.rfc == "EKU9003173C9"
    assert f.numero_serie == "292233162870206001759766198462772978647764840757"
    assert f.emisor.startswith("CN=AC UAT,O=SERVICIO DE ADMINISTRACION TRIBUTARIA")


def test_fiel_password_incorrecto():
    with pytest.raises(ConfigError):
        Fiel(
            generada().cer.read_bytes(),
            generada().key.read_bytes(),
            "no-es",
        )


def test_verifica_igual_a_phpcfdi():
    e = eku()
    esperado = (FIX / "phpcfdi-verifica-request.xml").read_text()
    xml = SatWsClient(fiel=fiel_prueba(e))._xml_firmado(
        "VerificaSolicitudDescarga", "solicitud",
        {"IdSolicitud": "3f30a4e1-af73-4085-8991-e4d97eef16bd", "RfcSolicitante": "EKU9003173C9"},
    )
    ET.fromstring(xml)  # bien formado
    for tag in ("DigestValue", "SignatureValue", "X509IssuerName", "X509SerialNumber", "X509Certificate"):
        assert _valor(xml, tag) == _valor(esperado, tag), tag
    _verificar_firma(xml, e)


def test_autentica_igual_a_phpcfdi():
    e = eku()
    esperado = (FIX / "phpcfdi-autentica-request.xml").read_text()
    creado = datetime(2019, 8, 1, 3, 38, 19, tzinfo=timezone.utc)
    expira = datetime(2019, 8, 1, 3, 43, 19, tzinfo=timezone.utc)
    xml = SatWsClient(fiel=fiel_prueba(e))._xml_autentica(
        creado, expira, "uuid-cf6c80fb-00ae-44c0-af56-54ec65decbaa-1"
    )
    ET.fromstring(xml)
    for tag in ("DigestValue", "SignatureValue"):
        assert _valor(xml, tag) == _valor(esperado, tag), tag
    _verificar_firma(xml, e)


def test_digest_es_del_nodo_firmado():
    """El DigestValue corresponde al nodo des:solicitud sin la firma."""
    xml = SatWsClient(fiel=fiel_prueba())._xml_firmado(
        "PeticionDescargaMasivaTercerosEntrada", "peticionDescarga",
        {"RfcSolicitante": "EKU9003173C9", "IdPaquete": "ABC_01"},
    )
    nodo = (
        '<des:PeticionDescargaMasivaTercerosEntrada xmlns:des="http://DescargaMasivaTerceros.sat.gob.mx">'
        '<des:peticionDescarga IdPaquete="ABC_01" RfcSolicitante="EKU9003173C9"></des:peticionDescarga>'
        "</des:PeticionDescargaMasivaTercerosEntrada>"
    )
    assert _valor(xml, "DigestValue") == base64.b64encode(hashlib.sha1(nodo.encode()).digest()).decode()
    _verificar_firma(xml)
