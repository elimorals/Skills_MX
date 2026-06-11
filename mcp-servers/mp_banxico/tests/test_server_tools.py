"""End-to-end tests for the FastMCP tool surface of mp_banxico.

These exercise the tools the way an agent would call them, validating
the full flow: pydantic validation → client → format response.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from mp_banxico.server import (
    ConvertirMontoInput,
    GetReferenciaInput,
    GetTcDiaHabilAnteriorInput,
    GetTcDofInput,
    Moneda,
    banxico_convertir_monto,
    banxico_get_inpc,
    banxico_get_tc_dia_habil_anterior,
    banxico_get_tc_dof,
    banxico_get_tiie_28,
    banxico_get_uma,
    banxico_listar_monedas_soportadas,
)


# ---------- banxico_get_tc_dof ----------


async def test_get_tc_dof_on_business_day() -> None:
    # Monday Feb 16, 2026 is a regular business day
    out = await banxico_get_tc_dof(GetTcDofInput(moneda=Moneda.USD, fecha="2026-02-16"))
    assert out["moneda_origen"] == "USD"
    assert out["moneda_destino"] == "MXN"
    assert out["fecha_consultada"] == "2026-02-16"
    assert out["fecha_aplicable"] == "2026-02-16"
    assert out["fecha_ajustada"] is False
    assert out["razon_ajuste"] is None
    assert out["simulated"] is True
    assert 18.0 < out["tipo_cambio"] < 19.0


async def test_get_tc_dof_on_saturday_falls_back_to_friday() -> None:
    # Saturday Feb 14, 2026 → Friday Feb 13
    out = await banxico_get_tc_dof(GetTcDofInput(moneda=Moneda.USD, fecha="2026-02-14"))
    assert out["fecha_consultada"] == "2026-02-14"
    assert out["fecha_aplicable"] == "2026-02-13"
    assert out["fecha_ajustada"] is True
    assert out["razon_ajuste"] == "fin_de_semana"


async def test_get_tc_dof_on_holiday_falls_back() -> None:
    # Monday Feb 2, 2026 = Constitución → falls back to Friday Jan 30
    out = await banxico_get_tc_dof(GetTcDofInput(moneda=Moneda.USD, fecha="2026-02-02"))
    assert out["fecha_consultada"] == "2026-02-02"
    assert out["fecha_aplicable"] == "2026-01-30"
    assert out["fecha_ajustada"] is True
    assert out["razon_ajuste"] == "feriado_bancario"


async def test_get_tc_dof_invalid_date_format_caught_by_pydantic() -> None:
    # Pattern enforces YYYY-MM-DD; passing wrong format raises before tool runs
    with pytest.raises(Exception):
        GetTcDofInput(moneda=Moneda.USD, fecha="2026/02/14")


async def test_get_tc_dof_invalid_date_logical_caught() -> None:
    # 2026-02-30 doesn't exist
    with pytest.raises(Exception):
        GetTcDofInput(moneda=Moneda.USD, fecha="2026-02-30")


# ---------- banxico_get_tc_dia_habil_anterior ----------


async def test_dia_habil_anterior_from_monday() -> None:
    out = await banxico_get_tc_dia_habil_anterior(
        GetTcDiaHabilAnteriorInput(moneda=Moneda.USD, fecha_referencia="2026-02-16")
    )
    # Friday Feb 13 is the prior business day
    assert out["fecha_aplicable"] == "2026-02-13"


async def test_dia_habil_anterior_skips_holiday() -> None:
    # Tuesday Feb 3 → prior business day = Friday Jan 30 (Feb 2 is holiday)
    out = await banxico_get_tc_dia_habil_anterior(
        GetTcDiaHabilAnteriorInput(moneda=Moneda.USD, fecha_referencia="2026-02-03")
    )
    assert out["fecha_aplicable"] == "2026-01-30"


async def test_dia_habil_anterior_defaults_to_today(monkeypatch) -> None:
    # When no fecha_referencia given, uses today
    out = await banxico_get_tc_dia_habil_anterior(
        GetTcDiaHabilAnteriorInput(moneda=Moneda.EUR)
    )
    today = datetime.now(timezone.utc).date()
    # Output's fecha_aplicable should be strictly before today
    fecha_aplicable = date.fromisoformat(out["fecha_aplicable"])
    assert fecha_aplicable < today


# ---------- banxico_convertir_monto ----------


async def test_convertir_usd_to_mxn() -> None:
    out = await banxico_convertir_monto(
        ConvertirMontoInput(
            monto=100, de_moneda="USD", a_moneda="MXN", fecha="2026-02-16"
        )
    )
    assert out["moneda_original"] == "USD"
    assert out["moneda_convertida"] == "MXN"
    assert out["direccion"] == "USD_to_MXN"
    # 100 USD * ~18.5 = ~1850 MXN
    assert 1800 < out["monto_convertido"] < 1900


async def test_convertir_mxn_to_usd() -> None:
    out = await banxico_convertir_monto(
        ConvertirMontoInput(
            monto=1850, de_moneda="MXN", a_moneda="USD", fecha="2026-02-16"
        )
    )
    assert out["direccion"] == "MXN_to_USD"
    # 1850 / ~18.5 = ~100
    assert 99 < out["monto_convertido"] < 101


async def test_convertir_same_currency_returns_validation_error() -> None:
    out = await banxico_convertir_monto(
        ConvertirMontoInput(monto=100, de_moneda="USD", a_moneda="USD")
    )
    # Error envelope
    assert out["error"] is True
    assert out["code"] == "validation_error"


async def test_convertir_cross_currency_returns_validation_error() -> None:
    out = await banxico_convertir_monto(
        ConvertirMontoInput(monto=100, de_moneda="USD", a_moneda="EUR")
    )
    assert out["error"] is True
    assert out["code"] == "validation_error"


async def test_convertir_unsupported_currency_returns_validation_error() -> None:
    out = await banxico_convertir_monto(
        ConvertirMontoInput(monto=100, de_moneda="ARS", a_moneda="MXN")
    )
    assert out["error"] is True
    assert out["code"] == "validation_error"


async def test_convertir_negative_amount_rejected_by_pydantic() -> None:
    with pytest.raises(Exception):
        ConvertirMontoInput(monto=-1, de_moneda="USD", a_moneda="MXN")


async def test_convertir_zero_amount_rejected_by_pydantic() -> None:
    with pytest.raises(Exception):
        ConvertirMontoInput(monto=0, de_moneda="USD", a_moneda="MXN")


async def test_convertir_default_uses_prior_business_day() -> None:
    # No fecha → uses prior business day, which should be a weekday
    out = await banxico_convertir_monto(
        ConvertirMontoInput(monto=100, de_moneda="USD", a_moneda="MXN")
    )
    fecha_tc = date.fromisoformat(out["fecha_tc"])
    assert fecha_tc.weekday() < 5  # Mon-Fri


async def test_convertir_returns_simulated_flag_in_mock_mode() -> None:
    out = await banxico_convertir_monto(
        ConvertirMontoInput(monto=100, de_moneda="USD", a_moneda="MXN", fecha="2026-02-16")
    )
    assert out["simulated"] is True


# ---------- banxico_get_uma ----------


async def test_get_uma_returns_diaria_mensual_anual() -> None:
    out = await banxico_get_uma(GetReferenciaInput())
    assert "valor_diario" in out
    assert "valor_mensual" in out
    assert "valor_anual" in out
    # Mensual ≈ diaria * 30.4
    assert out["valor_mensual"] == round(out["valor_diario"] * 30.4, 2)
    # Anual ≈ diaria * 365
    assert out["valor_anual"] == round(out["valor_diario"] * 365, 2)


async def test_get_uma_in_mock_mode_returns_plausible_value() -> None:
    out = await banxico_get_uma(GetReferenciaInput())
    # 2024 ref ~ 108.57; with ±1% jitter
    assert 100 < out["valor_diario"] < 120


# ---------- banxico_get_inpc ----------


async def test_get_inpc_returns_value() -> None:
    out = await banxico_get_inpc(GetReferenciaInput())
    assert "inpc" in out
    assert out["inpc"] > 0


# ---------- banxico_get_tiie_28 ----------


async def test_get_tiie_28_returns_value() -> None:
    out = await banxico_get_tiie_28(GetReferenciaInput())
    assert "tiie_28" in out
    assert out["tiie_28"] > 0


# ---------- banxico_listar_monedas_soportadas ----------


async def test_listar_monedas_returns_all_supported() -> None:
    out = await banxico_listar_monedas_soportadas()
    pares = {item["par"] for item in out["pares_soportados"]}
    assert pares == {"USD/MXN", "EUR/MXN", "GBP/MXN", "CAD/MXN", "JPY/MXN"}


async def test_listar_monedas_includes_serie_codes() -> None:
    out = await banxico_listar_monedas_soportadas()
    for item in out["pares_soportados"]:
        assert item["serie"].startswith("SF")
        assert len(item["serie"]) >= 7
