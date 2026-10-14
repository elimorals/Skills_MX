"""Tests mp_tenencia_mx (datos 2026 con fuente; None donde no hay verificación)."""
from __future__ import annotations

import pytest

from mp_tenencia_mx.client import TenenciaMxClient
from shared.errors import NotFoundError, ValidationError
from shared.tenencia_mx import CATALOGO_TENENCIA, calcular_tenencia


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path / "audit"))


@pytest.fixture
def client() -> TenenciaMxClient:
    return TenenciaMxClient()


def test_todo_monto_publicado_tiene_fuente() -> None:
    for e in CATALOGO_TENENCIA:
        if e.refrendo_mxn is not None or e.umbral_subsidio_100_mxn is not None:
            assert e.fuentes, e.clave


def test_cdmx_bajo_umbral_subsidiado() -> None:
    r = calcular_tenencia("cdmx", 450_000, 2024, 2026)
    assert r["subsidio_100_elegible"] is True
    assert r["tenencia_mxn"] == 0
    assert r["refrendo_mxn"] == 760
    assert r["subtotal_mxn"] == 760
    assert r["simulated"] is False


def test_edomex_sobre_umbral_no_inventa_tenencia() -> None:
    r = calcular_tenencia("edomex", 900_000, 2025, 2026)
    assert r["tenencia_mxn"] is None
    assert r["subtotal_mxn"] is None
    assert r["requiere_calculo_oficial"] is True
    assert r["advertencias"]


def test_umbral_es_inclusivo() -> None:
    assert calcular_tenencia("edomex", 638_000, 2025, 2026)["subsidio_100_elegible"] is True


def test_jal_sin_tenencia() -> None:
    r = calcular_tenencia("jal", 900_000, 2025, 2026)
    assert r["tenencia_mxn"] == 0
    assert r["subtotal_mxn"] == 1000


def test_estado_sin_refrendo_verificado() -> None:
    r = calcular_tenencia("hgo", 300_000, 2020, 2026)
    assert r["refrendo_mxn"] is None
    assert r["verificado_2026"] is False


def test_errores(client: TenenciaMxClient) -> None:
    with pytest.raises(NotFoundError):
        client.calcular("narnia", 300_000, 2024)
    with pytest.raises(ValidationError):
        client.calcular("cdmx", 300_000, 1900)


def test_comparar_separa_sin_monto(client: TenenciaMxClient) -> None:
    r = client.comparar_estados(["cdmx", "jal", "hgo", "narnia"], 400_000, 2024)
    assert [x["estado"] for x in r["barato_a_caro"]] == ["cdmx", "jal"]
    assert [x["estado"] for x in r["sin_monto_verificado"]] == ["hgo"]
    assert r["errores"][0]["estado"] == "narnia"


def test_info_estado(client: TenenciaMxClient) -> None:
    r = client.info_estado("cdmx")
    assert r["umbral_subsidio_100_mxn"] == 638_000
    with pytest.raises(NotFoundError):
        client.info_estado("narnia")


def test_listar(client: TenenciaMxClient) -> None:
    con = client.listar_estados(solo_con_tenencia=True)
    assert {e["clave"] for e in con["estados"]} == {"cdmx", "edomex", "qro"}
