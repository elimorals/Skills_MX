"""Tests del login FIEL httpx al portal SAT (shared/sat_portal_fiel.py).

Fixtures `loginda_*.html`: páginas reales del NIDP del SAT capturadas el
2026-10-14 sin credenciales (autosubmit + reto certform). La variante `_error`
es la misma página con `var error = 'Certificado Revocado'`, que es como el SAT
re-renderiza el reto al rechazar una e.firma (validado en vivo con un
certificado autofirmado: "El certificado no se encuentra disponible…").
Los pasos posteriores al login (SAML, JSF, JSON del PDF) usan HTML sintético
que sigue el flujo de satcfdi; solo el test live los valida de verdad.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from urllib.parse import parse_qs

import httpx
import pytest
import respx

pytest.importorskip("cryptography")

from cryptography.hazmat.primitives import hashes  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import padding  # noqa: E402

from mp_sat_portal.efirma_loader import EfirmaLoader  # noqa: E402
from mp_sat_portal.tests.test_efirma_loader import _gen_efirma_test  # noqa: E402
from shared.errors import AuthError, UpstreamError  # noqa: E402
from shared import sat_portal_fiel as fiel  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "sat_portal_fiel"
AUTOSUBMIT = (FIX / "loginda_autosubmit.html").read_text()
CERTFORM = (FIX / "loginda_certform.html").read_text()
CERTFORM_ERROR = (FIX / "loginda_certform_error.html").read_text()
PDF = b"%PDF-1.4\n%fake\n"
LOGINDA = "https://loginda.siat.sat.gob.mx"
LOGIN_SIAT = "https://login.siat.sat.gob.mx"


def _form(action: str, **inputs: str) -> str:
    campos = "".join(f'<input type="hidden" name="{k}" value="{v}"/>' for k, v in inputs.items())
    return f'<html><body><form method="POST" action="{action}">{campos}</form></body></html>'


@pytest.fixture
def efirma(tmp_path: Path) -> EfirmaLoader:
    c, k, p = _gen_efirma_test(tmp_path)
    return EfirmaLoader(cert_path=c, key_path=k, password=p)


@pytest.fixture
def sesion(efirma):
    with respx.mock(assert_all_called=False) as router:
        s = fiel.SatFielSession(efirma, client=httpx.Client(follow_redirects=True))
        yield s, router
        s.client.close()


def _mock_reto(router, base: str, entrada: str, respuesta_login: str):
    """GET entrada → autosubmit → certform → respuesta. Devuelve la ruta del POST del token."""
    router.get(entrada).respond(200, html=AUTOSUBMIT)
    router.post(url__startswith=f"{base}/nidp/app/login?id=fiel&sid=0").mock(
        side_effect=lambda req: httpx.Response(
            200, html=respuesta_login if b"token=" in req.content else CERTFORM
        )
    )


# ---------- unidades ----------


def test_get_form_autosubmit_real():
    action, data = fiel.get_form(AUTOSUBMIT, f"{LOGINDA}/nidp/app/login?id=fiel")
    assert action == f"{LOGINDA}/nidp/app/login?id=fiel&sid=0&option=credential&sid=0"
    assert data == {}


def test_get_form_certform_real():
    action, data = fiel.get_form(CERTFORM, f"{LOGINDA}/x?id=fiel", form_id="certform")
    assert action == f"{LOGINDA}/x?id=fiel"  # sin action → misma URL
    assert data["credentialsRequired"] == "CERT"
    assert len(data["guid"]) > 20
    assert "token" not in data  # input sin value se omite


def test_generar_token_firma_verificable(efirma):
    token = fiel.generar_token(efirma, "GUID123")
    co_b64, firma_b64b64 = base64.b64decode(token).split(b"#")
    co = base64.b64decode(co_b64)
    meta = efirma.metadata()
    assert co.decode() == f"GUID123|{meta.rfc}|{meta.numero_certificado}"
    firma = base64.b64decode(base64.b64decode(firma_b64b64))
    from cryptography import x509

    cert = x509.load_der_x509_certificate(efirma.cert_path.read_bytes())
    cert.public_key().verify(firma, co, padding.PKCS1v15(), hashes.SHA1())


# ---------- login ----------


def test_login_portal_ok_envia_token_y_fert(sesion, efirma):
    s, router = sesion
    _mock_reto(router, LOGINDA, fiel.URL_LOGIN_PORTAL, "<html>Bienvenido</html>")
    s.login_portal()
    post_token = [c.request for c in router.calls if b"token=" in c.request.content][0]
    body = parse_qs(post_token.content.decode())
    assert body["credentialsRequired"] == ["CERT"]
    assert body["fert"][0] == efirma.metadata().not_after.strftime("%y%m%d%H%M%SZ")
    assert body["token"][0]


def test_login_portal_rechazo_levanta_auth_error(sesion):
    s, router = sesion
    _mock_reto(router, LOGINDA, fiel.URL_LOGIN_PORTAL, CERTFORM_ERROR)
    with pytest.raises(AuthError) as e:
        s.login_portal()
    assert e.value.details["motivo"] == "Certificado Revocado"


def test_login_portal_http_500_es_upstream(sesion):
    s, router = sesion
    router.get(fiel.URL_LOGIN_PORTAL).respond(503)
    with pytest.raises(UpstreamError):
        s.login_portal()


def test_login_sin_certform_es_upstream(sesion):
    s, router = sesion
    _mock_reto(router, LOGINDA, fiel.URL_LOGIN_PORTAL, "x")
    router.post(url__startswith=f"{LOGINDA}/nidp/app/login?id=fiel&sid=0").respond(200, html="<html>cambió</html>")
    with pytest.raises(UpstreamError):
        s.login_portal()


# ---------- flujos ----------


def test_descargar_constancia(sesion):
    s, router = sesion
    _mock_reto(router, LOGIN_SIAT, fiel.URL_LOGIN_CONSTANCIA, "<html>ok</html>")
    jsf = "https://rfcampc.siat.sat.gob.mx/PTSC/IdcSiat/autc/ReimpresionTramite/ConsultaTramite.jsf"
    router.get(fiel.URL_CONSTANCIA_BROKER).respond(200, html=_form(f"{LOGIN_SIAT}/nidp/saml2/sso", SAMLRequest="r"))
    router.post(f"{LOGIN_SIAT}/nidp/saml2/sso").respond(
        200, html=_form("https://rfcampc.siat.sat.gob.mx/saml2/sp/acs/post", SAMLResponse="s")
    )
    router.post("https://rfcampc.siat.sat.gob.mx/saml2/sp/acs/post").respond(
        200, html=_form(jsf, **{"javax.faces.ViewState": "VS1"})
    )
    jsf_route = router.post(jsf).respond(200, text="<partial-response/>")
    router.get(fiel.URL_CONSTANCIA_PDF).respond(200, content=PDF)
    assert s.descargar_constancia() == PDF
    assert b"javax.faces.ViewState=VS1" in jsf_route.calls[0].request.content


def test_descargar_constancia_no_pdf_es_upstream(sesion):
    s, router = sesion
    _mock_reto(router, LOGIN_SIAT, fiel.URL_LOGIN_CONSTANCIA, "<html>ok</html>")
    router.get(fiel.URL_CONSTANCIA_BROKER).respond(200, html="<html>sin form</html>")
    router.get(fiel.URL_CONSTANCIA_PDF).respond(200, html="<html>Sesión expirada</html>")
    with pytest.raises(UpstreamError):
        s.descargar_constancia()


def test_descargar_opinion_32d(sesion, efirma):
    s, router = sesion
    ciec = f"{LOGINDA}/nidp/app/login?id=ciec&sid=0&option=credential&sid=0"
    router.get(fiel.URL_32D_ENTRADA).respond(200, html=_form(ciec))
    authz = f"{LOGINDA}/nidp/oauth/nam/authz?client_id=x"
    router.post(ciec.replace("id=ciec", "id=fiel")).mock(
        side_effect=lambda req: httpx.Response(
            200,
            html=f"<script>top.location.href='{authz}'</script>" if b"token=" in req.content else CERTFORM,
        )
    )
    router.get(authz).respond(200, html=_form("https://ptsc32d.clouda.sat.gob.mx/oauth2/callback", code="c"))
    router.post("https://ptsc32d.clouda.sat.gob.mx/oauth2/callback").respond(200, html="<html>app</html>")
    pdf_route = router.post(fiel.URL_32D_PDF).respond(
        200, json={"ContenidoBase64": base64.b64encode(PDF).decode()}
    )
    assert s.descargar_opinion_32d() == PDF
    enviado = json.loads(pdf_route.calls[0].request.content)
    assert enviado["rfc"] == efirma.metadata().rfc and enviado["tipoReporte"] == "32D"


def test_descargar_opinion_sin_pdf_es_upstream(sesion):
    s, router = sesion
    router.get(fiel.URL_32D_ENTRADA).respond(200, html="<html>ya autenticado</html>")
    router.post(fiel.URL_32D_PDF).respond(200, json={"ContenidoBase64": None})
    with pytest.raises(UpstreamError):
        s.descargar_opinion_32d()


def test_consultar_rfc(sesion):
    s, router = sesion
    cfdiau = "https://cfdiau.sat.gob.mx"
    router.get(url__regex=r"^https://portal\.facturaelectronica\.sat\.gob\.mx/?$").respond(
        200, html=_form(f"{cfdiau}/nidp/wsfed/ep?id=SATUPCFDiCon&sid=0&option=credential&sid=0")
    )
    router.post(url__startswith=f"{cfdiau}/nidp/app/login?id=SATx509Custom").mock(
        side_effect=lambda req: httpx.Response(
            200, html=_form(f"{cfdiau}/wsfed1", a="1") if b"token=" in req.content else CERTFORM
        )
    )
    router.post(f"{cfdiau}/wsfed1").respond(200, html=_form(f"{fiel.URL_FACTURA}/", wresult="x"))
    router.post(f"{fiel.URL_FACTURA}/").respond(
        200, html='<input name="__RequestVerificationToken" type="hidden" value="RVT9" />'
    )
    existe = router.post(f"{fiel.URL_FACTURA}/Clientes/ExisteLrfc").respond(
        200, json={"exitoso": True, "resultado": True}
    )
    router.get(url__startswith=f"{fiel.URL_FACTURA}/Clientes/ValidaLco").respond(
        200, json=json.dumps({"rfc": "AAA010101AAA", "regimenes": ["601"]})
    )
    r = s.consultar_rfc("aaa010101aaa")
    assert r == {"existe_en_lco": True, "lco": {"rfc": "AAA010101AAA", "regimenes": ["601"]}}
    assert existe.calls[0].request.headers["__RequestVerificationToken"] == "RVT9"
