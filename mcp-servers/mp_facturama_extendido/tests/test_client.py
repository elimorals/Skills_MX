"""Tests for FacturamaClient — mock mode behavior + response parsing."""

from __future__ import annotations

import pytest

from mp_facturama_extendido.client import (
    FacturamaClient,
    _generate_uuid_v4_like,
    _hash_payload,
)
from shared.errors import ConfigError


# ---------- construction ----------


def test_client_defaults_to_mock_without_creds() -> None:
    c = FacturamaClient()
    assert c.is_mock is True


def test_explicit_user_password_enable_real_mode() -> None:
    c = FacturamaClient(user="u", password="p")
    assert c.is_mock is False


def test_env_creds_enable_real_mode(monkeypatch) -> None:
    monkeypatch.setenv("FACTURAMA_USER", "u")
    monkeypatch.setenv("FACTURAMA_PASSWORD", "p")
    c = FacturamaClient()
    assert c.is_mock is False


def test_api_key_treated_as_user(monkeypatch) -> None:
    monkeypatch.setenv("FACTURAMA_API_KEY", "abcd1234")
    monkeypatch.setenv("FACTURAMA_PASSWORD", "anything")
    c = FacturamaClient()
    assert c.is_mock is False


def test_plugins_mx_mock_forces_mock(monkeypatch) -> None:
    monkeypatch.setenv("FACTURAMA_USER", "u")
    monkeypatch.setenv("FACTURAMA_PASSWORD", "p")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    c = FacturamaClient()
    assert c.is_mock is True


def test_default_environment_is_sandbox() -> None:
    c = FacturamaClient()
    assert c.environment == "sandbox"
    assert "sandbox" in c.base_url.lower()


def test_production_environment(monkeypatch) -> None:
    monkeypatch.setenv("FACTURAMA_ENV", "production")
    c = FacturamaClient(user="u", password="p")
    assert c.environment == "production"
    assert "sandbox" not in c.base_url.lower()


# ---------- mock timbrado ----------


async def test_mock_timbrar_returns_valid_uuid(valid_payload: dict) -> None:
    c = FacturamaClient()
    response = await c.timbrar_cfdi(valid_payload)
    assert response["simulated"] is True
    uuid = response["uuid"]
    # UUID format 8-4-4-4-12 hex
    parts = uuid.split("-")
    assert len(parts) == 5
    assert [len(p) for p in parts] == [8, 4, 4, 4, 12]
    assert all(c in "0123456789abcdef" for p in parts for c in p)


async def test_mock_timbrar_includes_all_required_fields(valid_payload: dict) -> None:
    c = FacturamaClient()
    response = await c.timbrar_cfdi(valid_payload)
    for field in (
        "uuid",
        "fecha_timbrado",
        "sello_sat",
        "sello_emisor",
        "cadena_original_complemento",
        "simulated",
    ):
        assert field in response, f"Missing field: {field}"


async def test_mock_timbrar_sello_is_deterministic_for_same_payload(
    valid_payload: dict,
) -> None:
    c = FacturamaClient()
    r1 = await c.timbrar_cfdi(valid_payload)
    r2 = await c.timbrar_cfdi(valid_payload)
    # Sello sat = hash del payload → same input, same hash
    assert r1["sello_sat"] == r2["sello_sat"]
    # But UUIDs differ (each timbrado is a "new" CFDI)
    assert r1["uuid"] != r2["uuid"]


async def test_mock_timbrar_writes_bitacora(valid_payload: dict) -> None:
    c = FacturamaClient()
    await c.timbrar_cfdi(valid_payload)
    entries = c._bitacora.tail()
    assert any(e["tool"] == "timbrar_cfdi" and e["success"] for e in entries)


async def test_mock_timbrar_hashes_rfc_in_bitacora(valid_payload: dict) -> None:
    """Bitacora must NOT contain the raw RFC."""
    c = FacturamaClient()
    await c.timbrar_cfdi(valid_payload)
    entries = c._bitacora.tail()
    raw_rfc = valid_payload["emisor"]["rfc"]
    for e in entries:
        assert raw_rfc not in str(e), "Raw RFC leaked into bitacora"


# ---------- mock cancelación ----------


async def test_mock_cancelar_returns_plausible_response() -> None:
    c = FacturamaClient()
    response = await c.cancelar_cfdi(
        uuid="abc12345-6789-4567-89ab-cdef01234567",
        motivo="02",
    )
    assert response["simulated"] is True
    assert response["uuid"] == "abc12345-6789-4567-89ab-cdef01234567"
    assert response["motivo"] == "02"


async def test_mock_cancelar_with_folio_sustituto() -> None:
    c = FacturamaClient()
    response = await c.cancelar_cfdi(
        uuid="abc12345-6789-4567-89ab-cdef01234567",
        motivo="01",
        folio_sustituto="def67890-1234-4567-89ab-cdef01234567",
    )
    assert response["folio_sustituto"] == "def67890-1234-4567-89ab-cdef01234567"


# ---------- mock consulta estatus ----------


async def test_mock_consultar_estatus_returns_vigente() -> None:
    c = FacturamaClient()
    response = await c.consultar_estatus("abc12345-6789-4567-89ab-cdef01234567")
    assert response["simulated"] is True
    assert response["estatus"] == "Vigente"


async def test_consultar_estatus_uses_cache() -> None:
    c = FacturamaClient()
    uuid = "abc12345-6789-4567-89ab-cdef01234567"
    r1 = await c.consultar_estatus(uuid)

    # Drop mock mode without setting creds — cache must serve
    c._mock_mode = False
    c._user = None
    c._password = None
    r2 = await c.consultar_estatus(uuid)
    assert r1["uuid"] == r2["uuid"]
    assert r1["estatus"] == r2["estatus"]


# ---------- mock descargas ----------


async def test_mock_descargar_xml_returns_synthetic() -> None:
    c = FacturamaClient()
    response = await c.descargar_xml("abc12345-6789-4567-89ab-cdef01234567")
    assert response["simulated"] is True
    assert "<?xml" in response["xml"]
    assert response["size_bytes"] > 0


async def test_mock_descargar_pdf_returns_base64() -> None:
    c = FacturamaClient()
    response = await c.descargar_pdf("abc12345-6789-4567-89ab-cdef01234567")
    assert response["simulated"] is True
    assert isinstance(response["pdf_base64"], str)
    assert len(response["pdf_base64"]) > 0


# ---------- mock búsqueda ----------


async def test_mock_buscar_returns_empty_list() -> None:
    c = FacturamaClient()
    response = await c.buscar_cfdis(rfc_receptor="IBM970131DRA")
    assert response["simulated"] is True
    assert response["cfdis"] == []
    assert response["total"] == 0


# ---------- real mode requires creds ----------


async def test_real_mode_timbrar_without_creds_raises_config_error(valid_payload: dict) -> None:
    c = FacturamaClient(user="u", password="p")  # explicit creds → real mode
    # Now clear them to simulate misconfiguration
    c._user = None
    c._password = None
    with pytest.raises(ConfigError):
        await c.timbrar_cfdi(valid_payload)


# ---------- helpers ----------


def test_generate_uuid_v4_like_format() -> None:
    uuid = _generate_uuid_v4_like()
    parts = uuid.split("-")
    assert [len(p) for p in parts] == [8, 4, 4, 4, 12]


def test_hash_payload_deterministic() -> None:
    p1 = {"a": 1, "b": 2}
    p2 = {"b": 2, "a": 1}  # different key order
    assert _hash_payload(p1) == _hash_payload(p2)


def test_hash_payload_different_for_different_payloads() -> None:
    assert _hash_payload({"a": 1}) != _hash_payload({"a": 2})


# ---------- parse real response ----------


def test_parse_timbrado_response_extracts_uuid_from_tfd() -> None:
    body = {
        "Id": "abc12345-6789-4567-89ab-cdef01234567",
        "Date": "2026-03-15T10:30:00",
        "Complement": {
            "TimbreFiscalDigital": {
                "UUID": "abc12345-6789-4567-89ab-cdef01234567",
                "Date": "2026-03-15T10:30:00",
                "SatSeal": "FAKE_SEAL",
                "CfdiSeal": "FAKE_CFDI_SEAL",
                "OriginalString": "||1.1|...",
                "SatCertNumber": "30001000000400002495",
                "RfcProvCertif": "FAKE_PAC",
            }
        },
        "ContentEncoding": "base64xml",
    }
    parsed = FacturamaClient._parse_timbrado_response(body)
    assert parsed["uuid"] == "abc12345-6789-4567-89ab-cdef01234567"
    assert parsed["sello_sat"] == "FAKE_SEAL"
    assert parsed["sello_emisor"] == "FAKE_CFDI_SEAL"
    assert parsed["simulated"] is False
