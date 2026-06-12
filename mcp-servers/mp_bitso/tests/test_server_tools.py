"""End-to-end tests de los tools FastMCP de mp_bitso."""

from __future__ import annotations

import pytest

from mp_bitso.server import (
    BookInput,
    CalculoIsrInput,
    LedgerInput,
    LimitInput,
    OrderBookInput,
    bitso_calcular_isr_cripto_mx,
    bitso_get_account_status,
    bitso_get_balance,
    bitso_get_fees,
    bitso_get_ledger,
    bitso_get_order_book,
    bitso_get_ticker,
    bitso_list_available_books,
    bitso_list_fundings,
    bitso_list_open_orders,
    bitso_list_withdrawals,
    bitso_listar_catalogos,
)


# ---------- públicos ----------


@pytest.mark.asyncio
async def test_ticker() -> None:
    r = await bitso_get_ticker(BookInput(book="btc_mxn"))
    assert r["book"] == "btc_mxn"


@pytest.mark.asyncio
async def test_order_book() -> None:
    r = await bitso_get_order_book(OrderBookInput(book="eth_mxn"))
    assert "bids" in r and "asks" in r


@pytest.mark.asyncio
async def test_available_books() -> None:
    r = await bitso_list_available_books()
    assert "books" in r


# ---------- privados ----------


@pytest.mark.asyncio
async def test_account_status() -> None:
    r = await bitso_get_account_status()
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_balance() -> None:
    r = await bitso_get_balance()
    assert "balances" in r


@pytest.mark.asyncio
async def test_fees() -> None:
    r = await bitso_get_fees()
    assert "fees" in r


@pytest.mark.asyncio
async def test_ledger() -> None:
    r = await bitso_get_ledger(LedgerInput(operations="trades,fees", limit=10))
    assert "ledger" in r


@pytest.mark.asyncio
async def test_fundings() -> None:
    r = await bitso_list_fundings(LimitInput(limit=10))
    assert "fundings" in r


@pytest.mark.asyncio
async def test_withdrawals() -> None:
    r = await bitso_list_withdrawals(LimitInput(limit=10))
    assert "withdrawals" in r


@pytest.mark.asyncio
async def test_open_orders() -> None:
    r = await bitso_list_open_orders()
    assert "orders" in r


# ---------- utility fiscal ----------


@pytest.mark.asyncio
async def test_calcular_isr_resico_baja() -> None:
    r = await bitso_calcular_isr_cripto_mx(
        CalculoIsrInput(
            ganancia_total_mxn=50_000.0,
            otros_ingresos_anuales_mxn=200_000.0,
            regimen="RESICO_PF",
        )
    )
    assert r["regimen"] == "RESICO_PF"
    assert r["isr_aproximado_mxn"] > 0
    assert r["vigencia_validada"] is False


@pytest.mark.asyncio
async def test_calcular_isr_pfae() -> None:
    r = await bitso_calcular_isr_cripto_mx(
        CalculoIsrInput(
            ganancia_total_mxn=100_000.0,
            otros_ingresos_anuales_mxn=500_000.0,
            regimen="PFAE",
        )
    )
    assert r["regimen"] == "PFAE"
    assert r["isr_aproximado_mxn"] > 0


@pytest.mark.asyncio
async def test_calcular_isr_advierte_vigencia() -> None:
    r = await bitso_calcular_isr_cripto_mx(
        CalculoIsrInput(ganancia_total_mxn=10000.0, regimen="GENERAL")
    )
    assert "validar con contador" in r["advertencia"].lower()


# ---------- catálogos ----------


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await bitso_listar_catalogos()
    assert "trading_pairs" in r
    assert "btc_mxn" in r["trading_pairs"]
    assert "fiscal_info_mx" in r
