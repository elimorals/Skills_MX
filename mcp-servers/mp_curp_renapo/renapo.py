"""Consulta RENAPO — verificación de existencia en padrón oficial.

⚠ Hoy mismo (2026-06): RENAPO no expone API pública. La consulta oficial
está en https://www.gob.mx/curp/ y requiere CAPTCHA.

Estrategias implementadas:
1. **Modo mock** (default): devuelve respuesta plausible "Vigente" con datos
   derivados de la propia CURP (sexo, fecha, estado). Útil para desarrollo,
   tests y flujos agénticos que solo necesitan "no crashee".

2. **Modo Playwright** (TODO): pendiente de integrar. La estructura está
   reservada para cuando se decida si:
   - usar un servicio CAPTCHA externo (2captcha, anti-captcha)
   - usar un endpoint privado RENAPO si la SRE de algún cliente lo expone
   - asumir intervención humana en el flujo

   Hasta entonces, llamar a `consultar_renapo_via_playwright` en modo real
   devuelve `not_implemented_error` con guía de qué hace falta.

Cache: las consultas RENAPO se cachean 90 días porque los datos del padrón
cambian muy raramente (correcciones, defunciones registradas).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_curp_renapo.catalogos import ESTADOS_CURP  # noqa: E402
from mp_curp_renapo.validacion import (  # noqa: E402
    derivar_estado,
    derivar_fecha_nacimiento,
    derivar_sexo,
    validar_estructura,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, NotFoundError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "curp_renapo_mcp"
CACHE_DIAS = 90


class _NotImplementedError(McpError):
    """Funcionalidad pendiente de integración (Playwright + CAPTCHA)."""

    code = "not_implemented_error"


class RenapoClient:
    """Wrapper sobre la consulta a RENAPO con cache + modo mock."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

        # RENAPO no tiene "credenciales" — el discriminador de mock es:
        # 1. PLUGINS_MX_MOCK=1 fuerza mock
        # 2. PLAYWRIGHT_AVAILABLE no seteado → mock por default (no hay forma
        #    de hacer consulta real sin Playwright)
        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            self._mock_mode = True
        elif os.environ.get("CURP_RENAPO_PLAYWRIGHT") == "1":
            self._mock_mode = False
        else:
            # Default: mock (porque Playwright no está integrado todavía)
            self._mock_mode = True

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    async def consultar(self, curp: str) -> dict[str, Any]:
        """Consulta una CURP en RENAPO. Cache 90 días."""
        # Validación estructural primero — no tiene sentido consultar RENAPO
        # si la CURP ni siquiera pasa el dígito verificador.
        estructura = validar_estructura(curp)
        if not estructura["valido_estructura"]:
            raise ValidationError(
                "CURP inválida estructuralmente — RENAPO va a rechazar la consulta. "
                f"Errores: {'; '.join(estructura['errores'])}"
            )

        curp_norm = estructura["curp_normalizado"]
        cache_key = f"renapo_{curp_norm}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_consulta(curp_norm, estructura)
            self._cache.set(cache_key, response, ttl_hours=24 * CACHE_DIAS)
            self._bitacora.log(
                "consultar_renapo",
                success=True,
                params_summary={
                    "curp_hash": Bitacora.hash_sensitive(curp_norm),
                    "mode": "mock",
                },
            )
            return response

        # Modo real — Playwright todavía no integrado
        raise _NotImplementedError(
            (
                "Consulta RENAPO real (vía Playwright) no está implementada todavía. "
                "Para activar: instalar playwright + integrar bypass de CAPTCHA "
                "(servicio externo tipo 2captcha o intervención humana). "
                "Mientras tanto, usar modo mock (PLUGINS_MX_MOCK=1 o sin "
                "CURP_RENAPO_PLAYWRIGHT=1)."
            ),
            details={"curp_hash": Bitacora.hash_sensitive(curp_norm)},
        )

    async def descargar_constancia(self, curp: str) -> dict[str, Any]:
        """Descarga el PDF de constancia CURP oficial.

        En mock devuelve metadata simulada con path donde estaría el PDF.
        En real, requiere Playwright (no implementado).
        """
        estructura = validar_estructura(curp)
        if not estructura["valido_estructura"]:
            raise ValidationError(
                "CURP inválida estructuralmente — no se puede descargar constancia."
            )

        if self._mock_mode:
            return mark_simulated(
                {
                    "curp": estructura["curp_normalizado"],
                    "constancia_pdf_path": (
                        f"/mock/constancias/{estructura['curp_normalizado']}.pdf"
                    ),
                    "constancia_pdf_bytes": 0,
                    "vigente_al": datetime.now(timezone.utc).isoformat(),
                    "nota": (
                        "Modo mock — no se generó PDF real. En modo Playwright "
                        "habría descargado y persistido el PDF en cache."
                    ),
                }
            )

        raise _NotImplementedError(
            (
                "Descarga de constancia real requiere integración Playwright. "
                "Ver consultar_renapo_via_playwright para guía."
            ),
        )

    # ---------- mock helpers ----------

    @staticmethod
    def _mock_consulta(curp: str, estructura: dict[str, Any]) -> dict[str, Any]:
        """Construye respuesta plausible derivada de la propia CURP."""
        fecha = derivar_fecha_nacimiento(curp)
        sexo = derivar_sexo(curp)
        estado_t = derivar_estado(curp)

        # Heurística determinística para "estado": las CURPs que terminan en
        # 0-3 son "vigente" (90% de los casos reales), 4 = "duplicado", 5+ = vigente
        digito = int(curp[-1])
        if digito == 4:
            estado_renapo = "DUPLICADO"
            estado_descripcion = "CURP duplicada — existe otra persona con esta CURP."
        else:
            estado_renapo = "VIGENTE"
            estado_descripcion = "CURP vigente en padrón RENAPO."

        return mark_simulated(
            {
                "curp": curp,
                "estado_renapo": estado_renapo,
                "estado_descripcion": estado_descripcion,
                "datos_persona": {
                    "fecha_nacimiento": fecha.isoformat() if fecha else None,
                    "sexo": sexo,
                    "entidad_registro": estado_t[1] if estado_t else None,
                    "nacionalidad": "MEXICANA"
                    if estado_t and estado_t[0] != "NE"
                    else "EXTRANJERA",
                },
                "consultado_en": datetime.now(timezone.utc).isoformat(),
                "cache_ttl_dias": CACHE_DIAS,
            }
        )
