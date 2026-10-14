"""La reputación sale de GET /users/{id} → seller_reputation (developers.mercadolibre.com.ar/en_us/sellers-reputation)."""

from __future__ import annotations

import respx

from mp_mercado_libre.client import ML_BASE_URL, MercadoLibreClient


@respx.mock
async def test_reputacion_desde_users(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    c = MercadoLibreClient(app_id="a", secret="s", refresh_token="r")

    async def _headers():
        return {"Authorization": "Bearer AT"}

    monkeypatch.setattr(c, "_auth_headers", _headers)
    respx.get(f"{ML_BASE_URL}/users/123").respond(
        200, json={"id": 123, "seller_reputation": {"level_id": "5_green", "power_seller_status": "gold"}}
    )
    r = await c.get_seller_reputation(123)
    assert r["level_id"] == "5_green" and r["seller_id"] == 123 and r["simulated"] is False
