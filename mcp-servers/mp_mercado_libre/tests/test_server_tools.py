"""End-to-end tests para los tools FastMCP de mercadolibre_mcp."""

from __future__ import annotations

import pytest

from mp_mercado_libre.server import (
    AnswerQuestionInput,
    GetItemInput,
    ListItemsInput,
    ListMessagesInput,
    ListOrdersInput,
    ListQuestionsInput,
    OrderIdInput,
    SellerIdInput,
    SendMessageInput,
    ToggleStatusInput,
    UpdatePriceInput,
    UpdateStockInput,
    mercadolibre_activate_item,
    mercadolibre_answer_question,
    mercadolibre_get_item,
    mercadolibre_get_me,
    mercadolibre_get_order,
    mercadolibre_get_seller_reputation,
    mercadolibre_list_items,
    mercadolibre_list_messages,
    mercadolibre_list_orders,
    mercadolibre_list_questions,
    mercadolibre_listar_catalogos,
    mercadolibre_pause_item,
    mercadolibre_send_message,
    mercadolibre_update_price,
    mercadolibre_update_stock,
)


@pytest.mark.asyncio
async def test_get_me_returns_simulated() -> None:
    me = await mercadolibre_get_me()
    assert me["simulated"] is True
    assert me["site_id"] == "MLM"


@pytest.mark.asyncio
async def test_list_items_default_args() -> None:
    page = await mercadolibre_list_items(ListItemsInput())
    assert page["simulated"] is True
    assert "results" in page
    assert "paging" in page


@pytest.mark.asyncio
async def test_list_items_filtered_by_status() -> None:
    from mp_mercado_libre.server import ItemStatus

    page = await mercadolibre_list_items(
        ListItemsInput(status=ItemStatus.paused, limit=2)
    )
    assert all(it["status"] == "paused" for it in page["items_preview"])


@pytest.mark.asyncio
async def test_get_item_enriches_with_derived_flags() -> None:
    item = await mercadolibre_get_item(GetItemInput(item_id="MLM0000000002"))
    assert item["status"] == "paused"
    assert item["is_reactivable"] is True
    assert item["is_terminal"] is False
    assert "Pausada" in item["status_description"] or "pausa" in item["status_description"].lower()


@pytest.mark.asyncio
async def test_update_stock_mock() -> None:
    out = await mercadolibre_update_stock(
        UpdateStockInput(item_id="MLM0000000111", available_quantity=42)
    )
    assert out["simulated"] is True
    assert out["available_quantity"] == 42


@pytest.mark.asyncio
async def test_update_price_mock() -> None:
    out = await mercadolibre_update_price(
        UpdatePriceInput(item_id="MLM0000000111", price=199.99)
    )
    assert out["simulated"] is True
    assert out["price"] == 199.99


@pytest.mark.asyncio
async def test_pause_and_activate_item_mock() -> None:
    paused = await mercadolibre_pause_item(
        ToggleStatusInput(item_id="MLM0000000111")
    )
    assert paused["status"] == "paused"
    activated = await mercadolibre_activate_item(
        ToggleStatusInput(item_id="MLM0000000111")
    )
    assert activated["status"] == "active"


@pytest.mark.asyncio
async def test_get_order_enriches_with_flags() -> None:
    order = await mercadolibre_get_order(OrderIdInput(order_id="12345"))
    assert order["status"] == "paid"
    assert order["is_paid"] is True
    assert order["is_terminal"] is True


@pytest.mark.asyncio
async def test_list_orders_default() -> None:
    out = await mercadolibre_list_orders(ListOrdersInput())
    assert out["simulated"] is True
    assert "results" in out


@pytest.mark.asyncio
async def test_list_messages_mock_empty() -> None:
    out = await mercadolibre_list_messages(
        ListMessagesInput(pack_id="pack-test-1")
    )
    assert out["simulated"] is True
    assert out["messages"] == []


@pytest.mark.asyncio
async def test_send_message_mock() -> None:
    out = await mercadolibre_send_message(
        SendMessageInput(pack_id="pack-1", buyer_id=42, text="Mensaje de prueba")
    )
    assert out["simulated"] is True
    assert out["text"] == "Mensaje de prueba"


@pytest.mark.asyncio
async def test_list_questions_default_unanswered() -> None:
    out = await mercadolibre_list_questions(ListQuestionsInput())
    assert out["simulated"] is True
    assert out["filters_applied"]["status"] == "UNANSWERED"


@pytest.mark.asyncio
async def test_answer_question_mock() -> None:
    out = await mercadolibre_answer_question(
        AnswerQuestionInput(question_id=12345, text="Sí, está disponible.")
    )
    assert out["simulated"] is True
    assert out["status"] == "ANSWERED"


@pytest.mark.asyncio
async def test_get_seller_reputation_mock() -> None:
    out = await mercadolibre_get_seller_reputation(SellerIdInput())
    assert out["simulated"] is True
    assert "level_id" in out
    assert "transactions" in out


@pytest.mark.asyncio
async def test_listar_catalogos_is_offline() -> None:
    out = await mercadolibre_listar_catalogos()
    assert "item_status" in out
    assert "order_status" in out
    assert "shipment_status" in out
    assert "MLM" in out["site_id"]


# ---------- validation errors ----------


def test_get_item_invalid_id_pattern() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        GetItemInput(item_id="not-a-meli-id")


def test_update_stock_negative_quantity_rejected() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        UpdateStockInput(item_id="MLM0000000001", available_quantity=-1)


def test_update_price_zero_rejected() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        UpdatePriceInput(item_id="MLM0000000001", price=0)


def test_send_message_empty_text_rejected() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        SendMessageInput(pack_id="p1", buyer_id=1, text="")
