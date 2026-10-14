"""Cliente mp_llave_mx — Llave MX (SSO ciudadano) por OAuth2, nunca con contraseña.

Observado en vivo 2026-10-14 (https://www.llave.gob.mx/):
- La portada redirige a `oauthV2.xhtml?client_id=…&redirect_url=…&state=…` (ojo: el
  parámetro es `redirect_url`, no `redirect_uri`). El formulario pide correo/CURP +
  contraseña y trae CAPTCHA.
- No hay `/.well-known/openid-configuration` (404) ni documentación pública del token
  endpoint: el canje de código y su URL se obtienen al dar de alta la aplicación con la
  ATDT. Por eso este MCP solo arma la URL de autorización con un `client_id` registrado
  (LLAVE_MX_CLIENT_ID) y jamás recibe la contraseña del ciudadano.

Datos abiertos: `usuarios_sistema_llave_mx` (ATDT) en datos.gob.mx — altas mensuales por
entidad. El CSV histórico se sirve desde datos.gob.mx; los de 2026 en repodatos.atdt.gob.mx
responden 403 Akamai a clientes no-navegador (2026-10-14).

Mock solo con PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import csv
import io
import os
import re
import secrets
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ConfigError, UpstreamError, ValidationError, handle_httpx_error  # noqa: E402
from shared.http_helpers import default_user_agent  # noqa: E402
from shared.llave_mx import (  # noqa: E402
    CATALOGO_TRAMITES_LLAVE_MX,
    CATEGORIAS_LLAVE_MX,
    URL_LLAVE_MX,
    buscar_tramite,
    tramites_por_categoria,
    tramites_por_dependencia,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "llave_mx"
URL_AUTORIZACION = "https://www.llave.gob.mx/oauthV2.xhtml"
URL_CSV_ADOPCION = ("https://www.datos.gob.mx/dataset/2d0f3a4e-d622-4ff5-ad1f-98532ffc52bc/resource/"
                    "2fa98e88-35ae-4744-bb2f-ea281e146d74/download/nuevos_usuarios.csv")
CURP_RE = re.compile(r"^[A-Z][AEIOU][A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HM][A-Z]{5}[A-Z0-9]\d$")


def _validar_curp(curp: str) -> str:
    curp = (curp or "").strip().upper()
    if not CURP_RE.match(curp):
        raise ValidationError(f"CURP inválida: {curp!r}")
    return curp


class LlaveMXClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def iniciar_oauth(self, redirect_url: str, state: str | None = None) -> dict[str, Any]:
        """URL de autorización para mandar al ciudadano a Llave MX (flujo authorization code)."""
        u = urlparse(redirect_url or "")
        if u.scheme != "https" or not u.netloc:
            raise ValidationError("redirect_url debe ser https y estar registrada con la ATDT")
        client_id = os.environ.get("LLAVE_MX_CLIENT_ID", "").strip()
        if not client_id:
            raise ConfigError(
                "Falta LLAVE_MX_CLIENT_ID: la aplicación debe darse de alta con la ATDT para obtener "
                "client_id, redirect_url autorizada y el endpoint de canje de código."
            )
        state = state or secrets.token_urlsafe(24)
        url = f"{URL_AUTORIZACION}?{urlencode({'client_id': client_id, 'redirect_url': redirect_url, 'state': state})}"
        return {
            "authorization_url": url,
            "state": state,
            "nota": ("Redirige al ciudadano a esta URL; Llave MX regresará a redirect_url con el código. "
                     "Valida que `state` coincida. El canje de código usa el endpoint de tu convenio."),
        }

    def autenticar(self, curp: str, password: str) -> dict[str, Any]:
        """Retirado: un MCP no debe recibir la contraseña del ciudadano (y el login tiene CAPTCHA)."""
        raise ValidationError(
            "Llave MX no se autentica con CURP+contraseña desde un tercero. Usa llave_iniciar_oauth "
            "y deja que el ciudadano inicie sesión en llave.gob.mx."
        )

    def validar_token(self, token: str) -> dict[str, Any]:
        if not token:
            raise ValidationError("token vacío")
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"token": token[:6] + "…", "valido": True})
        raise ConfigError(
            "Llave MX no publica endpoint de introspección; valida el token en tu backend con el "
            "endpoint que te asigne la ATDT."
        )

    def estado_endpoints(self) -> dict[str, Any]:
        """Verifica en vivo que la página de autorización responda (sin credenciales)."""
        try:
            r = httpx.get(URL_LLAVE_MX + "/", timeout=30.0, follow_redirects=True,
                          headers={"User-Agent": default_user_agent("mp_llave_mx", "monitoreo de disponibilidad")})
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        return {
            "url_final": str(r.url).split("?")[0],
            "http_status": r.status_code,
            "redirige_a_oauthV2": "oauthV2.xhtml" in str(r.url),
            "formulario_login": "frmLogin" in r.text,
            "captcha": bool(re.search(r"captcha", r.text, re.I)),
            "simulated": False,
        }

    def estadisticas_adopcion(self, entidad: str | None = None) -> dict[str, Any]:
        """Altas de usuarios Llave MX por entidad y mes (datos abiertos ATDT)."""
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"entidad": entidad, "total_nuevos_usuarios": 1000})
        try:
            r = httpx.get(URL_CSV_ADOPCION, timeout=60.0, follow_redirects=True,
                          headers={"User-Agent": default_user_agent("mp_llave_mx")})
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise handle_httpx_error(e) from e
        filas = list(csv.DictReader(io.StringIO(r.content.decode("utf-8-sig"))))
        if not filas or "nuevos_usuarios" not in filas[0]:
            raise UpstreamError("CSV de adopción Llave MX con formato inesperado", {"url": URL_CSV_ADOPCION})
        if entidad:
            e = entidad.strip().lower()
            filas = [f for f in filas if f["entidad"].lower() == e or f["cve_ent"] == entidad.strip()]
            if not filas:
                raise ValidationError(f"entidad sin datos: {entidad!r}")
        por_mes: dict[str, int] = {}
        for f in filas:
            por_mes[f["fecha"]] = por_mes.get(f["fecha"], 0) + int(f["nuevos_usuarios"])
        return {
            "entidad": entidad or "nacional",
            "total_nuevos_usuarios": sum(por_mes.values()),
            "por_mes": dict(sorted(por_mes.items())),
            "periodo": f"{min(por_mes)} a {max(por_mes)}",
            "fuente": URL_CSV_ADOPCION,
            "licencia": "CC-BY-4.0 (datos.gob.mx, ATDT)",
            "simulated": False,
        }

    def listar_tramites(self, categoria: str | None = None,
                        dependencia: str | None = None) -> dict[str, Any]:
        if categoria:
            items = tramites_por_categoria(categoria)
        elif dependencia:
            items = tramites_por_dependencia(dependencia)
        else:
            items = list(CATALOGO_TRAMITES_LLAVE_MX)
        return {
            "filtro": {"categoria": categoria, "dependencia": dependencia},
            "total": len(items),
            "categorias_disponibles": CATEGORIAS_LLAVE_MX,
            "tramites": [{
                "clave": t.clave, "nombre": t.nombre,
                "dependencia": t.dependencia, "categoria": t.categoria,
                "url_directa": t.url_directa,
            } for t in items],
            "verificado": False,
            "nota": ("Catálogo orientativo de trámites ciudadanos; no verifica cuáles aceptan Llave MX. "
                     "Para eso usa mp_llave_mx_tracker."),
        }

    def detalle_tramite(self, clave: str) -> dict[str, Any]:
        t = buscar_tramite(clave)
        if t is None:
            raise ValidationError(f"trámite no encontrado: {clave}")
        return {
            "clave": t.clave,
            "nombre": t.nombre,
            "dependencia": t.dependencia,
            "categoria": t.categoria,
            "url_directa": t.url_directa,
            "verificado": False,
        }

    def vincular_e_firma(self, curp: str) -> dict[str, Any]:
        """La vinculación la hace el titular en llave.gob.mx: handoff, nunca se suben .key/.cer aquí."""
        curp = _validar_curp(curp)
        return {
            "curp_hash": self._bitacora.hash_sensitive(curp),
            "e_firma_vinculada": None,
            "handoff_humano": True,
            "url": URL_LLAVE_MX,
            "pasos": ["El titular inicia sesión en llave.gob.mx y sigue la opción de su cuenta."],
        }
