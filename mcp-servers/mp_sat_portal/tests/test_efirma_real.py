"""Paths reales con e.firma de SatPortalClient (CSF, vigencia, padrón) + listas 69.

El flujo HTTP del portal se prueba en shared/tests/test_sat_portal_fiel.py; aquí
se sustituye SatFielSession para probar la lógica del cliente. Los tests
`live` usan la e.firma real del coordinador (SAT_RFC, SAT_EFIRMA_*).
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

import httpx
import pytest
import respx

pytest.importorskip("cryptography")

from mp_sat_portal import client as client_mod  # noqa: E402
from mp_sat_portal.client import SatPortalClient  # noqa: E402
from mp_sat_portal.tests.test_efirma_loader import _gen_efirma_test  # noqa: E402
from shared import sat_portal_fiel  # noqa: E402
from shared.errors import AuthError, ConfigError, UpstreamError, ValidationError  # noqa: E402

RFC = "EKU9003173C9"
PDF = b"%PDF-1.4 csf"


@pytest.fixture
def efirma_env(tmp_path: Path, monkeypatch):
    c, k, p = _gen_efirma_test(tmp_path)
    monkeypatch.setenv("SAT_EFIRMA_CERT", str(c))
    monkeypatch.setenv("SAT_EFIRMA_KEY", str(k))
    monkeypatch.setenv("SAT_EFIRMA_PASSWORD", p)
    return c, k, p


class _SesionFalsa:
    rechazo: str | None = None

    def __init__(self, firmante, **kw):
        self.firmante = firmante

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def login_portal(self):
        if self.rechazo:
            raise AuthError("rechazada", {"motivo": self.rechazo})

    def descargar_constancia(self):
        return PDF

    def consultar_rfc(self, rfc):
        return {"existe_en_lco": True, "lco": {"rfc": rfc}}


@pytest.fixture
def sesion_falsa(monkeypatch):
    _SesionFalsa.rechazo = None
    monkeypatch.setattr(sat_portal_fiel, "SatFielSession", _SesionFalsa)
    return _SesionFalsa


def test_csf_real_guarda_pdf_600(efirma_env, sesion_falsa):
    r = SatPortalClient().descargar_csf(RFC)
    assert r["simulated"] is False and r["pdf_bytes"] == len(PDF)
    path = Path(r["pdf_path"])
    assert path.read_bytes() == PDF
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_csf_rfc_ajeno_rechazado(efirma_env, sesion_falsa):
    with pytest.raises(ValidationError):
        SatPortalClient().descargar_csf("XAXX010101000")


def test_csf_sin_llave_es_config_error(monkeypatch, tmp_path):
    monkeypatch.setenv("SAT_EFIRMA_CERT", str(tmp_path / "no.cer"))
    with pytest.raises(ConfigError):
        SatPortalClient().descargar_csf(RFC)


def test_csf_efirma_vencida(tmp_path, monkeypatch, sesion_falsa):
    c, k, p = _gen_efirma_test(tmp_path, valid_days_before=400, valid_days_after=-1)
    monkeypatch.setenv("SAT_EFIRMA_CERT", str(c))
    monkeypatch.setenv("SAT_EFIRMA_KEY", str(k))
    monkeypatch.setenv("SAT_EFIRMA_PASSWORD", p)
    with pytest.raises(AuthError):
        SatPortalClient().descargar_csf(RFC)


def test_verificar_efirma_local_y_portal_ok(efirma_env, sesion_falsa):
    r = SatPortalClient().verificar_efirma_vigente(RFC)
    assert r["simulated"] is False
    assert r["rfc"] == RFC and r["rfc_coincide"] is True
    assert r["llave_corresponde_al_certificado"] is True
    assert r["verificacion_portal"]["aceptada_por_sat"] is True
    assert r["vigente"] is True
    assert r["numero_certificado"]


def test_verificar_efirma_revocada_en_portal(efirma_env, sesion_falsa):
    sesion_falsa.rechazo = "Certificado Revocado"
    r = SatPortalClient().verificar_efirma_vigente(RFC)
    assert r["verificacion_portal"] == {
        "aceptada_por_sat": False,
        "motivo_sat": "Certificado Revocado",
        "url": sat_portal_fiel.URL_LOGIN_PORTAL,
    }
    assert r["vigente"] is False


def test_verificar_efirma_solo_local(efirma_env):
    r = SatPortalClient().verificar_efirma_vigente(RFC, verificar_en_portal=False)
    assert r["verificacion_portal"] is None and r["vigente"] is True


def test_verificar_efirma_password_incorrecto(efirma_env, monkeypatch):
    monkeypatch.setenv("SAT_EFIRMA_PASSWORD", "mala")
    with pytest.raises(ValidationError):
        SatPortalClient().verificar_efirma_vigente(RFC, verificar_en_portal=False)


def test_padron_real_con_efirma(efirma_env, sesion_falsa):
    r = SatPortalClient().consultar_padron("AAA010101AAA")
    assert r["simulated"] is False and r["encontrado"] is True


def test_padron_con_ciec_sin_efirma_da_handoff(monkeypatch):
    monkeypatch.setenv("SAT_CIEC", "x")
    with pytest.raises(ConfigError) as e:
        SatPortalClient().consultar_padron(RFC)
    assert e.value.details["handoff_url"] == client_mod.URL_VALIDA_RFC


@pytest.mark.parametrize("metodo,args", [("descargar_buzon_tributario", (RFC,)), ("descargar_acuse", ("F1",))])
def test_no_implementados_son_error_explicito(efirma_env, metodo, args):
    with pytest.raises(UpstreamError) as e:
        getattr(SatPortalClient(), metodo)(*args)
    assert "handoff_url" in e.value.details


@respx.mock
def test_69b_sin_red_es_error_no_mock():
    respx.get(client_mod.URL_LISTA_69B_DEFINITIVOS).respond(503)
    respx.get(client_mod.URL_LISTA_69B_PRESUNTOS).respond(200, text="RFC,Nombre\n")
    with pytest.raises(UpstreamError):
        SatPortalClient().consultar_69b_efos("AAA010101AAA")


@respx.mock
def test_69_sin_red_es_error_no_mock():
    respx.get(client_mod.URL_LISTA_69_INCUMPLIDOS).mock(side_effect=httpx.ConnectError("x"))
    with pytest.raises(UpstreamError):
        SatPortalClient().consultar_69_incumplidos()


# ---------- live (PLUGINS_MX_LIVE=1) ----------

_LIVE_ENV = ["SAT_RFC", "SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]
# Se capturan al importar: el conftest autouse borra SAT_* antes de cada test.
_ENV_ORIGINAL = {v: os.environ.get(v, "") for v in _LIVE_ENV}


@pytest.fixture
def live_env(monkeypatch):
    faltan = [v for v, val in _ENV_ORIGINAL.items() if not val]
    if faltan:
        pytest.skip(f"faltan {faltan}")
    for v, val in _ENV_ORIGINAL.items():
        monkeypatch.setenv(v, val)
    return _ENV_ORIGINAL["SAT_RFC"].strip().upper()


@pytest.mark.live
def test_live_verificar_efirma(live_env):
    r = SatPortalClient().verificar_efirma_vigente(live_env)
    assert r["llave_corresponde_al_certificado"] is True
    assert r["verificacion_portal"]["aceptada_por_sat"] is True, r["verificacion_portal"]


@pytest.mark.live
def test_live_descargar_csf(live_env):
    r = SatPortalClient().descargar_csf(live_env)
    assert Path(r["pdf_path"]).read_bytes().startswith(b"%PDF")


@pytest.mark.live
def test_live_consultar_padron(live_env):
    r = SatPortalClient().consultar_padron(live_env)
    assert r["encontrado"] is True


@pytest.mark.live
def test_live_69b_lista_publica():
    r = SatPortalClient(http_timeout=120).consultar_69b_efos()
    assert r["simulated"] is False and r["total_registros"] > 1000
