"""Path real CNBV (PES) con respuestas reales capturadas 2026-10-14 (personas morales)."""

from pathlib import Path

import pytest
import respx

from mp_cnbv_fintech import pes
from mp_cnbv_fintech.client import CnbvFintechClient
from shared.errors import McpError, UpstreamError, ValidationError

FX = Path(__file__).parent / "fixtures"
URL = f"{pes.BASE}/Consulta/ConsultaEntidad"
IFPE = (FX / "pes_ifpe_2026-10-14.html").read_text(encoding="utf-8")
MELI = (FX / "pes_entidad_mercadolibre_2026-10-14.html").read_text(encoding="utf-8")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "c"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "a"))
    return CnbvFintechClient()


def test_parsear_ifpe_real():
    filas = pes.parsear(IFPE)
    assert len(filas) == 51
    assert filas[0]["casfim"] == "65-061"
    assert filas[0]["nombre_corto"] == "ACCESA"
    assert filas[0]["sector"] == pes.SECTOR_IFPE
    assert filas[0]["detalle_url"].startswith("https://pes.cnbv.gob.mx/DetalleEntidad?q=")


def test_parsear_html_ajeno():
    with pytest.raises(UpstreamError):
        pes.parsear("<html>mantenimiento</html>")


def test_listar_ifpe_real(client):
    with respx.mock() as router:
        route = router.get(URL).respond(200, text=IFPE)
        r = client.listar_ifpe()
        assert "FONDOS+DE+PAGO" in str(route.calls[0].request.url).upper().replace("%20", "+")
    assert r["simulated"] is False
    assert r["total"] == 51


def test_consultar_por_nombre(client):
    with respx.mock() as router:
        router.get(URL).respond(200, text=MELI)
        r = client.consultar_itf(nombre="MERCADOLIBRE")
    assert r["encontrada"] is True
    assert r["tipo"] == "ifpe"
    assert r["simulated"] is False


def test_solo_rfc_en_real_exige_nombre(client):
    with pytest.raises(ValidationError):
        client.consultar_itf(rfc="XAXX010101000")


def test_modelos_novedosos_sin_fuente(client):
    with pytest.raises(McpError) as e:
        client.listar_modelos_novedosos()
    assert e.value.code == "sin_fuente_publica"


def test_pes_caido(client):
    with respx.mock() as router:
        router.get(URL).respond(503)
        with pytest.raises(UpstreamError):
            client.listar_ifc()


@pytest.mark.live
def test_live_pes_ifpe(client):
    r = client.listar_ifpe()
    assert r["total"] > 10
    v = client.verificar_contraparte(nombre="MERCADOLIBRE", tipo_operacion="fondos_pago")
    assert v["puede_operar"] is True
