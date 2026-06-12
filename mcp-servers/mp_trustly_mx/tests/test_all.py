"""Tests mp_trustly_mx."""

from __future__ import annotations

import pytest

from mp_trustly_mx.client import TrustlyMxClient
from mp_trustly_mx.server import (
    CreatePaymentInput,
    ListPaymentsInput,
    PaymentIdInput,
    RefundInput,
    trustly_create_payment,
    trustly_get_payment,
    trustly_list_payments,
    trustly_listar_catalogos,
    trustly_refund_payment,
)
from shared.errors import ConfigError


@pytest.fixture
def client() -> TrustlyMxClient:
    return TrustlyMxClient()


def test_default_es_mock(client: TrustlyMxClient) -> None:
    assert client.is_mock is True
    assert client.environment == "sandbox"


def test_con_api_key_no_mock(monkeypatch) -> None:
    monkeypatch.setenv("TRUSTLY_API_KEY", "key_test_xxx")
    c = TrustlyMxClient()
    assert c.is_mock is False


def test_require_key_falla_sin(client: TrustlyMxClient) -> None:
    with pytest.raises(ConfigError):
        client._require_key()


@pytest.mark.asyncio
async def test_create_payment_mock(client: TrustlyMxClient) -> None:
    r = await client.create_payment_request(
        amount_mxn=1500.00,
        external_reference="invoice_001",
        customer_email="demo@example.mx",
    )
    assert r["simulated"] is True
    assert r["amount_mxn"] == 1500.00
    assert r["status"] == "pending"
    assert "checkout_url" in r


@pytest.mark.asyncio
async def test_get_payment_pending(client: TrustlyMxClient) -> None:
    r = await client.get_payment_status("trustly_demo_xxx")
    assert r["status"] == "pending"


@pytest.mark.asyncio
async def test_get_payment_paid(client: TrustlyMxClient) -> None:
    r = await client.get_payment_status("trustly_demo_paid_abc")
    assert r["status"] == "completed"
    assert r["completed_at"] is not None


@pytest.mark.asyncio
async def test_list_payments(client: TrustlyMxClient) -> None:
    r = await client.list_payments(status="completed", limit=10)
    assert "payments" in r


@pytest.mark.asyncio
async def test_refund_mock(client: TrustlyMxClient) -> None:
    r = await client.refund_payment("trustly_demo_xxx", amount_mxn=750.0)
    assert r["status"] == "approved"
    assert r["amount_mxn"] == 750.0


@pytest.mark.asyncio
async def test_create_tool() -> None:
    r = await trustly_create_payment(CreatePaymentInput(
        amount_mxn=1000.0,
        external_reference="ref_001",
        customer_email="x@y.mx",
    ))
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_get_tool() -> None:
    r = await trustly_get_payment(PaymentIdInput(payment_id="trustly_demo_xxx"))
    assert "status" in r


@pytest.mark.asyncio
async def test_list_tool() -> None:
    r = await trustly_list_payments(ListPaymentsInput(limit=5))
    assert "payments" in r


@pytest.mark.asyncio
async def test_refund_tool() -> None:
    r = await trustly_refund_payment(RefundInput(payment_id="trustly_demo_xxx"))
    assert r["status"] == "approved"


@pytest.mark.asyncio
async def test_catalogos() -> None:
    r = await trustly_listar_catalogos()
    assert "payment_status" in r
    assert "bbva" in r["bancos_soportados"]
