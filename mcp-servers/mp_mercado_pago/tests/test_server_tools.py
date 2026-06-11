"""End-to-end tests for mp_mercado_pago FastMCP tools."""

from __future__ import annotations

import hashlib
import hmac
import time

import pytest

from mp_mercado_pago.server import (
    CreatePreferenceInput,
    CurrencyMP,
    Item,
    ListPaymentsInput,
    PaymentIdInput,
    PaymentStatusEnum,
    PreferenceIdInput,
    RefundPaymentInput,
    ValidateWebhookInput,
    mercadopago_cancel_payment,
    mercadopago_create_preference,
    mercadopago_get_payment,
    mercadopago_get_preference,
    mercadopago_list_payments,
    mercadopago_listar_catalogos,
    mercadopago_refund_payment,
    mercadopago_validate_webhook_signature,
)


# ---------- create_preference ----------


async def test_create_preference_basic() -> None:
    result = await mercadopago_create_preference(
        CreatePreferenceInput(
            items=[Item(title="Consultoría", quantity=1, unit_price=1500.0)],
            external_reference="cot-001",
        )
    )
    assert result["simulated"] is True
    assert result["preference_id"]
    assert result["external_reference"] == "cot-001"


async def test_create_preference_with_back_urls() -> None:
    result = await mercadopago_create_preference(
        CreatePreferenceInput(
            items=[Item(title="X", quantity=1, unit_price=100)],
            back_url_success="https://example.com/ok",
            back_url_failure="https://example.com/fail",
        )
    )
    # Mock just returns OK; we verify nothing exploded
    assert "preference_id" in result


async def test_create_preference_with_expiration() -> None:
    result = await mercadopago_create_preference(
        CreatePreferenceInput(
            items=[Item(title="X", quantity=1, unit_price=100)],
            expires=True,
            expiration_date_to="2026-12-31T23:59:59.000-06:00",
        )
    )
    assert result["expires"] is True


async def test_create_preference_requires_at_least_one_item() -> None:
    with pytest.raises(Exception):  # pydantic ValidationError
        CreatePreferenceInput(items=[])


async def test_create_preference_negative_price_rejected() -> None:
    with pytest.raises(Exception):
        Item(title="X", quantity=1, unit_price=-10)


async def test_create_preference_invalid_email_rejected() -> None:
    with pytest.raises(Exception):
        CreatePreferenceInput(
            items=[Item(title="X", quantity=1, unit_price=100)],
            payer_email="not-an-email",
        )


# ---------- get_preference ----------


async def test_get_preference_returns_data() -> None:
    result = await mercadopago_get_preference(PreferenceIdInput(preference_id="pref-123"))
    assert result["preference_id"] == "pref-123"
    assert result["simulated"] is True


# ---------- get_payment ----------


async def test_get_payment_includes_derived_flags() -> None:
    result = await mercadopago_get_payment(PaymentIdInput(payment_id="1"))
    assert result["status"] == "approved"
    assert result["is_paid"] is True
    assert result["is_terminal"] is True
    assert result["is_refundable"] is True
    assert "status_description" in result


async def test_get_payment_pending_has_correct_flags() -> None:
    result = await mercadopago_get_payment(PaymentIdInput(payment_id="2"))
    assert result["status"] == "pending"
    assert result["is_paid"] is False
    assert result["is_terminal"] is False
    assert result["is_refundable"] is False


async def test_get_payment_rejected_has_correct_flags() -> None:
    result = await mercadopago_get_payment(PaymentIdInput(payment_id="reject"))
    assert result["is_paid"] is False
    assert result["is_terminal"] is True
    assert result["is_refundable"] is False


# ---------- list_payments ----------


async def test_list_payments_with_filters() -> None:
    result = await mercadopago_list_payments(
        ListPaymentsInput(
            external_reference="cot-123",
            status=PaymentStatusEnum.approved,
            limit=10,
        )
    )
    assert result["simulated"] is True
    assert result["results"] == []


async def test_list_payments_invalid_limit_rejected_by_pydantic() -> None:
    with pytest.raises(Exception):
        ListPaymentsInput(limit=200)  # > 100


# ---------- refund ----------


async def test_refund_full() -> None:
    result = await mercadopago_refund_payment(RefundPaymentInput(payment_id="123"))
    assert result["status"] == "approved"
    assert result["amount"] is None


async def test_refund_partial() -> None:
    result = await mercadopago_refund_payment(
        RefundPaymentInput(payment_id="123", amount=50.0)
    )
    assert result["amount"] == 50.0


async def test_refund_negative_amount_rejected_by_pydantic() -> None:
    with pytest.raises(Exception):
        RefundPaymentInput(payment_id="1", amount=-5)


# ---------- cancel ----------


async def test_cancel_payment_returns_cancelled() -> None:
    result = await mercadopago_cancel_payment(PaymentIdInput(payment_id="999"))
    assert result["status"] == "cancelled"


# ---------- validate_webhook_signature ----------


async def test_validate_webhook_signature_valid() -> None:
    secret = hashlib.sha256(b"plugins-mx-test-fixture-v1").hexdigest()
    ts = int(time.time())
    data_id = "payment-123"
    request_id = "req-abc"
    manifest = f"id:{data_id};request-id:{request_id};ts:{ts};"
    v1 = hmac.new(
        secret.encode(), manifest.encode(), hashlib.sha256
    ).hexdigest()

    result = await mercadopago_validate_webhook_signature(
        ValidateWebhookInput(
            x_signature=f"ts={ts},v1={v1}",
            x_request_id=request_id,
            data_id=data_id,
            secret=secret,
        )
    )
    assert result["valid"] is True
    assert result["reason"] is None


async def test_validate_webhook_signature_invalid() -> None:
    result = await mercadopago_validate_webhook_signature(
        ValidateWebhookInput(
            x_signature="ts=100,v1=wrong",
            x_request_id="r1",
            data_id="d1",
            secret=hashlib.sha256(b"plugins-mx-test-fixture-v1").hexdigest(),
        )
    )
    assert result["valid"] is False
    # Either timestamp expired (default 5min window) or hmac mismatch
    assert result["reason"] in ("expired_timestamp", "hmac_mismatch")


# ---------- listar_catalogos ----------


async def test_listar_catalogos_returns_all() -> None:
    out = await mercadopago_listar_catalogos()
    assert "payment_status" in out
    assert "payment_status_detail" in out
    assert "refund_status" in out
    assert "subscription_status" in out
    assert "webhook_topics" in out
    assert "currency" in out
    assert "advertencia_vigencia" in out

    # Common values
    assert "approved" in out["payment_status"]
    assert "payment" in out["webhook_topics"]
    assert "MXN" in out["currency"]
