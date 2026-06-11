"""Tests for catalog helpers."""

from __future__ import annotations

from mp_mercado_pago.catalogos import (
    PAYMENT_STATUS,
    describe_payment_status,
    is_payment_paid,
    is_payment_refundable,
    is_payment_terminal,
)


def test_describe_known_status() -> None:
    assert describe_payment_status("approved") is not None
    assert "aprobado" in describe_payment_status("approved").lower()


def test_describe_unknown_status() -> None:
    assert describe_payment_status("not_a_real_status") is None


def test_approved_is_paid() -> None:
    assert is_payment_paid("approved") is True


def test_pending_is_not_paid() -> None:
    assert is_payment_paid("pending") is False


def test_rejected_is_not_paid() -> None:
    assert is_payment_paid("rejected") is False


def test_approved_is_terminal() -> None:
    assert is_payment_terminal("approved") is True


def test_pending_is_not_terminal() -> None:
    assert is_payment_terminal("pending") is False


def test_authorized_is_not_terminal() -> None:
    assert is_payment_terminal("authorized") is False


def test_approved_is_refundable() -> None:
    assert is_payment_refundable("approved") is True


def test_rejected_not_refundable() -> None:
    assert is_payment_refundable("rejected") is False


def test_already_refunded_not_refundable_again() -> None:
    assert is_payment_refundable("refunded") is False


def test_all_documented_statuses_are_in_catalog() -> None:
    """Make sure all status code constants used elsewhere are documented."""
    from mp_mercado_pago.catalogos import (
        PAYMENT_STATUS_PAID,
        PAYMENT_STATUS_REFUNDABLE,
        PAYMENT_STATUS_TERMINAL,
    )

    for s in PAYMENT_STATUS_PAID | PAYMENT_STATUS_REFUNDABLE | PAYMENT_STATUS_TERMINAL:
        assert s in PAYMENT_STATUS, f"Status {s!r} used in helpers but not in PAYMENT_STATUS dict"
