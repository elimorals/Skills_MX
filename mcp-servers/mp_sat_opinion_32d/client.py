"""Cliente para SAT Opinión 32-D Pública.

Endpoint: POST https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico/Index
          Content-Type: multipart/form-data
          Body: {Rfc, Curp}

Responses (descubierto con Playwright MCP el 2026-06-14):
  - 200 application/json   → {"MsjeIformativo": "..."}  (no autorizado / no inscrito)
  - 200 text/html          → <div class="alert-success">...</div> + PDF base64
                             O <div class="alert-danger">...</div> + PDF base64

Modo mock por default. Real: setear PLUGINS_MX_MOCK=0.
Cache 7 días — la opinión se recalcula diariamente pero rara vez cambia.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    UpstreamError,
    ValidationError,
    handle_httpx_error,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.sat_opinion_32d import (  # noqa: E402
    CONSULTA_ENDPOINT,
    PORTAL_URL,
    parsear_respuesta_html,
    parsear_respuesta_json,
    validar_estructura_curp,
    validar_estructura_rfc,
)


NAMESPACE = "sat_opinion_32d"
CACHE_TTL_HOURS = 24 * 7  # 7 días — la opinión se recalcula diariamente pero rara vez cambia
TIMEOUT_SECONDS = 20.0


class SatOpinion32DClient:
    """Cliente unificado para consulta pública SAT Opinión 32-D."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    # ============================================================
    # Tool principal
    # ============================================================

    def consultar(
        self,
        rfc: str = "",
        curp: str = "",
        incluir_pdf: bool = True,
    ) -> dict[str, Any]:
        """Consulta opinión 32-D pública por RFC o CURP.

        Args:
            rfc: RFC del contribuyente (12 o 13 caracteres). PM o PF.
            curp: CURP del contribuyente (18 caracteres). Solo PF.
                  Si se proporcionan ambos, RFC tiene prioridad.
            incluir_pdf: si False, no devuelve PDF base64 (respuesta más liviana).

        Returns:
            {
              "rfc": str | "",
              "curp": str | "",
              "estado": "positiva" | "negativa" | "no_autorizado" | "no_inscrito" | "error",
              "puede_contratar_con_gobierno": bool,
              "mensaje_oficial": str,
              "pdf_base64": str | None,
              "fecha_consulta": ISO-8601 UTC,
              "fuente": URL del portal,
              "simulated": bool,
            }
        """
        rfc = (rfc or "").strip().upper()
        curp = (curp or "").strip().upper()

        if not rfc and not curp:
            raise ValidationError(
                "Debe proporcionarse RFC o CURP.",
                {"campos": ["rfc", "curp"]},
            )

        if rfc and not validar_estructura_rfc(rfc):
            raise ValidationError(
                f"RFC '{rfc}' tiene estructura inválida.",
                {"rfc": rfc, "esperado": "12 chars PM o 13 chars PF según regex SAT"},
            )

        if curp and not validar_estructura_curp(curp):
            raise ValidationError(
                f"CURP '{curp}' tiene estructura inválida.",
                {"curp": curp, "esperado": "18 chars con estado válido"},
            )

        # Solo el RFC se usa si se proporcionan ambos (consistente con portal SAT)
        identificador = rfc if rfc else curp
        cache_key = f"{rfc}|{curp}"

        cached = self._cache.get(cache_key)
        if cached is not None:
            self._bitacora.log(
                "consultar",
                success=True,
                params_summary={"identificador_hash": self._bitacora.hash_sensitive(identificador), "cache": "hit"},
            )
            return cached

        # Portal público — default a real cuando no hay override
        if is_mock_mode(credential_env_vars=[], default_when_no_creds=False):
            result = self._mock_response(rfc=rfc, curp=curp)
        else:
            result = self._llamar_endpoint(rfc=rfc, curp=curp)

        if not incluir_pdf:
            result = {**result, "pdf_base64": None}

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log(
            "consultar",
            success=True,
            params_summary={
                "identificador_hash": self._bitacora.hash_sensitive(identificador),
                "estado": result.get("estado"),
                "cache": "miss",
            },
        )
        return result

    # ============================================================
    # Tools de conveniencia
    # ============================================================

    def verificar_proveedor(self, rfc: str) -> dict[str, Any]:
        """Verificación binaria para due-diligence B2B/B2G.

        Returns:
            {
              "rfc": str,
              "puede_contratar_con_gobierno": bool,
              "estado": str,
              "advertencias": [...],
              "detalle": {...resultado consultar()...}
            }
        """
        detalle = self.consultar(rfc=rfc, incluir_pdf=False)
        estado = detalle["estado"]
        advertencias = []

        if estado == "positiva":
            puede = True
        elif estado == "negativa":
            puede = False
            advertencias.append(
                "Opinión NEGATIVA: el contribuyente tiene incumplimientos fiscales. "
                "El Art. 32-D CFF impide contratar con gobierno federal. "
                "Riesgo B2B alto — el SAT puede haberlo publicado en lista 69 o 69-B."
            )
        elif estado == "no_autorizado":
            puede = False
            advertencias.append(
                "RFC NO autorizó publicación pública. Pídele al proveedor que active "
                "'Autorizar para hacerse público' en su Buzón Tributario para validar."
            )
        elif estado == "no_inscrito":
            puede = False
            advertencias.append(
                "RFC NO INSCRITO en padrón SAT. Posiblemente erróneo o nunca activado. "
                "Bloqueador absoluto — no firmar contratos."
            )
        else:
            puede = False
            advertencias.append(
                f"Respuesta inesperada del SAT (estado={estado}). Reintentar más tarde."
            )

        return {
            "rfc": rfc.strip().upper(),
            "puede_contratar_con_gobierno": puede,
            "estado": estado,
            "advertencias": advertencias,
            "detalle": detalle,
        }

    # ============================================================
    # HTTP layer
    # ============================================================

    def _llamar_endpoint(self, *, rfc: str, curp: str) -> dict[str, Any]:
        try:
            import httpx
        except ImportError as e:  # pragma: no cover
            raise UpstreamError(
                "httpx no está instalado en el entorno. Instala con `pip install httpx`.",
                {"raw": str(e)},
            )

        url = f"{PORTAL_URL}{CONSULTA_ENDPOINT}"
        files = {
            "Rfc": (None, rfc),
            "Curp": (None, curp),
        }
        headers = {
            # El portal acepta cualquier UA, pero declaramos uno honesto
            "User-Agent": "plugins-mx/mp_sat_opinion_32d (compliance B2B/B2G)",
            "Accept": "*/*",
            "Origin": PORTAL_URL,
            "Referer": f"{PORTAL_URL}/ConsultaPublico",
        }

        # Usa shared helpers: truststore para gov.mx (cadena cert incompleta)
        from shared.http_helpers import build_ssl_verify
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS, follow_redirects=True, verify=build_ssl_verify()) as client:
                resp = client.post(url, files=files, headers=headers)
                resp.raise_for_status()
        except Exception as exc:
            raise handle_httpx_error(exc) from exc

        return self._parsear_respuesta(resp, rfc=rfc, curp=curp)

    def _parsear_respuesta(
        self,
        resp: Any,
        *,
        rfc: str,
        curp: str,
    ) -> dict[str, Any]:
        content_type = (resp.headers.get("content-type") or "").lower()

        if "application/json" in content_type:
            try:
                payload = resp.json()
            except ValueError:
                payload = {"MsjeIformativo": resp.text}
            parsed = parsear_respuesta_json(payload)
        elif "text/html" in content_type:
            parsed = parsear_respuesta_html(resp.text)
        else:
            parsed = {
                "estado": "error",
                "mensaje_oficial": f"Content-Type inesperado: {content_type}",
                "pdf_base64": None,
            }

        return {
            "rfc": rfc,
            "curp": curp,
            "estado": parsed["estado"],
            "puede_contratar_con_gobierno": parsed["estado"] == "positiva",
            "mensaje_oficial": parsed["mensaje_oficial"],
            "pdf_base64": parsed["pdf_base64"],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": f"{PORTAL_URL}{CONSULTA_ENDPOINT}",
            "simulated": False,
        }

    # ============================================================
    # Mock layer (default en dev / CI)
    # ============================================================

    def _mock_response(self, *, rfc: str, curp: str) -> dict[str, Any]:
        """Respuesta simulada determinística basada en el último char del identificador.

        Permite probar todos los caminos en tests sin tocar el SAT:
          - Termina en par (0,2,4,6,8) → positiva
          - Termina en 1,3,5     → no_autorizado
          - Termina en 7,9       → negativa
          - Vacío                → error
        """
        ident = rfc or curp
        if not ident:
            estado, msj = "error", "Sin identificador"
        else:
            last = ident[-1]
            if last in "02468":
                estado, msj = "positiva", "Opinión Positiva. * Información a la fecha de la consulta."
            elif last in "79":
                estado, msj = "negativa", "Opinión Negativa. * Información a la fecha de la consulta."
            else:
                estado, msj = "no_autorizado", "El RFC o CURP consultado no se encuentra autorizado para hacerse público."

        result = {
            "rfc": rfc,
            "curp": curp,
            "estado": estado,
            "puede_contratar_con_gobierno": estado == "positiva",
            "mensaje_oficial": msj,
            "pdf_base64": "JVBERi0xLjQK<<MOCK_PDF>>" if estado in ("positiva", "negativa") else None,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": f"{PORTAL_URL}{CONSULTA_ENDPOINT}",
        }
        return mark_simulated(result)
