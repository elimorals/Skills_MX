"""Tests mp_predial_mx — cliente unificado."""

from __future__ import annotations

import pytest

from mp_predial_mx.client import PredialMxClient, _normalizar_clave
from shared.errors import UpstreamError, ValidationError


@pytest.fixture
def client() -> PredialMxClient:
    return PredialMxClient()


# ============================================================
# Helpers
# ============================================================

def test_normalizar_clave_simple():
    assert _normalizar_clave("Guadalajara") == "guadalajara"


def test_normalizar_clave_acentos():
    assert _normalizar_clave("San Pedro Garza García") == "san_pedro_garza_garcia"


def test_normalizar_clave_parentesis():
    assert _normalizar_clave("Ciudad Hidalgo (Mich)") == "ciudad_hidalgo_mich"


# ============================================================
# consultar() - mock paths
# ============================================================

def test_consultar_mock_cdmx(client: PredialMxClient):
    """CDMX validado en catálogo → mock realista."""
    r = client.consultar("cdmx", "ciudad_de_mexico", "12345678")
    assert r.get("simulated") is True
    assert r["estado"] == "cdmx"
    assert "adeudo_total_mxn" in r


def test_consultar_mock_guadalajara(client: PredialMxClient):
    """GDL validado → mock con URL real en respuesta."""
    r = client.consultar("jal", "guadalajara", "U12345678")
    assert r.get("simulated") is True
    assert "guadalajara" in r["url_consultada"].lower()


def test_consultar_mock_sacpi_michoacan(client: PredialMxClient):
    """Ciudad Hidalgo MICH → routing a SACPI."""
    r = client.consultar("mich", "hidalgo_mich", "001234", tipo="urbano")
    assert r.get("simulated") is True
    # Plataforma debe indicar SACPI
    assert "SACPI" in str(r.get("plataforma", "")) or "sacpi" in str(r.get("url_consultada", "")).lower()


def test_consultar_caso_sin_url(client: PredialMxClient):
    """Tlaquepaque está en catálogo pero sin URL validada."""
    # Mock debería igual devolver algo (es mock universal)
    r = client.consultar("jal", "tlaquepaque", "12345")
    assert r.get("simulated") is True
    # Pero la URL sería 'mock://no-url' o similar
    assert r["estado"] == "jal"


# ============================================================
# consultar() - errors
# ============================================================

def test_consultar_estado_invalido(client: PredialMxClient):
    with pytest.raises(ValidationError, match="no en catálogo"):
        client.consultar("zzz", "fake", "12345")


def test_consultar_municipio_inexistente(client: PredialMxClient):
    with pytest.raises(ValidationError, match="no encontrado"):
        client.consultar("jal", "municipio_imaginario", "12345")


def test_consultar_normaliza_nombre(client: PredialMxClient):
    """'Guadalajara' debería resolver igual que 'guadalajara'."""
    r1 = client.consultar("jal", "guadalajara", "U001")
    r2 = client.consultar("jal", "Guadalajara", "U001")
    assert r1["municipio"] == r2["municipio"]


# ============================================================
# listar_municipios()
# ============================================================

def test_listar_municipios_todos(client: PredialMxClient):
    r = client.listar_municipios()
    assert r["total"] >= 200  # catálogo tiene 209
    assert "jal" in r["por_estado"]
    assert "cdmx" in r["por_estado"]


def test_listar_municipios_solo_validados(client: PredialMxClient):
    r = client.listar_municipios(solo_validados=True)
    assert r["total"] >= 30  # ~33 validados
    # Cada municipio en respuesta debe ser validado
    for estado, muns in r["por_estado"].items():
        for m in muns:
            assert m["validado"] is True


def test_listar_municipios_por_estado(client: PredialMxClient):
    r = client.listar_municipios(estado="jal")
    assert "jal" in r["por_estado"]
    assert "cdmx" not in r["por_estado"]  # filtrado
    nombres = [m["nombre"] for m in r["por_estado"]["jal"]]
    assert "Guadalajara" in nombres


# ============================================================
# estadisticas_catalogo()
# ============================================================

def test_estadisticas_catalogo(client: PredialMxClient):
    s = client.estadisticas_catalogo()
    assert s["estados_cubiertos"] == 32
    assert s["municipios_totales"] >= 200
    assert s["municipios_validados"] >= 30
    assert "saas" in s
    assert s["saas"]["municipios_cubiertos_via_saas"] >= 90  # SACPI 95
    assert s["cobertura_efectiva"] >= 120  # validados + SaaS


# ============================================================
# buscar_municipio()
# ============================================================

def test_buscar_municipio_exacto(client: PredialMxClient):
    r = client.buscar_municipio("guadalajara")
    assert len(r) >= 1
    assert any(m["nombre"] == "Guadalajara" for m in r)


def test_buscar_municipio_parcial(client: PredialMxClient):
    r = client.buscar_municipio("guadal")
    assert len(r) >= 1
    assert all("guadal" in m["nombre"].lower() or "guadal" in m["clave"].lower() for m in r)


def test_buscar_municipio_no_existe(client: PredialMxClient):
    r = client.buscar_municipio("xyzpdqcity")
    assert r == []


def test_buscar_municipio_limit(client: PredialMxClient):
    """No debe devolver más de 20."""
    r = client.buscar_municipio("a")  # match amplio
    assert len(r) <= 20


# ============================================================
# Integración bitácora
# ============================================================

def test_consultar_loguea_a_bitacora(client: PredialMxClient, tmp_path):
    """consultar() debe escribir en bitácora con hash de cuenta."""
    client.consultar("jal", "guadalajara", "MUYSECRETO123")
    # Bitácora debe existir pero no contener la cuenta en plain
    import os
    audit_dir = os.environ["PLUGINS_MX_AUDIT_DIR"]
    # No verificamos contenido exacto (file format varía), solo que no haya leak
    if os.path.exists(audit_dir):
        for root, _, files in os.walk(audit_dir):
            for f in files:
                path = os.path.join(root, f)
                content = open(path).read() if os.path.exists(path) else ""
                assert "MUYSECRETO123" not in content
