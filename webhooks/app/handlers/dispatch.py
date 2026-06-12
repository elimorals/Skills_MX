"""Dispatcher central: source → handler.

Único punto de mapping para encontrar el handler de cada source.
"""

from __future__ import annotations

from typing import Any

from . import HandlerFn
from . import (
    banxico_cep,
    calendly,
    condusef,
    conekta,
    facturama,
    github,
    imss_buzon,
    mercadolibre,
    mercadopago,
    meta_whatsapp,
    stripe,
    typeform,
)


_HANDLERS: dict[str, HandlerFn] = {
    "stripe": stripe.handle,
    "mercadopago": mercadopago.handle,
    "conekta": conekta.handle,
    "facturama": facturama.handle,
    "meta_whatsapp": meta_whatsapp.handle,
    "github": github.handle,
    "calendly": calendly.handle,
    "typeform": typeform.handle,
    "mercadolibre": mercadolibre.handle,
    "banxico_cep": banxico_cep.handle,
    "imss_buzon": imss_buzon.handle,
    "condusef": condusef.handle,
}


SUPPORTED_SOURCES: tuple[str, ...] = tuple(_HANDLERS.keys())


def get_handler(source: str) -> HandlerFn | None:
    return _HANDLERS.get(source)


def dispatch(source: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    handler = get_handler(source)
    if handler is None:
        return {
            "action": "no_handler",
            "target_workflow": None,
            "notes": [f"source desconocido: {source}"],
            "raw_event_type": None,
        }
    return handler(payload, headers)
