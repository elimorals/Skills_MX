"""Tests de los drivers Playwright bancarios."""

from __future__ import annotations

import pytest

from mp_bancos_mx.playwright_drivers import (
    BanamexDriver,
    BanorteDriver,
    BbvaDriver,
    DriverMode,
    SantanderDriver,
    get_driver,
)


@pytest.fixture
def clean_env(monkeypatch):
    """Limpia env vars relevantes para evitar contaminación entre tests."""
    for v in [
        "PLUGINS_MX_MOCK", "PLUGINS_MX_PLAYWRIGHT_REAL",
        "BBVA_USUARIO", "BBVA_PASSWORD",
        "BANAMEX_USUARIO", "BANAMEX_PASSWORD",
        "SANTANDER_USUARIO", "SANTANDER_PASSWORD",
        "BANORTE_USUARIO", "BANORTE_PASSWORD",
    ]:
        monkeypatch.delenv(v, raising=False)


def test_get_driver_4_bancos_soportados():
    assert get_driver("bbva") is BbvaDriver
    assert get_driver("banamex") is BanamexDriver
    assert get_driver("santander") is SantanderDriver
    assert get_driver("banorte") is BanorteDriver
    assert get_driver("XYZ") is None


def test_get_driver_case_insensitive():
    assert get_driver("BBVA") is BbvaDriver
    assert get_driver("Banamex") is BanamexDriver


def test_bbva_modo_mock_sin_credenciales(clean_env):
    d = BbvaDriver.from_env()
    assert d.get_mode() == DriverMode.MOCK


def test_bbva_modo_blocked_con_credenciales_sin_optin(clean_env, monkeypatch):
    monkeypatch.setenv("BBVA_USUARIO", "u")
    monkeypatch.setenv("BBVA_PASSWORD", "p")
    d = BbvaDriver.from_env()
    assert d.get_mode() == DriverMode.BLOCKED


def test_bbva_listar_movimientos_mock(clean_env):
    d = BbvaDriver.from_env()
    r = d.listar_movimientos("01234567890", dias=30)
    assert r["operation"] == "listar_movimientos"
    assert r["banco"] == "bbva"
    assert r["simulated"] is True
    assert r["data"]["total"] == 2
    movs = r["data"]["movimientos"]
    assert any(m["tipo"] == "deposito" for m in movs)


def test_bbva_no_loguea_cuenta_en_claro(tmp_path, monkeypatch):
    from shared.bitacora import Bitacora

    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    bita = Bitacora("bancos_mx_bbva")
    d = BbvaDriver(bitacora=bita)
    d.listar_movimientos("01234567890")
    entries = bita.tail(5)
    for e in entries:
        params = e.get("params", {})
        assert "01234567890" not in str(params)
        assert params.get("cuenta_hash")


def test_banamex_descargar_estado_mock(clean_env):
    d = BanamexDriver.from_env()
    r = d.descargar_estado_cuenta("01234", 2025, 5)
    assert r["data"]["mes"] == 5
    assert r["data"]["ejercicio"] == 2025
    assert r["data"]["ruta_local"] is None
    assert r["simulated"] is True


def test_santander_verificar_pago_mock(clean_env):
    d = SantanderDriver.from_env()
    r = d.verificar_pago_por_referencia("ABC-001", 1500.00)
    assert r["data"]["encontrado"] is False
    assert r["data"]["monto_esperado"] == "1500.0"
    assert r["simulated"] is True


def test_banorte_totp_sin_seed_devuelve_none(clean_env):
    d = BanorteDriver.from_env()
    assert d._generar_totp() is None


def test_banorte_totp_con_seed_genera_codigo(monkeypatch, clean_env):
    monkeypatch.setenv("BANORTE_USUARIO", "u")
    monkeypatch.setenv("BANORTE_PASSWORD", "p")
    monkeypatch.setenv("BANORTE_SOFT_TOKEN_SEED", "JBSWY3DPEHPK3PXP")  # seed base32 estándar
    d = BanorteDriver.from_env()
    code = d._generar_totp()
    if code is None:
        pytest.skip("pyotp no instalado")
    assert code.isdigit() and 6 <= len(code) <= 8


def test_plugins_mx_mock_force_overrides_credentials(monkeypatch, clean_env):
    monkeypatch.setenv("BBVA_USUARIO", "u")
    monkeypatch.setenv("BBVA_PASSWORD", "p")
    monkeypatch.setenv("PLUGINS_MX_PLAYWRIGHT_REAL", "1")
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    d = BbvaDriver.from_env()
    assert d.get_mode() == DriverMode.MOCK


def test_movimiento_serializable():
    from datetime import date
    from decimal import Decimal

    from mp_bancos_mx.playwright_drivers import Movimiento

    m = Movimiento(
        fecha=date(2026, 1, 15),
        tipo="deposito",
        concepto="X",
        referencia_numerica="R1",
        clave_rastreo_spei="K1",
        monto=Decimal("100.00"),
    )
    d = m.to_dict()
    assert d["fecha"] == "2026-01-15"
    assert d["monto"] == "100.00"
    assert d["saldo_resultante"] is None
