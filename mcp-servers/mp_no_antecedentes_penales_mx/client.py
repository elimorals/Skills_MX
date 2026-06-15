"""Cliente Constancia No Antecedentes Penales — CDMX + EdoMex.

NOTA importante:
  Este MCP NO emite la constancia (eso requiere SSO Llave CDMX del propio
  ciudadano y pago $77-87 MXN). El MCP **verifica autenticidad** de una
  constancia ya emitida (por folio + CURP) o **consulta su vigencia**.

  Caso de uso típico RRHH:
    1. Candidato sube su constancia (PDF) durante el proceso de contratación.
    2. Empresa extrae folio + CURP del PDF.
    3. MCP verifica que la constancia es real y está vigente.

3 modos:
  - mock (default)
  - playwright (PLUGINS_MX_NOANT_LIVE=1): browser headless contra el verificador
  - 2captcha (futuro): si EdoMex agrega captcha (hoy 2026-06-15 no tiene)

Cache 30 días (las constancias vigentes raramente cambian de status).
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
from shared.errors import UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.no_antecedentes import (  # noqa: E402
    CDMX_PORTAL_URL,
    EDOMEX_PORTAL_URL,
    ConstanciaNoAntecedentes,
    Entidad,
    EstadoCarta,
    validar_curp,
    validar_entidad,
    validar_folio,
)


NAMESPACE = "no_antecedentes"
CACHE_TTL_HOURS = 24 * 30  # 30 días


class NoAntecedentesClient:
    """Cliente unificado constancias no antecedentes — CDMX + EdoMex."""

    LIVE_ENV_FLAG = "PLUGINS_MX_NOANT_LIVE"

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    # ============================================================
    # Tools
    # ============================================================

    def verificar_constancia(
        self,
        curp: str,
        folio: str,
        entidad: str,
    ) -> dict[str, Any]:
        """Verifica que una constancia (curp+folio) sea auténtica y vigente.

        Args:
            curp: CURP del titular.
            folio: folio de la constancia.
            entidad: "cdmx" o "edomex".

        Returns:
            {
              "curp": str,
              "entidad": "cdmx" | "edomex",
              "estado": "VIGENTE" | "EXPIRADA" | "ANULADA" | "NO_ENCONTRADA",
              "folio": str,
              "fecha_emision": str,
              "fecha_vigencia": str,
              "tiene_antecedentes": bool,
              "es_apta_para_contratacion": bool,
              "advertencias": [str],
              "simulated": bool,
            }
        """
        curp = validar_curp(curp)
        folio = validar_folio(folio)
        ent: Entidad = validar_entidad(entidad)

        cache_key = f"{ent}:{curp}:{folio}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if is_mock_mode(credential_env_vars=[], default_when_no_creds=True):
            # Default mock para este MCP — el path real requiere Playwright + login Llave
            result = self._mock(curp, folio, ent)
        else:
            result = self._real(curp, folio, ent)

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log(
            "verificar_constancia",
            success=True,
            params_summary={
                "curp_hash": self._bitacora.hash_sensitive(curp),
                "folio_hash": self._bitacora.hash_sensitive(folio),
                "entidad": ent,
                "estado": result.get("estado"),
            },
        )
        return result

    def verificar_apto_contratacion(self, curp: str, folio: str, entidad: str) -> dict[str, Any]:
        """Decisión binaria para RRHH: ¿este candidato es apto para contratar?

        Returns:
            {
              "curp": str,
              "apto_para_contratacion": bool,
              "razon": str,
              "advertencias": [str],
              "detalle": {...verificar_constancia...}
            }
        """
        detalle = self.verificar_constancia(curp, folio, entidad)
        apto = detalle.get("es_apta_para_contratacion", False)

        if detalle["estado"] == "NO_ENCONTRADA":
            razon = "Constancia NO encontrada en el registro — folio falso o inexistente."
        elif detalle["estado"] == "EXPIRADA":
            razon = f"Constancia EXPIRADA (vigencia: {detalle.get('fecha_vigencia')}). Solicitar nueva."
        elif detalle["estado"] == "ANULADA":
            razon = "Constancia ANULADA por la autoridad. NO contratar — investigar."
        elif detalle.get("tiene_antecedentes"):
            razon = "Persona TIENE antecedentes penales registrados. Decisión final a RRHH/legal."
        else:
            razon = "Constancia vigente y sin antecedentes — apto."

        return {
            "curp": curp,
            "apto_para_contratacion": apto,
            "razon": razon,
            "advertencias": detalle.get("advertencias", []),
            "detalle": detalle,
        }

    # ============================================================
    # Real path (placeholder — requiere Playwright + Llave SSO o EdoMex pública)
    # ============================================================

    def _real(self, curp: str, folio: str, ent: Entidad) -> dict[str, Any]:
        # EdoMex tiene endpoint público sin SSO; CDMX requiere Llave.
        # En v1 dejamos el path real como UpstreamError + mensaje de cómo activarlo.
        raise UpstreamError(
            f"Path real para entidad={ent} no implementado en v1.\n"
            "  CDMX: requiere Playwright + login con Llave CDMX SSO del titular.\n"
            "  EdoMex: pendiente captura del endpoint público de verificación.\n"
            "Usa PLUGINS_MX_MOCK=1 (default) o contribuye el implementación.",
            {"entidad": ent},
        )

    # ============================================================
    # Mock path
    # ============================================================

    def _mock(self, curp: str, folio: str, ent: Entidad) -> dict[str, Any]:
        """Mock determinístico:
          - Folio terminado en par → VIGENTE sin antecedentes
          - Folio terminado en impar → VIGENTE con antecedentes
          - Folio contiene FAKE/INEXIST → NO_ENCONTRADA
          - Folio termina en X → EXPIRADA
          - Folio termina en Z → ANULADA
        """
        last = folio[-1].upper()
        if "FAKE" in folio.upper() or "INEXIST" in folio.upper():
            estado: EstadoCarta = "NO_ENCONTRADA"
            tiene = False
        elif last == "X":
            estado = "EXPIRADA"
            tiene = False
        elif last == "Z":
            estado = "ANULADA"
            tiene = False
        elif last in "13579":
            estado = "VIGENTE"
            tiene = True
        else:
            estado = "VIGENTE"
            tiene = False

        portal = CDMX_PORTAL_URL if ent == "cdmx" else EDOMEX_PORTAL_URL
        c = ConstanciaNoAntecedentes(
            curp=curp,
            entidad=ent,
            estado=estado,
            folio=folio,
            fecha_emision="2026-04-15",
            fecha_vigencia="2026-10-15" if estado != "EXPIRADA" else "2025-12-15",
            tiene_antecedentes=tiene,
        )
        advertencias: list[str] = []
        if estado == "NO_ENCONTRADA":
            advertencias.append("Constancia no encontrada — folio falso o erróneo.")
        elif estado == "EXPIRADA":
            advertencias.append("Constancia vencida — vigencia 6 meses desde emisión.")
        elif tiene:
            advertencias.append(
                "Persona tiene antecedentes penales. La constancia es válida; "
                "decisión de contratación corresponde a RRHH/legal."
            )

        return mark_simulated({
            **c.to_dict(),
            "fuente": portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "advertencias": advertencias,
        })
