"""Tests mp_llave_mx."""
from __future__ import annotations
import os
import sys
from pathlib import Path
import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))

TEST_PWD = "x" * 8  # synthetic only — secret-scan compliant


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("PLUGINS_MX_MOCK", "1")
    monkeypatch.setenv("PLUGINS_MX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("PLUGINS_MX_BITACORA_DIR", str(tmp_path / "bita"))


def test_autenticar_ok():
    from mp_llave_mx.client import LlaveMXClient
    c = LlaveMXClient()
    r = c.autenticar(curp="HEGJ900101HDFRRN09", password=TEST_PWD)
    assert r["ok"] is True
    assert len(r["token_sso"]) == 48


def test_autenticar_password_corto():
    from mp_llave_mx.client import LlaveMXClient
    from shared.errors import ValidationError
    c = LlaveMXClient()
    with pytest.raises(ValidationError):
        c.autenticar(curp="HEGJ900101HDFRRN09", password="x")


def test_validar_token_ok():
    from mp_llave_mx.client import LlaveMXClient
    c = LlaveMXClient()
    r = c.validar_token(token="a" * 48)
    assert r["valido"] is True


def test_validar_token_corto():
    from mp_llave_mx.client import LlaveMXClient
    from shared.errors import ValidationError
    c = LlaveMXClient()
    with pytest.raises(ValidationError):
        c.validar_token(token="x")


def test_listar_tramites_categoria_fiscal():
    from mp_llave_mx.client import LlaveMXClient
    c = LlaveMXClient()
    r = c.listar_tramites(categoria="fiscal")
    assert r["total"] >= 3


def test_listar_tramites_dependencia_imss():
    from mp_llave_mx.client import LlaveMXClient
    c = LlaveMXClient()
    r = c.listar_tramites(dependencia="IMSS")
    assert r["total"] >= 1


def test_detalle_tramite_existente():
    from mp_llave_mx.client import LlaveMXClient
    c = LlaveMXClient()
    r = c.detalle_tramite(clave="curp_consulta")
    assert r["dependencia"] == "RENAPO"


def test_detalle_tramite_inexistente():
    from mp_llave_mx.client import LlaveMXClient
    from shared.errors import ValidationError
    c = LlaveMXClient()
    with pytest.raises(ValidationError):
        c.detalle_tramite(clave="inexistente")


def test_vincular_e_firma():
    from mp_llave_mx.client import LlaveMXClient
    c = LlaveMXClient()
    r = c.vincular_e_firma(curp="HEGJ900101HDFRRN09")
    assert r["e_firma_vinculada"] is True
