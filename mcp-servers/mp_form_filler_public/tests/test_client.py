"""Tests mp_form_filler_public."""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent.parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import pytest

from mp_form_filler_public.client import (
    FORMULARIOS_PUBLICOS,
    FormFillerPublicClient,
    _validar_campo,
)
from shared.errors import ValidationError


class TestValidarCampo:
    def test_rfc_valido(self):
        ok, _ = _validar_campo("ABC010101AAA", "RFC_RE")
        assert ok is True

    def test_rfc_invalido(self):
        ok, msg = _validar_campo("ABC", "RFC_RE")
        assert ok is False
        assert msg is not None

    def test_curp_valida(self):
        ok, _ = _validar_campo("MOMM900101HDFRRR05", "CURP_RE")
        assert ok is True

    def test_telefono_10_digitos(self):
        ok, _ = _validar_campo("5512345678", "TEL_RE")
        assert ok is True

    def test_telefono_9_digitos_falla(self):
        ok, _ = _validar_campo("551234567", "TEL_RE")
        assert ok is False

    def test_campo_vacio_falla(self):
        ok, msg = _validar_campo("", "RFC_RE")
        assert ok is False
        assert msg == "Campo vacío"


class TestListar:
    def setup_method(self):
        self.c = FormFillerPublicClient()

    def test_listar_todos(self):
        r = self.c.listar_formularios()
        assert r["total"] == len(FORMULARIOS_PUBLICOS)

    def test_filtrar_sin_captcha(self):
        r = self.c.listar_formularios(sin_captcha=True)
        for f in r["formularios"]:
            assert f["tiene_captcha"] is False

    def test_metadatos_completos(self):
        r = self.c.listar_formularios()
        for f in r["formularios"]:
            assert "campos_requeridos" in f
            assert "tipo_resultado" in f


class TestValidarInputs:
    def setup_method(self):
        self.c = FormFillerPublicClient()

    def test_rfc_consulta_ok(self):
        r = self.c.validar_inputs("sat_rfc_consulta", {"rfc": "ABC010101AAA"})
        assert r["valido"] is True

    def test_rfc_consulta_falta_campo(self):
        r = self.c.validar_inputs("sat_rfc_consulta", {})
        assert r["valido"] is False
        assert any(e["campo"] == "rfc" for e in r["errores"])

    def test_repep_telefono_invalido(self):
        r = self.c.validar_inputs("repep_consulta", {"telefono": "abc"})
        assert r["valido"] is False

    def test_clave_inexistente_falla(self):
        with pytest.raises(ValidationError):
            self.c.validar_inputs("xx", {"rfc": "ABC010101AAA"})


class TestLlenar:
    def setup_method(self):
        self.c = FormFillerPublicClient()

    def test_mock_marca_captcha_para_rfc(self, monkeypatch):
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        r = self.c.llenar("sat_rfc_consulta", {"rfc": "ABC010101AAA"})
        assert r["simulated"] is True
        assert r["requiere_intervencion_humana"] is True
        assert r["captcha_tipo_detectado"] == "imagen"

    def test_mock_repse_sin_captcha(self, monkeypatch):
        monkeypatch.delenv("MP_PLAYWRIGHT_PUBLIC", raising=False)
        r = self.c.llenar("repse_consulta", {"rfc": "ABC010101AAA"})
        assert r["simulated"] is True
        assert r["requiere_intervencion_humana"] is False

    def test_preflight_falla_antes_de_llenar(self):
        with pytest.raises(ValidationError):
            self.c.llenar("sat_rfc_consulta", {"rfc": "MAL"})

    def test_clave_inexistente_falla(self):
        with pytest.raises(ValidationError):
            self.c.llenar("inexistente", {"rfc": "ABC010101AAA"})
