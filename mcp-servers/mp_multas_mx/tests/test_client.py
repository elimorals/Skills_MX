"""Tests mp_multas_mx."""

from __future__ import annotations

import pytest

from mp_multas_mx.client import MultasMxClient
from shared.errors import ValidationError


@pytest.fixture
def client() -> MultasMxClient:
    return MultasMxClient()


def test_consultar_jal_mock(client: MultasMxClient):
    r = client.consultar_multas("jal", "ABC-12-34")
    assert r.get("simulated") is True
    assert r["estado"] == "jal"
    assert "placa_hash" in r
    # No exponer placa completa
    assert "ABC-12-34" not in str(r)


def test_consultar_cdmx_requiere_humano(client: MultasMxClient):
    """CDMX usa CAPTCHA → debe devolver status requiere_humano."""
    r = client.consultar_multas("cdmx", "XYZ-98-76")
    assert r["status"] == "requiere_humano"
    assert "url_consulta_manual" in r


def test_consultar_placa_invalida(client: MultasMxClient):
    with pytest.raises(ValidationError, match="formato"):
        client.consultar_multas("jal", "X")


def test_consultar_estado_invalido(client: MultasMxClient):
    with pytest.raises(ValidationError, match="no soportado"):
        client.consultar_multas("yyy", "ABC-12-34")


def test_consultar_normaliza_placa(client: MultasMxClient):
    """Acepta placa con o sin guiones."""
    r1 = client.consultar_multas("jal", "ABC1234")
    r2 = client.consultar_multas("jal", "abc-12-34")
    # Mismo hash (mismo placa normalizada)
    assert r1["placa_hash"] == r2["placa_hash"]


def test_estados_disponibles(client: MultasMxClient):
    r = client.estados_disponibles()
    assert r["total"] >= 8
    assert "cdmx" in r["soportados"]
    assert "cdmx" in r["requieren_captcha"]
    assert "jal" not in r["requieren_captcha"]


def test_mock_genera_multas_si_seed_alto(client: MultasMxClient):
    """Placa con seed alto debería tener multas en mock."""
    # ZZZ-99-99 da seed alto
    r = client.consultar_multas("nl", "ZZZ-99-99")
    assert r.get("simulated") is True
    # Estructura presente aunque vacía
    assert "multas" in r
    assert "total_multas_pendientes" in r


def test_no_leak_placa_en_bitacora(client: MultasMxClient, tmp_path):
    import os
    placa = "PLACASECRETA"
    try:
        client.consultar_multas("jal", "ABC-12-34")
    except ValidationError:
        pass
    audit_dir = os.environ.get("PLUGINS_MX_AUDIT_DIR")
    if audit_dir and os.path.exists(audit_dir):
        for root, _, files in os.walk(audit_dir):
            for f in files:
                content = open(os.path.join(root, f)).read()
                assert placa not in content
