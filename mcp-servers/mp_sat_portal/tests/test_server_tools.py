"""End-to-end tests para los tools FastMCP de mp_sat_portal."""

from __future__ import annotations

import pytest

from mp_sat_portal.server import (
    ActualizarObligacionesInput,
    CitaSatInput,
    DescargaMasivaInput,
    FolioInput,
    RfcInput,
    RfcOpcionalInput,
    UuidInput,
    VerificarCfdiInput,
    sat_actualizar_obligaciones,
    sat_agendar_cita,
    sat_consultar_69_incumplidos,
    sat_consultar_69b_efos,
    sat_consultar_padron,
    sat_descargar_acuse,
    sat_descargar_buzon_tributario,
    sat_descargar_cfdi_masivo,
    sat_descargar_csf,
    sat_listar_catalogos,
    sat_validar_uuid_estructura,
    sat_verificar_cfdi_uuid,
    sat_verificar_efirma_vigente,
)
from mp_sat_portal.tests.conftest import (
    DEMO_RFC_PF,
    DEMO_RFC_PM_CORTO,
    DEMO_UUID_VALIDO,
)


# ---------- tools públicos ----------


@pytest.mark.asyncio
async def test_consultar_padron_devuelve_simulated() -> None:
    r = await sat_consultar_padron(RfcInput(rfc=DEMO_RFC_PF))
    assert r["simulated"] is True
    assert r["rfc"] == DEMO_RFC_PF


@pytest.mark.asyncio
async def test_consultar_padron_normaliza_rfc() -> None:
    r = await sat_consultar_padron(RfcInput(rfc=DEMO_RFC_PF.lower()))
    assert r["rfc"] == DEMO_RFC_PF


@pytest.mark.asyncio
async def test_consultar_69b_sin_rfc(monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = await sat_consultar_69b_efos(RfcOpcionalInput())
    assert "registros" in r or "encontrado" in r


@pytest.mark.asyncio
async def test_consultar_69b_con_rfc_riesgo_alto(monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = await sat_consultar_69b_efos(RfcOpcionalInput(rfc="EFD850202002"))
    assert r["encontrado"] is True
    assert r["riesgo_alto"] is True  # DEFINITIVO


@pytest.mark.asyncio
async def test_consultar_69_incumplidos_con_rfc(monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = await sat_consultar_69_incumplidos(RfcOpcionalInput(rfc="INC910202002"))
    assert r["encontrado"] is True
    assert r["riesgo_alto"] is True  # DOMICILIO_FALSO


@pytest.mark.asyncio
async def test_verificar_cfdi_uuid_estructura_valida_modo_mock() -> None:
    r = await sat_verificar_cfdi_uuid(
        VerificarCfdiInput(
            uuid=DEMO_UUID_VALIDO,
            rfc_emisor=DEMO_RFC_PF,
            rfc_receptor=DEMO_RFC_PM_CORTO,
            total="1500.50",
        )
    )
    assert r["valido_estructuralmente"] is True
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_verificar_cfdi_uuid_invalido() -> None:
    r = await sat_verificar_cfdi_uuid(
        VerificarCfdiInput(
            uuid="malo",
            rfc_emisor=DEMO_RFC_PF,
            rfc_receptor=DEMO_RFC_PM_CORTO,
            total="100",
        )
    )
    assert r["valido_estructuralmente"] is False


# ---------- tool utilitario local ----------


@pytest.mark.asyncio
async def test_validar_uuid_estructura_ok() -> None:
    r = await sat_validar_uuid_estructura(UuidInput(uuid=DEMO_UUID_VALIDO))
    assert r["valido"] is True
    assert r["es_v4_random"] is True


@pytest.mark.asyncio
async def test_validar_uuid_estructura_mal() -> None:
    r = await sat_validar_uuid_estructura(UuidInput(uuid="no-es-uuid"))
    assert r["valido"] is False


# ---------- tools con auth ----------


@pytest.mark.asyncio
async def test_descargar_csf_simulado() -> None:
    r = await sat_descargar_csf(RfcInput(rfc=DEMO_RFC_PF))
    assert r["simulated"] is True
    assert "domicilio_fiscal" in r


@pytest.mark.asyncio
async def test_descargar_buzon_simulado() -> None:
    r = await sat_descargar_buzon_tributario(RfcInput(rfc=DEMO_RFC_PF))
    assert r["simulated"] is True
    assert isinstance(r["notificaciones"], list)


@pytest.mark.asyncio
async def test_descargar_cfdi_masivo_simulado() -> None:
    r = await sat_descargar_cfdi_masivo(
        DescargaMasivaInput(
            rfc=DEMO_RFC_PF, ejercicio=2026, mes=3, tipo="emitidos"
        )
    )
    assert r["simulated"] is True
    assert r["tipo"] == "emitidos"


@pytest.mark.asyncio
async def test_agendar_cita_simulado() -> None:
    r = await sat_agendar_cita(
        CitaSatInput(rfc=DEMO_RFC_PF, tipo_tramite="firma electronica")
    )
    assert r["simulated"] is True
    assert len(r["citas_disponibles"]) >= 1


@pytest.mark.asyncio
async def test_verificar_efirma_simulado() -> None:
    r = await sat_verificar_efirma_vigente(RfcInput(rfc=DEMO_RFC_PF))
    assert r["simulated"] is True
    assert "fecha_vencimiento" in r


@pytest.mark.asyncio
async def test_descargar_acuse_simulado() -> None:
    r = await sat_descargar_acuse(FolioInput(folio="ACU-2026-001"))
    assert r["simulated"] is True


# ---------- tool de escritura ----------


@pytest.mark.asyncio
async def test_actualizar_obligaciones_siempre_simulado() -> None:
    r = await sat_actualizar_obligaciones(
        ActualizarObligacionesInput(rfc=DEMO_RFC_PF, accion="alta_obligacion")
    )
    assert r["simulated"] is True
    assert "advertencia" in str(r).lower()


# ---------- catálogos ----------


@pytest.mark.asyncio
async def test_listar_catalogos() -> None:
    r = await sat_listar_catalogos()
    assert "status_rfc" in r
    assert "estado_69b" in r
    assert "tipos_obligacion" in r
    assert "ACTIVO" in r["status_rfc"]
