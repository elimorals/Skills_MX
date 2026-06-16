"""Tests opt-in path real Playwright para mp_imss_patronal."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_imss_patronal import _real_playwright as rp
from shared.errors import UpstreamError


def test_checklist_sin_credenciales_devuelve_todo_false(monkeypatch):
    for var in [
        "IMSS_RFC_PATRONAL",
        "IMSS_NPIE_PATH",
        "IMSS_NPIE_PIN",
        "IMSS_EFIRMA_CERT",
        "IMSS_EFIRMA_KEY",
        "IMSS_EFIRMA_PASS",
        "PLUGINS_MX_PLAYWRIGHT_REAL",
        "PLUGINS_MX_IMSS_PERMITIR_ESCRITURA",
    ]:
        monkeypatch.delenv(var, raising=False)
    c = rp.checklist_credenciales()
    assert c["rfc_patronal_set"] is False
    assert c["tiene_npie"] is False
    assert c["tiene_efirma"] is False
    assert c["playwright_real_flag"] is False
    assert c["permitir_escritura"] is False


def test_checklist_con_efirma_completa(monkeypatch):
    monkeypatch.setenv("IMSS_RFC_PATRONAL", "EMPR010101AAA")
    monkeypatch.setenv("IMSS_EFIRMA_CERT", "/secrets/efirma.cer")
    monkeypatch.setenv("IMSS_EFIRMA_KEY", "/secrets/efirma.key")
    monkeypatch.setenv("IMSS_EFIRMA_PASS", "pass")
    monkeypatch.setenv("PLUGINS_MX_PLAYWRIGHT_REAL", "1")
    c = rp.checklist_credenciales()
    assert c["tiene_efirma"] is True
    assert c["rfc_patronal_set"] is True
    assert c["playwright_real_flag"] is True


def test_respuesta_no_implementada_tiene_checklist_y_url():
    r = rp.respuesta_no_implementada("imss_consultar_sbc")
    assert r["simulated"] is False
    assert r["real_implementado"] is False
    assert r["portal"] == "imss_idse"
    assert r["portal_url"] == "https://idse.imss.gob.mx"
    assert r["tool"] == "imss_consultar_sbc"
    assert "checklist" in r


def test_real_consultar_sbc_devuelve_respuesta_honesta():
    r = rp.real_consultar_sbc("EMPR010101AAA", "12345678901")
    assert r["tool"] == "imss_consultar_sbc"
    assert r["estado"] == "no_implementado"


def test_movimiento_afiliatorio_bloqueado_sin_flag_escritura(monkeypatch):
    monkeypatch.delenv("PLUGINS_MX_IMSS_PERMITIR_ESCRITURA", raising=False)
    with pytest.raises(UpstreamError) as exc:
        rp.real_enviar_movimiento_afiliatorio("EMPR010101AAA", "12345678901", "02")
    assert "PERMITIR_ESCRITURA" in str(exc.value)


def test_movimiento_afiliatorio_con_flag_escritura_devuelve_no_implementado(monkeypatch):
    monkeypatch.setenv("PLUGINS_MX_IMSS_PERMITIR_ESCRITURA", "1")
    r = rp.real_enviar_movimiento_afiliatorio("EMPR010101AAA", "12345678901", "02")
    assert r["tool"] == "imss_enviar_movimiento_afiliatorio"
    assert r["estado"] == "no_implementado"
