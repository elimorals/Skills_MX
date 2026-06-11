"""End-to-end tests of the FastMCP tool surface for mp_facturama_extendido."""

from __future__ import annotations

import copy

import pytest

from mp_facturama_extendido.server import (
    BuscarCfdisInput,
    CancelarCfdiInput,
    MotivoCancelacion,
    TimbrarCfdiInput,
    UuidInput,
    ValidarPayloadInput,
    facturama_buscar_cfdis,
    facturama_cancelar_cfdi,
    facturama_consultar_estatus,
    facturama_descargar_pdf,
    facturama_descargar_xml,
    facturama_listar_catalogos,
    facturama_timbrar_cfdi,
    facturama_validar_payload_local,
)


# ---------- facturama_validar_payload_local ----------


async def test_validar_payload_valid_returns_is_valid_true(valid_payload: dict) -> None:
    out = await facturama_validar_payload_local(ValidarPayloadInput(payload=valid_payload))
    assert out["is_valid"] is True
    assert out["errors_count"] == 0


async def test_validar_payload_with_errors(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["emisor"]["rfc"]
    payload["comprobante"]["metodo_pago"] = "PUE"
    payload["comprobante"]["forma_pago"] = "99"
    out = await facturama_validar_payload_local(ValidarPayloadInput(payload=payload))
    assert out["is_valid"] is False
    assert out["errors_count"] >= 2


# ---------- facturama_timbrar_cfdi ----------


async def test_timbrar_valid_payload_succeeds(valid_payload: dict) -> None:
    out = await facturama_timbrar_cfdi(TimbrarCfdiInput(payload=valid_payload))
    assert out["ok"] is True
    assert "uuid" in out
    assert out["simulated"] is True


async def test_timbrar_invalid_payload_blocks_before_pac(valid_payload: dict) -> None:
    """Validación local debe bloquear y NO llamar al PAC."""
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["metodo_pago"] = "PUE"
    payload["comprobante"]["forma_pago"] = "99"
    out = await facturama_timbrar_cfdi(TimbrarCfdiInput(payload=payload))
    assert out["ok"] is False
    assert out["validacion_local_failed"] is True
    assert any(e["code"] == "metodo_forma_inconsistente_pue_99" for e in out["errors"])
    # No UUID — porque no se llamó al PAC
    assert "uuid" not in out


async def test_timbrar_with_skip_validation_bypasses_check(valid_payload: dict) -> None:
    """skip_local_validation=True permite payloads inválidos pasen (peligroso)."""
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["metodo_pago"] = "PUE"
    payload["comprobante"]["forma_pago"] = "99"
    out = await facturama_timbrar_cfdi(
        TimbrarCfdiInput(payload=payload, skip_local_validation=True)
    )
    # Mock mode doesn't check semantics, so it would succeed
    assert out["ok"] is True
    assert "uuid" in out


# ---------- facturama_cancelar_cfdi ----------


async def test_cancelar_valid() -> None:
    out = await facturama_cancelar_cfdi(
        CancelarCfdiInput(
            uuid="abc12345-6789-4567-89ab-cdef01234567",
            motivo=MotivoCancelacion.ERROR_SIN_RELACION,
        )
    )
    assert out["ok"] is True
    assert out["uuid"] == "abc12345-6789-4567-89ab-cdef01234567"


async def test_cancelar_motivo_01_without_folio_fails() -> None:
    out = await facturama_cancelar_cfdi(
        CancelarCfdiInput(
            uuid="abc12345-6789-4567-89ab-cdef01234567",
            motivo=MotivoCancelacion.ERROR_CON_RELACION,
        )
    )
    assert out["ok"] is False
    assert out["validacion_local_failed"] is True


async def test_cancelar_motivo_01_with_folio_ok() -> None:
    out = await facturama_cancelar_cfdi(
        CancelarCfdiInput(
            uuid="abc12345-6789-4567-89ab-cdef01234567",
            motivo=MotivoCancelacion.ERROR_CON_RELACION,
            folio_sustituto="def67890-1234-4567-89ab-cdef01234567",
        )
    )
    assert out["ok"] is True


async def test_cancelar_invalid_uuid_format_rejected_by_pydantic() -> None:
    with pytest.raises(Exception):
        CancelarCfdiInput(uuid="not-a-uuid", motivo=MotivoCancelacion.ERROR_SIN_RELACION)


# ---------- facturama_consultar_estatus ----------


async def test_consultar_estatus_returns_vigente_in_mock() -> None:
    out = await facturama_consultar_estatus(
        UuidInput(uuid="abc12345-6789-4567-89ab-cdef01234567")
    )
    assert out["estatus"] == "Vigente"
    assert out["simulated"] is True


# ---------- facturama_descargar_xml / pdf ----------


async def test_descargar_xml_returns_synthetic() -> None:
    out = await facturama_descargar_xml(
        UuidInput(uuid="abc12345-6789-4567-89ab-cdef01234567")
    )
    assert "<?xml" in out["xml"]
    assert out["simulated"] is True


async def test_descargar_pdf_returns_base64() -> None:
    out = await facturama_descargar_pdf(
        UuidInput(uuid="abc12345-6789-4567-89ab-cdef01234567")
    )
    assert isinstance(out["pdf_base64"], str)
    assert out["simulated"] is True


# ---------- facturama_buscar_cfdis ----------


async def test_buscar_cfdis_with_filter() -> None:
    out = await facturama_buscar_cfdis(
        BuscarCfdisInput(rfc_receptor="IBM970131DRA", limit=10)
    )
    assert out["cfdis"] == []  # mock returns empty
    assert out["simulated"] is True


async def test_buscar_cfdis_with_invalid_rfc_rejected_by_pydantic() -> None:
    with pytest.raises(Exception):
        BuscarCfdisInput(rfc_receptor="not-rfc")


async def test_buscar_cfdis_with_invalid_fecha_rejected_by_pydantic() -> None:
    with pytest.raises(Exception):
        BuscarCfdisInput(fecha_desde="2026/03/15")


# ---------- facturama_listar_catalogos ----------


async def test_listar_catalogos_returns_all() -> None:
    out = await facturama_listar_catalogos()
    assert "uso_cfdi" in out
    assert "forma_pago" in out
    assert "metodo_pago" in out
    assert "regimen_fiscal" in out
    assert "exportacion" in out
    assert "motivos_cancelacion" in out
    assert "tipo_comprobante" in out

    # Common keys present
    assert "G03" in out["uso_cfdi"]
    assert "03" in out["forma_pago"]
    assert "PUE" in out["metodo_pago"]
    assert "612" in out["regimen_fiscal"]


async def test_listar_catalogos_includes_vigencia_warning() -> None:
    out = await facturama_listar_catalogos()
    assert "advertencia_vigencia" in out
    assert "SAT" in out["advertencia_vigencia"]
