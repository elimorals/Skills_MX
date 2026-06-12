"""End-to-end tests para los tools FastMCP de mp_conekta."""

from __future__ import annotations

import base64
import hashlib
import hmac

import pytest

from mp_conekta.server import (
    ChargeOnOrderInput,
    CreateCustomerInput,
    CreateOrderInput,
    CustomerIdInput,
    CustomerInfo,
    LineItem,
    ListOrdersInput,
    OrderIdInput,
    PaymentLinkInput,
    PaymentMethodInput,
    RefundOrderInput,
    SubscriptionCreateInput,
    SubscriptionUpdateInput,
    WebhookValidateInput,
    conekta_create_charge_on_order,
    conekta_create_customer,
    conekta_create_order,
    conekta_create_payment_link,
    conekta_get_customer,
    conekta_get_order,
    conekta_list_orders,
    conekta_listar_catalogos,
    conekta_refund_order,
    conekta_subscription_cancel,
    conekta_subscription_create,
    conekta_subscription_update,
    conekta_validate_webhook,
)
from mp_conekta.tests.conftest import DEMO_SECRET


# ---------- orders ----------


@pytest.mark.asyncio
async def test_create_order_devuelve_simulated() -> None:
    r = await conekta_create_order(
        CreateOrderInput(
            line_items=[LineItem(name="Producto", unit_price=10000, quantity=1)],
            currency="MXN",
            customer_info=CustomerInfo(
                name="Juan", email="juan@example.mx", phone="+525512345678"
            ),
        )
    )
    assert r["simulated"] is True
    assert r["amount"] == 10000


@pytest.mark.asyncio
async def test_get_order() -> None:
    r = await conekta_get_order(OrderIdInput(order_id="ord_xyz"))
    assert r["id"] == "ord_xyz"
    assert r["simulated"] is True


@pytest.mark.asyncio
async def test_list_orders() -> None:
    r = await conekta_list_orders(ListOrdersInput(limit=10, payment_status="paid"))
    assert r["simulated"] is True
    assert r["data"] == []


# ---------- charges ----------


@pytest.mark.asyncio
async def test_charge_on_order_oxxo() -> None:
    r = await conekta_create_charge_on_order(
        ChargeOnOrderInput(
            order_id="ord_x",
            payment_method=PaymentMethodInput(type="oxxo_cash"),
        )
    )
    assert r["simulated"] is True
    assert r["payment_method"]["type"] == "oxxo_cash"


@pytest.mark.asyncio
async def test_refund_total() -> None:
    r = await conekta_refund_order(RefundOrderInput(order_id="ord_x"))
    assert r["status"] == "refunded"


@pytest.mark.asyncio
async def test_refund_parcial() -> None:
    r = await conekta_refund_order(
        RefundOrderInput(order_id="ord_x", amount=5000, reason="duplicate")
    )
    assert r["amount"] == 5000


# ---------- customers ----------


@pytest.mark.asyncio
async def test_create_customer() -> None:
    r = await conekta_create_customer(
        CreateCustomerInput(name="Juan", email="juan@x.mx", phone="+5215512345678")
    )
    assert r["simulated"] is True
    assert r["id"].startswith("cus_")


@pytest.mark.asyncio
async def test_get_customer() -> None:
    r = await conekta_get_customer(CustomerIdInput(customer_id="cus_demo"))
    assert r["id"] == "cus_demo"


# ---------- payment links ----------


@pytest.mark.asyncio
async def test_payment_link() -> None:
    r = await conekta_create_payment_link(
        PaymentLinkInput(name="Asesoría 1hr", amount=80000, currency="MXN")
    )
    assert r["simulated"] is True
    assert r["amount"] == 80000


# ---------- subscriptions ----------


@pytest.mark.asyncio
async def test_subscription_create() -> None:
    r = await conekta_subscription_create(
        SubscriptionCreateInput(customer_id="cus_x", plan_id="plan_basic")
    )
    assert r["status"] == "active"


@pytest.mark.asyncio
async def test_subscription_update() -> None:
    r = await conekta_subscription_update(
        SubscriptionUpdateInput(customer_id="cus_x", plan_id="plan_pro")
    )
    assert r["plan_id"] == "plan_pro"


@pytest.mark.asyncio
async def test_subscription_cancel() -> None:
    r = await conekta_subscription_cancel(CustomerIdInput(customer_id="cus_x"))
    assert r["status"] == "canceled"


# ---------- validate webhook ----------


@pytest.mark.asyncio
async def test_webhook_valido_digest() -> None:
    payload_bytes = b'{"event":"charge.paid"}'
    mac = hmac.new(DEMO_SECRET.encode(), payload_bytes, hashlib.sha256).digest()
    digest = "SHA256=" + base64.b64encode(mac).decode("ascii")
    r = await conekta_validate_webhook(
        WebhookValidateInput(
            headers={"Digest": digest},
            payload=payload_bytes.decode("utf-8"),
            secret=DEMO_SECRET,
        )
    )
    assert r["valid"] is True
    assert r["signature_format"] == "digest"


@pytest.mark.asyncio
async def test_webhook_invalido() -> None:
    r = await conekta_validate_webhook(
        WebhookValidateInput(
            headers={"Digest": "SHA256=AAAA"},
            payload='{"event":"charge.paid"}',
            secret=DEMO_SECRET,
        )
    )
    assert r["valid"] is False


# ---------- catálogos ----------


@pytest.mark.asyncio
async def test_listar_catalogos() -> None:
    r = await conekta_listar_catalogos()
    assert "order_status" in r
    assert "paid" in r["order_status"]
    assert "card" in r["payment_method_type"]
    assert "charge.paid" in r["webhook_events"]
