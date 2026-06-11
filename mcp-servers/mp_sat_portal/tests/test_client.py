"""Tests para mp_sat_portal/client.py — modo mock + parseo HTML."""

from __future__ import annotations

import pytest

from mp_sat_portal.client import SatPortalClient, _parsear_html_verificacfdi
from mp_sat_portal.tests.conftest import DEMO_RFC_PF, DEMO_RFC_PM_CORTO, DEMO_UUID_VALIDO
from shared.errors import McpError


@pytest.fixture
def client() -> SatPortalClient:
    return SatPortalClient()


# ---------- tools públicos en modo mock ----------


def test_consultar_padron_mock_devuelve_status(client: SatPortalClient) -> None:
    r = client.consultar_padron(DEMO_RFC_PF)
    assert r["simulated"] is True
    assert r["rfc"] == DEMO_RFC_PF
    assert r["status"] == "ACTIVO"


def test_consultar_69b_mock_sin_rfc(client: SatPortalClient, monkeypatch) -> None:
    # Forzar mock por si la URL real respondiera en el entorno
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = client.consultar_69b_efos()
    assert r["simulated"] is True
    assert "registros" in r
    assert r["total_registros"] >= 1


def test_consultar_69b_mock_con_rfc_demo_encontrado(
    client: SatPortalClient, monkeypatch
) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    # RFC demo de la mock list
    r = client.consultar_69b_efos("EFD850101001")
    assert r["simulated"] is True
    assert r["encontrado"] is True
    assert r["registro"]["estado_69b"] == "PRESUNTO"


def test_consultar_69b_mock_rfc_no_demo(client: SatPortalClient, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = client.consultar_69b_efos("XYZ999999999")
    assert r["simulated"] is True
    assert r["encontrado"] is False


def test_consultar_69_incumplidos_mock(client: SatPortalClient, monkeypatch) -> None:
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    r = client.consultar_69_incumplidos()
    assert r["simulated"] is True
    assert r["total_registros"] >= 1


def test_verificar_cfdi_uuid_invalido_no_consulta_portal(
    client: SatPortalClient,
) -> None:
    r = client.verificar_cfdi_uuid(
        "no-es-uuid", DEMO_RFC_PF, DEMO_RFC_PM_CORTO, "100.00"
    )
    assert r["valido_estructuralmente"] is False
    assert r["simulated"] is False
    assert r["estado_cfdi"] is None


def test_verificar_cfdi_uuid_valido_modo_mock(client: SatPortalClient) -> None:
    r = client.verificar_cfdi_uuid(
        DEMO_UUID_VALIDO, DEMO_RFC_PF, DEMO_RFC_PM_CORTO, "1500.50"
    )
    assert r["valido_estructuralmente"] is True
    assert r["simulated"] is True
    assert r["estado_cfdi"] == "Vigente"


# ---------- tools con auth en modo mock ----------


def test_descargar_csf_mock(client: SatPortalClient) -> None:
    r = client.descargar_csf(DEMO_RFC_PF)
    assert r["simulated"] is True
    assert r["rfc"] == DEMO_RFC_PF
    assert "obligaciones_vigentes" in r


def test_descargar_buzon_mock(client: SatPortalClient) -> None:
    r = client.descargar_buzon_tributario(DEMO_RFC_PF)
    assert r["simulated"] is True
    assert "notificaciones" in r


def test_descargar_cfdi_masivo_mock(client: SatPortalClient) -> None:
    r = client.descargar_cfdi_masivo(DEMO_RFC_PF, 2026, 3, "emitidos")
    assert r["simulated"] is True
    assert r["ejercicio"] == 2026
    assert r["mes"] == 3
    assert r["tipo"] == "emitidos"
    assert "solicitud_id" in r


def test_agendar_cita_mock(client: SatPortalClient) -> None:
    r = client.agendar_cita_sat(DEMO_RFC_PF, "firma electronica")
    assert r["simulated"] is True
    assert len(r["citas_disponibles"]) >= 1


def test_verificar_efirma_mock(client: SatPortalClient) -> None:
    r = client.verificar_efirma_vigente(DEMO_RFC_PF)
    assert r["simulated"] is True
    assert r["status_efirma"] in {"VIGENTE", "POR_VENCER_90D", "VENCIDA", "REVOCADA"}


def test_descargar_acuse_mock(client: SatPortalClient) -> None:
    r = client.descargar_acuse("ACU-2026-001")
    assert r["simulated"] is True
    assert r["folio"] == "ACU-2026-001"


def test_actualizar_obligaciones_siempre_simulada(client: SatPortalClient) -> None:
    r = client.actualizar_obligaciones(DEMO_RFC_PF, "alta_obligacion")
    assert r["simulated"] is True
    assert "advertencia_critica" in r


# ---------- bloqueo de path real cuando hay credenciales ----------


def test_path_real_bloqueado_sin_playwright(monkeypatch) -> None:
    """Si hay credenciales (no es mock) pero no path real implementado, levanta error."""
    monkeypatch.setenv("SAT_RFC", DEMO_RFC_PF)
    monkeypatch.setenv("SAT_CIEC", "fake-ciec")
    client = SatPortalClient()
    with pytest.raises(McpError):
        client.descargar_csf(DEMO_RFC_PF)


def test_actualizar_obligaciones_bloqueado_sin_flag(monkeypatch) -> None:
    """Aún con credenciales, escritura está doble-bloqueada."""
    monkeypatch.setenv("SAT_RFC", DEMO_RFC_PF)
    monkeypatch.setenv("SAT_CIEC", "fake-ciec")
    client = SatPortalClient()
    with pytest.raises(McpError) as exc_info:
        client.actualizar_obligaciones(DEMO_RFC_PF, "alta_obligacion")
    # El mensaje debe mencionar el flag de escritura
    assert "PLUGINS_MX_SAT_PERMITIR_ESCRITURA" in str(exc_info.value) or "escritura" in str(exc_info.value).lower()


# ---------- parseo HTML ----------


def test_parsear_html_estado_vigente() -> None:
    html = """
    <html><body>
        <span id="ContentPlaceHolder1_lblEstadoCFDI">Estado CFDI <strong>Vigente</strong></span>
        <span id="ContentPlaceHolder1_lblEstadoCancelacion">Estatus de cancelación <span>No cancelable</span></span>
    </body></html>
    """
    r = _parsear_html_verificacfdi(
        html, DEMO_UUID_VALIDO, DEMO_RFC_PF, DEMO_RFC_PM_CORTO, "100.00"
    )
    assert r["parseo_fallido"] is False
    assert r["estado_cfdi"] is not None
    assert "Vigente" in r["estado_cfdi"]


def test_parsear_html_estructura_desconocida() -> None:
    html = "<html><body>Página de error</body></html>"
    r = _parsear_html_verificacfdi(
        html, DEMO_UUID_VALIDO, DEMO_RFC_PF, DEMO_RFC_PM_CORTO, "100.00"
    )
    assert r["parseo_fallido"] is True
    assert r["estado_cfdi"] is None


# ---------- bitácora ----------


def test_bitacora_hashea_rfc(client: SatPortalClient, tmp_path) -> None:
    """El RFC no debe escribirse en claro en el audit log."""
    client.consultar_padron(DEMO_RFC_PF)
    # Buscar el archivo JSONL más reciente
    audit_root = tmp_path / "audit" / "sat_portal"
    if not audit_root.exists():
        # Algunas implementaciones pueden no anidar — buscar en tmp_path
        candidates = list((tmp_path / "audit").rglob("*.jsonl"))
    else:
        candidates = list(audit_root.rglob("*.jsonl"))
    assert candidates, "No se generó archivo de bitácora"
    content = candidates[0].read_text()
    # El RFC NO debe aparecer en claro
    assert DEMO_RFC_PF not in content
    # Pero la operación sí debe estar registrada
    assert "consultar_padron" in content
