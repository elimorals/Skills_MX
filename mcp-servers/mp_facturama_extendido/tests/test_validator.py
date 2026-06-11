"""Tests for the local CFDI 4.0 validator.

Covers:
- happy path with valid payload
- each individual validation rule
- error vs warning severity
- composability (multiple errors collected at once)
"""

from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone

import pytest

from mp_facturama_extendido.validator import (
    Issue,
    validate_cancelacion,
    validate_cfdi_payload,
)


# ---------- happy path ----------


def test_valid_payload_passes(valid_payload: dict) -> None:
    report = validate_cfdi_payload(valid_payload)
    assert report.is_valid, f"Errors: {[e.message for e in report.errors]}"
    assert len(report.errors) == 0


# ---------- emisor errors ----------


def test_missing_emisor_rfc(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["emisor"]["rfc"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "emisor_rfc_faltante" for e in report.errors)


def test_invalid_emisor_rfc_format(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["emisor"]["rfc"] = "INVALID-RFC"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "emisor_rfc_invalido" for e in report.errors)


def test_missing_emisor_regimen(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["emisor"]["regimen_fiscal"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "emisor_regimen_faltante" for e in report.errors)


def test_invalid_emisor_regimen(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["emisor"]["regimen_fiscal"] = "999"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "emisor_regimen_invalido" for e in report.errors)


def test_missing_emisor_cp(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["emisor"]["cp_lugar_expedicion"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "emisor_cp_faltante" for e in report.errors)


def test_invalid_emisor_cp(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["emisor"]["cp_lugar_expedicion"] = "1234"  # 4 digits, not 5
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "emisor_cp_invalido" for e in report.errors)


# ---------- receptor errors ----------


def test_missing_receptor_cp_is_error(valid_payload: dict) -> None:
    """CP del receptor es obligatorio en CFDI 4.0 (novedad vs 3.3)."""
    payload = copy.deepcopy(valid_payload)
    del payload["receptor"]["cp_domicilio"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "receptor_cp_faltante" for e in report.errors)


def test_missing_receptor_regimen(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["receptor"]["regimen_fiscal"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "receptor_regimen_faltante" for e in report.errors)


def test_missing_uso_cfdi(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["receptor"]["uso_cfdi"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "uso_cfdi_faltante" for e in report.errors)


def test_invalid_uso_cfdi(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["receptor"]["uso_cfdi"] = "ZZ99"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "uso_cfdi_invalido" for e in report.errors)


# ---------- RFC genérico rules ----------


def test_rfc_generico_nacional_with_non_s01_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["receptor"]["rfc"] = "XAXX010101000"
    payload["receptor"]["uso_cfdi"] = "G03"
    report = validate_cfdi_payload(payload)
    assert any(e.code == "rfc_generico_requiere_s01" for e in report.errors)


def test_rfc_generico_nacional_with_s01_ok(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["receptor"]["rfc"] = "XAXX010101000"
    payload["receptor"]["uso_cfdi"] = "S01"
    payload["receptor"]["regimen_fiscal"] = "616"  # Sin obligaciones
    report = validate_cfdi_payload(payload)
    # No debe haber error específico de RFC genérico
    assert not any(e.code == "rfc_generico_requiere_s01" for e in report.errors)


def test_rfc_extranjero_requires_residencia_fiscal(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["receptor"]["rfc"] = "XEXX010101000"
    payload["receptor"]["uso_cfdi"] = "S01"
    # Sin residencia_fiscal
    report = validate_cfdi_payload(payload)
    assert any(e.code == "extranjero_falta_residencia_fiscal" for e in report.errors)


def test_rfc_extranjero_with_residencia_ok(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["receptor"]["rfc"] = "XEXX010101000"
    payload["receptor"]["uso_cfdi"] = "S01"
    payload["receptor"]["residencia_fiscal"] = "USA"
    payload["receptor"]["num_reg_id_trib"] = "12-3456789"
    report = validate_cfdi_payload(payload)
    assert not any(e.code == "extranjero_falta_residencia_fiscal" for e in report.errors)


# ---------- comprobante ----------


def test_metodo_pue_with_forma_99_fails(valid_payload: dict) -> None:
    """El bug más común: PUE+99 que el SAT rechaza."""
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["metodo_pago"] = "PUE"
    payload["comprobante"]["forma_pago"] = "99"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "metodo_forma_inconsistente_pue_99" for e in report.errors)


def test_metodo_ppd_with_specific_forma_fails(valid_payload: dict) -> None:
    """PPD requiere forma=99."""
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["metodo_pago"] = "PPD"
    payload["comprobante"]["forma_pago"] = "03"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "metodo_forma_inconsistente_ppd_no_99" for e in report.errors)


def test_metodo_ppd_with_99_ok(valid_payload: dict) -> None:
    """PPD+99 es la combinación válida."""
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["metodo_pago"] = "PPD"
    payload["comprobante"]["forma_pago"] = "99"
    report = validate_cfdi_payload(payload)
    assert not any(
        e.code.startswith("metodo_forma_inconsistente") for e in report.errors
    )


def test_missing_exportacion_is_error(valid_payload: dict) -> None:
    """Exportacion es obligatorio en CFDI 4.0."""
    payload = copy.deepcopy(valid_payload)
    del payload["comprobante"]["exportacion"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "exportacion_faltante" for e in report.errors)


def test_invalid_tipo_comprobante(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["tipo_comprobante"] = "X"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "tipo_comprobante_invalido" for e in report.errors)


def test_foreign_currency_requires_tipo_cambio(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["moneda"] = "USD"
    # Sin tipo_cambio
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "tipo_cambio_requerido" for e in report.errors)


def test_foreign_currency_with_tipo_cambio_ok(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["moneda"] = "USD"
    payload["comprobante"]["tipo_cambio"] = 18.5
    report = validate_cfdi_payload(payload)
    assert not any(e.code == "tipo_cambio_requerido" for e in report.errors)


def test_foreign_currency_with_zero_tc_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["moneda"] = "USD"
    payload["comprobante"]["tipo_cambio"] = 0
    report = validate_cfdi_payload(payload)
    assert any(e.code == "tipo_cambio_requerido" for e in report.errors)


# ---------- fechas ----------


def test_future_date_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    future = datetime.now(timezone(timedelta(hours=-6))) + timedelta(hours=1)
    payload["comprobante"]["fecha"] = future.replace(microsecond=0).isoformat()
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "fecha_futura" for e in report.errors)


def test_old_date_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    old = datetime.now(timezone(timedelta(hours=-6))) - timedelta(days=5)
    payload["comprobante"]["fecha"] = old.replace(microsecond=0).isoformat()
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "fecha_demasiado_antigua" for e in report.errors)


def test_malformed_date_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["fecha"] = "ayer"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "fecha_formato_invalido" for e in report.errors)


# ---------- conceptos ----------


def test_empty_conceptos_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["conceptos"] = []
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "conceptos_vacios" for e in report.errors)


def test_concepto_missing_objeto_imp_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["conceptos"][0]["objeto_imp"]
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "concepto_objeto_imp_faltante" for e in report.errors)


def test_concepto_negative_importe_fails(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["conceptos"][0]["importe"] = -10
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "concepto_importe_negativo" for e in report.errors)


def test_concepto_importe_no_cuadra(valid_payload: dict) -> None:
    """importe ≠ cantidad × valor_unitario."""
    payload = copy.deepcopy(valid_payload)
    payload["conceptos"][0]["cantidad"] = 2
    payload["conceptos"][0]["valor_unitario"] = 100
    payload["conceptos"][0]["importe"] = 999  # debería ser 200
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "concepto_importe_no_cuadra" for e in report.errors)


def test_concepto_clave_prod_serv_non_8_digits_warns(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["conceptos"][0]["clave_prod_serv"] = "123"  # too short
    report = validate_cfdi_payload(payload)
    # Es warning, no error
    assert any(w.code == "concepto_clave_prod_serv_formato" for w in report.warnings)


# ---------- totales ----------


def test_subtotal_mismatch(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["subtotal"] = 9999  # but concept totals to 10000
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "subtotal_no_cuadra" for e in report.errors)


def test_total_mismatch(valid_payload: dict) -> None:
    """Total declarado ≠ subtotal + trasladados − retenidos."""
    payload = copy.deepcopy(valid_payload)
    payload["total"] = 11111  # off
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "total_no_cuadra" for e in report.errors)


def test_small_rounding_tolerance(valid_payload: dict) -> None:
    """Diferencias <= 0.01 deben tolerarse."""
    payload = copy.deepcopy(valid_payload)
    payload["total"] = 9533.34  # 1 cent off
    report = validate_cfdi_payload(payload)
    # Should NOT fail just for 1 cent
    assert not any(e.code == "total_no_cuadra" for e in report.errors)


# ---------- UsoCFDI × régimen ----------


def test_d01_to_pm_receptor_fails(valid_payload: dict) -> None:
    """D01 (honorarios médicos) solo aplica a PF; receptor PM debe fallar."""
    payload = copy.deepcopy(valid_payload)
    payload["receptor"]["uso_cfdi"] = "D01"  # Solo PF
    payload["receptor"]["regimen_fiscal"] = "601"  # PM
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "uso_cfdi_incompatible_persona" for e in report.errors)


def test_d01_to_pf_receptor_ok(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["receptor"]["uso_cfdi"] = "D01"
    payload["receptor"]["regimen_fiscal"] = "612"  # PFAE
    payload["receptor"]["rfc"] = "MAJG800101XYZ"  # PF (13 chars)
    report = validate_cfdi_payload(payload)
    assert not any(e.code == "uso_cfdi_incompatible_persona" for e in report.errors)


# ---------- UsoCFDI obligatorio por tipo ----------


def test_tipo_p_requires_cp01(valid_payload: dict) -> None:
    """CFDI tipo P (Pago) requiere UsoCFDI = CP01."""
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["tipo_comprobante"] = "P"
    payload["receptor"]["uso_cfdi"] = "G03"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    assert any(e.code == "uso_cfdi_obligatorio_no_cumplido" for e in report.errors)


def test_tipo_n_requires_cn01(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["tipo_comprobante"] = "N"
    payload["receptor"]["uso_cfdi"] = "G03"
    report = validate_cfdi_payload(payload)
    assert any(e.code == "uso_cfdi_obligatorio_no_cumplido" for e in report.errors)


# ---------- patrón anticipo / PPD → REP ----------


def test_ppd_warns_about_rep(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    payload["comprobante"]["metodo_pago"] = "PPD"
    payload["comprobante"]["forma_pago"] = "99"
    report = validate_cfdi_payload(payload)
    assert any(w.code == "ppd_requiere_rep_posterior" for w in report.warnings)


# ---------- composability: multiple errors collected ----------


def test_collects_multiple_errors(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["emisor"]["rfc"]
    del payload["receptor"]["cp_domicilio"]
    payload["comprobante"]["metodo_pago"] = "PUE"
    payload["comprobante"]["forma_pago"] = "99"
    report = validate_cfdi_payload(payload)
    assert not report.is_valid
    codes = {e.code for e in report.errors}
    assert "emisor_rfc_faltante" in codes
    assert "receptor_cp_faltante" in codes
    assert "metodo_forma_inconsistente_pue_99" in codes


# ---------- validate_cancelacion ----------


def test_cancelacion_valid() -> None:
    report = validate_cancelacion(
        uuid="abc12345-6789-4567-89ab-cdef01234567",
        motivo="02",
        folio_sustituto=None,
    )
    assert report.is_valid


def test_cancelacion_motivo_01_requires_folio_sustituto() -> None:
    report = validate_cancelacion(
        uuid="abc12345-6789-4567-89ab-cdef01234567",
        motivo="01",
        folio_sustituto=None,
    )
    assert not report.is_valid
    assert any(e.code == "motivo_01_requiere_folio_sustituto" for e in report.errors)


def test_cancelacion_motivo_01_with_folio_ok() -> None:
    report = validate_cancelacion(
        uuid="abc12345-6789-4567-89ab-cdef01234567",
        motivo="01",
        folio_sustituto="def67890-1234-4567-89ab-cdef01234567",
    )
    assert report.is_valid


def test_cancelacion_invalid_motivo() -> None:
    report = validate_cancelacion(
        uuid="abc12345-6789-4567-89ab-cdef01234567",
        motivo="99",
        folio_sustituto=None,
    )
    assert not report.is_valid
    assert any(e.code == "motivo_invalido" for e in report.errors)


def test_cancelacion_invalid_uuid() -> None:
    report = validate_cancelacion(
        uuid="not-a-uuid", motivo="02", folio_sustituto=None
    )
    assert not report.is_valid
    assert any(e.code == "uuid_invalido" for e in report.errors)


def test_cancelacion_folio_sustituto_warning_when_not_motivo_01() -> None:
    report = validate_cancelacion(
        uuid="abc12345-6789-4567-89ab-cdef01234567",
        motivo="02",
        folio_sustituto="def67890-1234-4567-89ab-cdef01234567",
    )
    assert report.is_valid  # warning, not error
    assert any(w.code == "folio_sustituto_no_aplica" for w in report.warnings)


# ---------- report serialization ----------


def test_report_to_dict_serializable(valid_payload: dict) -> None:
    payload = copy.deepcopy(valid_payload)
    del payload["emisor"]["rfc"]
    report = validate_cfdi_payload(payload)
    out = report.to_dict()
    assert out["is_valid"] is False
    assert out["errors_count"] >= 1
    assert isinstance(out["errors"], list)
    assert all("severity" in e and "code" in e and "message" in e for e in out["errors"])
