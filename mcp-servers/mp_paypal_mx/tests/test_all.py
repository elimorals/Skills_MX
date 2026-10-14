import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import httpx
import pytest
import respx

from mp_paypal_mx.client import PaypalMxClient
from shared.errors import AuthError, NotFoundError, ValidationError

API = "https://api-m.paypal.com"
# Ejemplos tomados de https://developer.paypal.com/api/transaction-search/v1/
TX = {
    "transaction_info": {
        "transaction_id": "5TY05013RG002845M",
        "transaction_event_code": "T0006",
        "transaction_initiation_date": "2026-10-01T23:46:13+0000",
        "transaction_amount": {"currency_code": "MXN", "value": "465.00"},
        "fee_amount": {"currency_code": "MXN", "value": "-19.87"},
        "transaction_status": "S",
    }
}
_LIVE = {v: os.environ.get(v, "") for v in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET")}


@pytest.fixture
def creds(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    monkeypatch.delenv("PLUGINS_MX_MOCK", raising=False)
    monkeypatch.delenv("PAYPAL_ENV", raising=False)
    monkeypatch.setenv("PAYPAL_CLIENT_ID", "cid")
    monkeypatch.setenv("PAYPAL_CLIENT_SECRET", "sec")


def _token(router):
    return router.post(f"{API}/v1/oauth2/token").respond(200, json={"access_token": "T", "expires_in": 32400})


@respx.mock
def test_listar_transacciones_real(creds):
    tok = _token(respx)
    ruta = respx.get(f"{API}/v1/reporting/transactions").respond(
        200, json={"transaction_details": [TX], "total_items": 1, "total_pages": 1, "page": 1}
    )
    r = PaypalMxClient().listar_transacciones("2026-10-01", "2026-10-14")
    assert r["simulated"] is False and r["total_items"] == 1
    q = ruta.calls.last.request.url.params
    assert q["start_date"] == "2026-10-01T00:00:00Z" and q["end_date"] == "2026-10-14T00:00:00Z"
    assert ruta.calls.last.request.headers["Authorization"] == "Bearer T"
    assert tok.calls.last.request.headers["Authorization"].startswith("Basic ")


def test_rango_mayor_a_31_dias_falla(creds):
    with pytest.raises(ValidationError):
        PaypalMxClient().listar_transacciones("2026-08-01", "2026-10-01")


@respx.mock
def test_consultar_transaccion_no_encontrada(creds):
    _token(respx)
    respx.get(f"{API}/v1/reporting/transactions").respond(200, json={"transaction_details": []})
    with pytest.raises(NotFoundError):
        PaypalMxClient().consultar_transaccion("5TY05013RG002845M")


@respx.mock
def test_consultar_transaccion_ok(creds):
    _token(respx)
    respx.get(f"{API}/v1/reporting/transactions").respond(200, json={"transaction_details": [TX]})
    r = PaypalMxClient().consultar_transaccion("5TY05013RG002845M")
    assert r["transaction_info"]["transaction_amount"]["value"] == "465.00"


@respx.mock
def test_balance_y_token_reutilizado(creds):
    tok = _token(respx)
    respx.get(f"{API}/v1/reporting/balances").respond(
        200, json={"balances": [{"currency": "MXN", "primary": True, "total_balance": {"currency_code": "MXN", "value": "1000.00"}}]}
    )
    c = PaypalMxClient()
    c.balance("mxn")
    r = c.balance()
    assert r["balances"][0]["currency"] == "MXN" and tok.call_count == 1


@respx.mock
def test_credenciales_invalidas_es_auth_error(creds):
    respx.post(f"{API}/v1/oauth2/token").respond(401, json={"error": "invalid_client"})
    with pytest.raises(AuthError):
        PaypalMxClient().balance()


def test_sin_credenciales_es_simulado(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_AUDIT_DIR", str(tmp_path))
    for v in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET", "PLUGINS_MX_MOCK"):
        monkeypatch.delenv(v, raising=False)
    assert PaypalMxClient().balance()["simulated"] is True


def test_sandbox_por_env(monkeypatch):
    monkeypatch.setenv("PAYPAL_ENV", "sandbox")
    assert PaypalMxClient(http=httpx.Client()).base_url.endswith("sandbox.paypal.com")


@pytest.mark.live
def test_live_balance_sandbox(monkeypatch):
    if not all(_LIVE.values()):
        pytest.skip("requiere PAYPAL_CLIENT_ID y PAYPAL_CLIENT_SECRET de una app sandbox")
    for k, v in _LIVE.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("PAYPAL_ENV", os.environ.get("PAYPAL_ENV", "sandbox"))
    assert PaypalMxClient().balance()["simulated"] is False
