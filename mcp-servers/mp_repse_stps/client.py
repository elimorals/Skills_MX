"""Cliente unificado para consulta REPSE STPS.

3 modos de consulta:
1. **Por razón social** (fuzzy search): devuelve todas las coincidencias.
2. **Por número de registro** (exacto): devuelve detalle completo.
3. **Verificar proveedor** (compuesto): tool de alto nivel para compliance B2B.

Cache 30 días — el padrón cambia raramente (altas/bajas/renovaciones).

Modo mock por default. Real: setear MP_PLAYWRIGHT_PUBLIC=1.
"""

from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, NotFoundError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.repse_stps import (  # noqa: E402
    URL_REPSE_APP,
    normalizar_razon_social,
    parsear_aviso_registro,
    parsear_entidad_municipio,
)


NAMESPACE = "repse_stps"

# Número de registro REPSE: 6 dígitos numéricos típicamente
REPSE_REGISTRO_REGEX = re.compile(r"^\d{4,7}$")


class RepseStpsClient:
    """Cliente unificado REPSE STPS."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    # ============================================================
    # Tools principales
    # ============================================================

    def consultar_por_razon_social(
        self,
        razon_social: str,
        limite: int = 20,
    ) -> dict[str, Any]:
        """Búsqueda fuzzy por nombre o razón social.

        Args:
            razon_social: nombre o razón social (mín 3 chars)
            limite: máx resultados a devolver

        Returns:
            {
              "razon_social_buscada": str,
              "encontrados": [{razon_social, numero_registro}],
              "total": int,
              "url_consultado": URL_REPSE_APP,
              "simulated": bool
            }
        """
        if not razon_social or len(razon_social.strip()) < 3:
            raise ValidationError(
                "razon_social debe tener al menos 3 caracteres para búsqueda."
            )
        if limite < 1 or limite > 100:
            raise ValidationError("limite debe estar entre 1 y 100.")

        razon_norm = normalizar_razon_social(razon_social)
        cache_key = f"search_{razon_norm[:60].replace(' ', '_')}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("consultar_por_razon_social", {"razon": razon_norm[:50]})

        resultado = self._consultar_busqueda(razon_norm, limite)
        self._cache.set(cache_key, resultado, ttl_days=30)
        return resultado

    def consultar_por_numero_registro(
        self,
        numero_registro: str,
    ) -> dict[str, Any]:
        """Consulta detalle por número de registro REPSE exacto.

        Returns:
            {
              "numero_registro": str,
              "folio": str,
              "razon_social": str,
              "entidad": str,
              "municipio": str,
              "aviso_registro": str,
              "fecha_aviso": str,
              "vigencia": str,
              "vigente": bool,
              "servicios": [...],
              "url_consultado": URL_REPSE_APP,
              "simulated": bool
            }
        """
        if not REPSE_REGISTRO_REGEX.match(numero_registro):
            raise ValidationError(
                f"Número de registro '{numero_registro}' inválido. "
                "Debe ser 4-7 dígitos numéricos (ej. '669356')."
            )

        cache_key = f"detalle_{numero_registro}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("consultar_por_numero_registro", {"numero": numero_registro})

        resultado = self._consultar_detalle(numero_registro)
        self._cache.set(cache_key, resultado, ttl_days=30)
        return resultado

    def verificar_proveedor(
        self,
        razon_social: str,
        numero_registro: Optional[str] = None,
    ) -> dict[str, Any]:
        """Tool de alto nivel para compliance B2B.

        Si el proveedor está en REPSE y vigente, validas que NO te haces responsable
        solidario por Art. 15 LFT al contratarlo.

        Returns:
            {
              "razon_social": str,
              "registrado": bool,
              "vigente": bool,
              "puede_contratar_servicios_especializados": bool,
              "advertencias": [...],
              "detalle": {...},
              "url_consultado": URL_REPSE_APP
            }

        Reglas:
        - Si NO está registrado → puede_contratar=False (NO subcontrata legalmente)
        - Si registrado pero vencido → puede_contratar=False (debe renovar)
        - Si registrado y vigente → puede_contratar=True
        """
        advertencias = []

        if numero_registro:
            try:
                detalle = self.consultar_por_numero_registro(numero_registro)
            except (ValidationError, NotFoundError) as e:
                return {
                    "razon_social": razon_social,
                    "registrado": False,
                    "vigente": False,
                    "puede_contratar_servicios_especializados": False,
                    "advertencias": [f"Número de registro inválido o no encontrado: {e}"],
                    "url_consultado": URL_REPSE_APP,
                }
        else:
            busqueda = self.consultar_por_razon_social(razon_social, limite=5)
            if not busqueda["encontrados"]:
                return {
                    "razon_social": razon_social,
                    "registrado": False,
                    "vigente": False,
                    "puede_contratar_servicios_especializados": False,
                    "advertencias": [
                        "Razón social no aparece en REPSE. "
                        "NO puede prestar servicios especializados (Art. 15 LFT). "
                        "Contratar lo convertiría en responsable solidario laboral y fiscal."
                    ],
                    "url_consultado": URL_REPSE_APP,
                }
            # Tomar primer match (más relevante)
            primer = busqueda["encontrados"][0]
            try:
                detalle = self.consultar_por_numero_registro(primer["numero_registro"])
            except Exception as e:
                return {
                    "razon_social": razon_social,
                    "registrado": True,
                    "vigente": False,
                    "puede_contratar_servicios_especializados": False,
                    "advertencias": [f"Error obteniendo detalle: {e}"],
                    "url_consultado": URL_REPSE_APP,
                }

        vigente = self._es_vigente(detalle.get("vigencia"))
        if not vigente:
            advertencias.append(
                f"Registro REPSE NO vigente (venció {detalle.get('vigencia')}). "
                "El proveedor debe renovar antes de prestar servicios."
            )

        return {
            "razon_social": detalle.get("razon_social"),
            "numero_registro": detalle.get("numero_registro"),
            "registrado": True,
            "vigente": vigente,
            "puede_contratar_servicios_especializados": vigente,
            "advertencias": advertencias,
            "detalle": detalle,
            "url_consultado": URL_REPSE_APP,
        }

    # ============================================================
    # Backend: real vs mock
    # ============================================================

    def _is_mock(self) -> bool:
        return is_mock_mode(credential_env_vars=[])

    @staticmethod
    def _es_vigente(vigencia_str: Optional[str]) -> bool:
        if not vigencia_str:
            return False
        try:
            vig = datetime.strptime(vigencia_str, "%Y-%m-%d").date()
            return vig >= date.today()
        except (ValueError, TypeError):
            return False

    def _consultar_busqueda(self, razon_norm: str, limite: int) -> dict[str, Any]:
        """Busca empresas por razón social. Mock por default."""
        if self._is_mock():
            return mark_simulated({
                "razon_social_buscada": razon_norm,
                "encontrados": [
                    {
                        "razon_social": f"{razon_norm} CORPORATIVO SA DE CV",
                        "numero_registro": "669356",
                    },
                    {
                        "razon_social": f"{razon_norm} PROFESSIONAL SA DE CV",
                        "numero_registro": "651051",
                    },
                ][:limite],
                "total": min(2, limite),
                "url_consultado": URL_REPSE_APP,
            })

        # Path real con Playwright
        return self._consultar_busqueda_real(razon_norm, limite)

    def _consultar_detalle(self, numero_registro: str) -> dict[str, Any]:
        if self._is_mock():
            return mark_simulated({
                "numero_registro": numero_registro,
                "folio": "2334",
                "razon_social": "EMPRESA MOCK SA DE CV",
                "entidad": "Ciudad de México",
                "municipio": "Benito Juárez",
                "aviso_registro": "AR6169",
                "fecha_aviso": "2024-06-12",
                "vigencia": "2027-06-12",
                "vigente": True,
                "servicios": [
                    "Prestación de servicios especializados en administración de negocios.",
                    "Gestión y planeación financiera, economía, tesorería.",
                    "Servicios especializados de consultoría y auditoría.",
                ],
                "url_consultado": URL_REPSE_APP,
            })

        return self._consultar_detalle_real(numero_registro)

    def _consultar_busqueda_real(self, razon_norm: str, limite: int) -> dict[str, Any]:
        raise McpError(
            "Playwright real no instalado. Setear MP_PLAYWRIGHT_PUBLIC=1 + "
            "instalar playwright. URL: " + URL_REPSE_APP,
            {"hint": "ver shared/repse_stps.py para selectores DOM validados"},
        )

    def _consultar_detalle_real(self, numero_registro: str) -> dict[str, Any]:
        raise McpError(
            "Playwright real no instalado. Setear MP_PLAYWRIGHT_PUBLIC=1.",
            {"hint": "ver shared/repse_stps.py para selectores DOM validados"},
        )
