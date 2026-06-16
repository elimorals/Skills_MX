"""Tests opt-in path real Playwright para mp_infonavit_patronal."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from mp_infonavit_patronal import _real_playwright as rp


def test_checklist_sin_credenciales(monkeypatch):
    for v in [
        "INFONAVIT_RFC_PATRONAL",
        "INFONAVIT_USUARIO",
        "INFONAVIT_PASSWORD",
        "INFONAVIT_EFIRMA_CERT",
        "PLUGINS_MX_PLAYWRIGHT_REAL",
    ]:
        monkeypatch.delenv(v, raising=False)
    c = rp.checklist_credenciales()
    assert all(v is False for v in c.values())


def test_checklist_con_usuario_password(monkeypatch):
    monkeypatch.setenv("INFONAVIT_RFC_PATRONAL", "EMPR010101AAA")
    monkeypatch.setenv("INFONAVIT_USUARIO", "responsable")
    monkeypatch.setenv("INFONAVIT_PASSWORD", "x" * 8)
    c = rp.checklist_credenciales()
    assert c["tiene_usuario_password"] is True
    assert c["rfc_patronal_set"] is True


def test_respuesta_tiene_url_y_checklist():
    r = rp.respuesta_no_implementada("infonavit_descargar_emis")
    assert r["portal"] == "infonavit_empresarial"
    assert r["portal_url"] == "https://empresarios.infonavit.org.mx"
    assert r["tool"] == "infonavit_descargar_emis"
    assert "checklist" in r


def test_real_descargar_emis():
    r = rp.real_descargar_emis("EMPR010101AAA", 4, 2026)
    assert r["tool"] == "infonavit_descargar_emis"
    assert r["estado"] == "no_implementado"
