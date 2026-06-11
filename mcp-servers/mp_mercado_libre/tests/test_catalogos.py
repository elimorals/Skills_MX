"""Tests de las funciones helper de catalogos.py."""

from __future__ import annotations

from mp_mercado_libre.catalogos import (
    ITEM_STATUS,
    ORDER_STATUS,
    SHIPMENT_STATUS,
    describe_item_status,
    is_item_reactivable,
    is_item_terminal,
    is_order_paid,
    is_order_terminal,
    is_shipment_awaiting_seller,
    is_shipment_delivered,
    is_shipment_in_transit,
)


def test_describe_known_item_status() -> None:
    assert "activa" in describe_item_status("active").lower()


def test_describe_unknown_item_status() -> None:
    assert describe_item_status("does_not_exist") is None


def test_paused_is_reactivable() -> None:
    assert is_item_reactivable("paused") is True


def test_closed_is_not_reactivable() -> None:
    assert is_item_reactivable("closed") is False


def test_closed_is_terminal() -> None:
    assert is_item_terminal("closed") is True


def test_active_is_not_terminal() -> None:
    assert is_item_terminal("active") is False


def test_paid_order_is_paid() -> None:
    assert is_order_paid("paid") is True


def test_partially_paid_counts_as_paid() -> None:
    assert is_order_paid("partially_paid") is True


def test_pending_payment_not_paid() -> None:
    assert is_order_paid("payment_required") is False


def test_paid_is_terminal() -> None:
    assert is_order_terminal("paid") is True


def test_cancelled_is_terminal() -> None:
    assert is_order_terminal("cancelled") is True


def test_payment_in_process_is_not_terminal() -> None:
    assert is_order_terminal("payment_in_process") is False


def test_delivered_shipment() -> None:
    assert is_shipment_delivered("delivered") is True
    assert is_shipment_delivered("shipped") is False


def test_in_transit_shipment() -> None:
    assert is_shipment_in_transit("shipped") is True
    assert is_shipment_in_transit("delivered") is False


def test_awaiting_seller_shipment() -> None:
    assert is_shipment_awaiting_seller("pending") is True
    assert is_shipment_awaiting_seller("handling") is True
    assert is_shipment_awaiting_seller("ready_to_ship") is True
    assert is_shipment_awaiting_seller("shipped") is False


def test_catalog_coverage_for_all_helper_constants() -> None:
    """Los estados que mencionan los helpers deben estar documentados."""
    from mp_mercado_libre.catalogos import (
        ITEM_STATUS_REACTIVABLE,
        ITEM_STATUS_TERMINAL,
        ORDER_STATUS_PAID,
        ORDER_STATUS_TERMINAL,
        SHIPMENT_STATUS_AWAITING_SELLER,
        SHIPMENT_STATUS_DELIVERED,
        SHIPMENT_STATUS_IN_TRANSIT,
    )

    for s in ITEM_STATUS_REACTIVABLE | ITEM_STATUS_TERMINAL:
        assert s in ITEM_STATUS, f"{s!r} no está en ITEM_STATUS"
    for s in ORDER_STATUS_PAID | ORDER_STATUS_TERMINAL:
        assert s in ORDER_STATUS, f"{s!r} no está en ORDER_STATUS"
    for s in (
        SHIPMENT_STATUS_AWAITING_SELLER
        | SHIPMENT_STATUS_DELIVERED
        | SHIPMENT_STATUS_IN_TRANSIT
    ):
        assert s in SHIPMENT_STATUS, f"{s!r} no está en SHIPMENT_STATUS"
