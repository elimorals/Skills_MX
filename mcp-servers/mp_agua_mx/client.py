"""Cliente unificado consulta agua municipal/estatal MX.

3 modos:
  - mock (default): respuestas determinísticas por organismo
  - playwright (PLUGINS_MX_AGUA_LIVE=1): scraping real por organismo
  - cached: TTL 14 días (los recibos cambian bimestral)

Auto-routing: el cliente recibe (organismo, cuenta) y decide:
  1. Si el organismo está consultable=True → path real
  2. Si no → mock con advertencia "no implementado aún"
"""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.agua_mx import (  # noqa: E402
    CATALOGO_AGUA,
    OrganismoAgua,
    buscar_organismo,
    buscar_por_estado,
    estadisticas,
    listar_organismos,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import NotFoundError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.playwright_session import should_use_real_browser  # noqa: E402


NAMESPACE = "agua_mx"
CACHE_TTL_HOURS = 24 * 14  # 14 días — recibos bimestrales


class AguaMxClient:
    """Cliente unificado consulta agua."""

    LIVE_ENV_FLAG = "PLUGINS_MX_AGUA_LIVE"

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

    def consultar_adeudo(
        self,
        organismo: str,
        cuenta: str,
    ) -> dict[str, Any]:
        """Consulta el adeudo actual de una cuenta de agua.

        Args:
            organismo: clave del operador (sacmex, siapa, sadm, etc.).
            cuenta: identificador del usuario (cuenta, contrato, NIS según organismo).

        Returns:
            {
              "organismo": str,
              "cuenta": str,
              "consultado": bool,
              "adeudo_mxn": float,
              "vencimiento": str,
              "estatus": "AL DIA" | "PENDIENTE" | "VENCIDO" | "NO_IMPLEMENTADO",
              "ultimo_pago": str | None,
              "consumo_m3": float | None,
              "advertencias": [str],
              "fuente": URL,
              "fecha_consulta": ISO-8601,
              "simulated": bool,
            }
        """
        org = buscar_organismo(organismo)
        if not org:
            raise NotFoundError(
                f"Organismo '{organismo}' no está en el catálogo. "
                f"Usa agua_listar_organismos() para ver opciones.",
                {"organismo_solicitado": organismo},
            )

        cuenta = cuenta.strip()
        if not cuenta:
            raise ValidationError("Cuenta requerida.")
        if not re.match(org.identificador_regex, cuenta):
            raise ValidationError(
                f"Cuenta '{cuenta}' no matchea formato esperado de {org.clave}: {org.identificador_regex}.",
                {"organismo": org.clave, "esperado": org.identificador_regex},
            )

        cache_key = f"{org.clave}:{cuenta}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if not org.consultable:
            result = self._not_implemented(org, cuenta)
        elif is_mock_mode(credential_env_vars=[], default_when_no_creds=True):
            # Default mock para agua (path real requiere Playwright + portal-specific)
            result = self._mock(org, cuenta)
        else:
            # Path real — pendiente implementación específica por organismo
            result = self._real_pending(org, cuenta)

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log(
            "consultar_adeudo",
            success=True,
            params_summary={
                "organismo": org.clave,
                "cuenta_hash": self._bitacora.hash_sensitive(cuenta),
                "consultado": result.get("consultado"),
            },
        )
        return result

    def listar_organismos(self, solo_consultables: bool = False) -> dict[str, Any]:
        """Lista organismos en el catálogo."""
        orgs = listar_organismos(solo_consultables=solo_consultables)
        return {
            "total": len(orgs),
            "filtro_solo_consultables": solo_consultables,
            "organismos": [
                {
                    "clave": o.clave,
                    "nombre": o.nombre_completo,
                    "estado": o.estado,
                    "municipios_cubre": o.municipio,
                    "url_portal": o.url_portal,
                    "identificador": o.identificador_label,
                    "metodo": o.metodo,
                    "frecuencia": o.frecuencia_recibo,
                    "poblacion_aprox": o.poblacion_aprox,
                    "consultable": o.consultable,
                }
                for o in orgs
            ],
        }

    def buscar_por_estado(self, estado: str) -> dict[str, Any]:
        """Lista organismos que cubren un estado mexicano."""
        orgs = buscar_por_estado(estado)
        return {
            "estado_buscado": estado.upper(),
            "encontrados": len(orgs),
            "organismos": [{"clave": o.clave, "nombre": o.nombre_completo, "consultable": o.consultable} for o in orgs],
        }

    def estadisticas_catalogo(self) -> dict[str, Any]:
        """Stats agregadas del catálogo."""
        return estadisticas()

    # ============================================================
    # Internal paths
    # ============================================================

    def _not_implemented(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        return {
            "organismo": org.clave,
            "cuenta": cuenta,
            "consultado": False,
            "adeudo_mxn": 0.0,
            "vencimiento": "",
            "estatus": "NO_IMPLEMENTADO",
            "ultimo_pago": None,
            "consumo_m3": None,
            "advertencias": [
                f"⚠️ El organismo {org.clave} ({org.nombre_completo}) está en el catálogo "
                f"pero el scraper Playwright NO está implementado aún. {org.notas}"
            ],
            "fuente": org.url_portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }

    def _real_pending(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        """Placeholder para path real Playwright — implementación por-organismo."""
        # En v1 ningún organismo tiene scraper implementado todavía.
        # Estructura lista para que se implemente uno por uno con su portal específico.
        return self._not_implemented(org, cuenta)

    def _mock(self, org: OrganismoAgua, cuenta: str) -> dict[str, Any]:
        """Mock determinístico por suffix de cuenta."""
        last = cuenta[-1] if cuenta else "0"
        if last in "02468":
            adeudo = 0.0
            estatus = "AL DIA"
            consumo = 15.5
        elif last in "13579":
            # Adeudo proporcional al digit
            adeudo = float(int(last) * 145.30 + 122.50)
            estatus = "PENDIENTE" if int(last) <= 5 else "VENCIDO"
            consumo = 22.7
        else:
            adeudo = 0.0
            estatus = "AL DIA"
            consumo = 18.2

        return mark_simulated({
            "organismo": org.clave,
            "cuenta": cuenta,
            "consultado": True,
            "adeudo_mxn": adeudo,
            "vencimiento": "2026-08-15",
            "estatus": estatus,
            "ultimo_pago": "2026-04-22",
            "consumo_m3": consumo,
            "advertencias": [] if estatus == "AL DIA" else [
                f"Adeudo {estatus.lower()} — pagar antes del 15-ago para evitar recargos."
            ],
            "fuente": org.url_portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })
