"""Cliente unificado mp_isn_mx — Impuesto sobre Nómina estatal MX.

Auto-routing por estado: cada operación enruta al portal estatal correspondiente.

Operaciones soportadas:
1. **`calcular_isn`** (offline, sin tocar portal): cálculo determinístico desde el catálogo.
2. **`listar_estados`** / **`info_estado`**: introspección del catálogo.
3. **`generar_linea_captura`**: requiere acceso al portal (path real con Playwright).
4. **`descargar_declaracion`**: descarga comprobante PDF desde bóveda estatal.

Cache 90 días para declaraciones (datos fiscales no cambian).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.catalogo_isn_estatal import (  # noqa: E402
    CATALOGO_ISN,
    calcular_isn,
    estadisticas_catalogo,
    get_estado_config,
    listar_estados,
)
from shared.errors import (  # noqa: E402
    McpError,
    NotFoundError,
    ValidationError,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402


NAMESPACE = "isn_mx"

# Periodo formato YYYY-MM
PERIODO_REGEX = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

# RFC persona moral: 12 chars, persona física: 13 chars
RFC_REGEX = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$")


class IsnMxClient:
    """Cliente unificado ISN multi-estado."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        if "rfc" in safe and safe["rfc"]:
            safe["rfc_hash"] = Bitacora.hash_sensitive(str(safe.pop("rfc")))
        self._bitacora.log(op, success=True, params_summary=safe)

    # ============================================================
    # Catálogo & cálculo (sin tocar portales)
    # ============================================================

    def calcular(self, nomina_gravable: float, estado: str) -> dict[str, Any]:
        """Calcula ISN del periodo. No requiere acceso al portal."""
        if nomina_gravable < 0:
            raise ValidationError("nomina_gravable debe ser >= 0.")
        try:
            return calcular_isn(nomina_gravable, estado)
        except ValueError as e:
            if "no encontrado" in str(e).lower():
                raise NotFoundError(str(e), {"estado": estado})
            raise ValidationError(str(e))

    def listar(self, solo_validados: bool = False) -> dict[str, Any]:
        """Devuelve lista de estados del catálogo."""
        items = listar_estados(solo_validados=solo_validados)
        return {
            "total": len(items),
            "estados": items,
            "stats": estadisticas_catalogo(),
        }

    def info_estado(self, estado: str) -> dict[str, Any]:
        """Devuelve config completa de un estado."""
        cfg = get_estado_config(estado)
        if cfg is None:
            raise NotFoundError(
                f"Estado '{estado}' no encontrado en catálogo ISN.",
                {"estado": estado, "claves_validas": list(CATALOGO_ISN.keys())},
            )
        return {
            "clave": cfg.estado_clave,
            "nombre": cfg.estado_nombre,
            "portal_url": cfg.portal_url,
            "tasa_pct": cfg.tasa_pct,
            "tasa_rango": cfg.tasa_rango,
            "periodicidad": cfg.periodicidad,
            "dia_vencimiento": cfg.dia_vencimiento,
            "requiere_efirma": cfg.requiere_efirma,
            "requiere_credenciales_estatales": cfg.requiere_credenciales_estatales,
            "captcha_presente": cfg.captcha_presente,
            "selectores_documentados": cfg.selectores,
            "validado": cfg.validado,
            "notas": cfg.notas,
        }

    # ============================================================
    # Operaciones contra portal (path real con Playwright o mock)
    # ============================================================

    def generar_linea_captura(
        self,
        estado: str,
        periodo: str,
        rfc: str,
        nomina_gravable: float,
    ) -> dict[str, Any]:
        """Genera línea de captura para pagar ISN del periodo.

        Modo mock: devuelve línea simulada determinística.
        Modo real: navega al portal estatal y obtiene línea oficial.
        """
        cfg = self._validar_inputs(estado, periodo, rfc, nomina_gravable)

        cache_key = f"linea_{cfg.estado_clave}_{periodo}_{rfc[:8]}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("generar_linea_captura", {
            "estado": cfg.estado_clave, "periodo": periodo, "rfc": rfc,
        })

        calc = calcular_isn(nomina_gravable, cfg.estado_clave)

        if self._is_mock():
            resultado = mark_simulated({
                "estado": cfg.estado_clave,
                "periodo": periodo,
                "rfc": rfc,
                "linea_captura": f"{cfg.estado_clave}{periodo.replace('-','')}{rfc[-3:]}1234567890",
                "monto_a_pagar": calc["isn_a_pagar"],
                "tasa_aplicada_pct": calc["tasa_pct"],
                "vencimiento_dia": calc["vencimiento_dia"],
                "portal_pago": cfg.portal_url,
                "instrucciones": (
                    f"Para pagar ISN de {periodo} en {cfg.estado_nombre}: "
                    f"ingrese a {cfg.portal_url}, capture la línea generada "
                    "y realice el pago referenciado vía portal bancario o ventanilla."
                ),
            })
        else:
            # Path real Playwright
            resultado = self._generar_linea_real(cfg, periodo, rfc, nomina_gravable)

        self._cache.set(cache_key, resultado, ttl_days=90)
        return resultado

    def descargar_declaracion(
        self,
        estado: str,
        periodo: str,
        rfc: str,
    ) -> dict[str, Any]:
        """Descarga el comprobante PDF de la declaración del periodo desde bóveda estatal.

        En modo mock: devuelve path simulado.
        En real: navega al portal y descarga PDF.
        """
        if not PERIODO_REGEX.match(periodo):
            raise ValidationError(f"periodo '{periodo}' inválido. Formato YYYY-MM.")
        if not RFC_REGEX.match(rfc.upper()):
            raise ValidationError(f"RFC '{rfc}' inválido.")
        cfg = get_estado_config(estado)
        if cfg is None:
            raise NotFoundError(f"Estado '{estado}' no en catálogo.")

        cache_key = f"decl_{cfg.estado_clave}_{periodo}_{rfc[:8]}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        self._log("descargar_declaracion", {
            "estado": cfg.estado_clave, "periodo": periodo, "rfc": rfc,
        })

        if self._is_mock():
            resultado = mark_simulated({
                "estado": cfg.estado_clave,
                "periodo": periodo,
                "rfc": rfc,
                "declaracion_pdf_path": (
                    f"/mock/declaraciones/{cfg.estado_clave}_{periodo}_{rfc[:8]}.pdf"
                ),
                "tamano_bytes": 0,
                "fuente": cfg.portal_url,
                "nota": "Mock: en path real bajaría PDF de la bóveda estatal.",
            })
        else:
            resultado = self._descargar_declaracion_real(cfg, periodo, rfc)

        self._cache.set(cache_key, resultado, ttl_days=90)
        return resultado

    # ============================================================
    # Internos
    # ============================================================

    def _is_mock(self) -> bool:
        return is_mock_mode(credential_env_vars=[])

    def _validar_inputs(self, estado, periodo, rfc, nomina_gravable):
        if not PERIODO_REGEX.match(periodo):
            raise ValidationError(f"periodo '{periodo}' inválido. Formato YYYY-MM.")
        if not RFC_REGEX.match(rfc.upper()):
            raise ValidationError(f"RFC '{rfc}' inválido.")
        if nomina_gravable < 0:
            raise ValidationError("nomina_gravable debe ser >= 0.")
        cfg = get_estado_config(estado)
        if cfg is None:
            raise NotFoundError(
                f"Estado '{estado}' no encontrado.",
                {"claves_validas": list(CATALOGO_ISN.keys())},
            )
        return cfg

    def _generar_linea_real(self, cfg, periodo, rfc, nomina_gravable):
        raise McpError(
            f"Path real para {cfg.estado_clave} pendiente. Setear MP_PLAYWRIGHT_PUBLIC=1.",
            {
                "estado": cfg.estado_clave,
                "portal_url": cfg.portal_url,
                "selectores_disponibles": cfg.selectores,
            },
        )

    def _descargar_declaracion_real(self, cfg, periodo, rfc):
        raise McpError(
            f"Descarga real para {cfg.estado_clave} pendiente.",
            {"estado": cfg.estado_clave, "portal_url": cfg.portal_url},
        )
