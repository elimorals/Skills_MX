"""Cliente unificado mp_isn_mx — Impuesto sobre Nómina estatal MX.

Auto-routing por estado: cada operación enruta al portal estatal correspondiente.

Operaciones soportadas:
1. **`calcular_isn`** (offline, sin tocar portal): cálculo determinístico desde el catálogo.
2. **`listar_estados`** / **`info_estado`**: introspección del catálogo.
3. **`generar_linea_captura`**: requiere sesión del contribuyente → ConfigError (mock solo con PLUGINS_MX_MOCK=1).
4. **`descargar_declaracion`**: igual que 3.

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
    ConfigError,
    NotFoundError,
    ValidationError,
)
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import mock_forzado  # noqa: E402


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
            "fuente_tasa": cfg.fuente_tasa,
            "confianza_tasa": cfg.confianza_tasa,
            "tasa_no_calculable": cfg.tasa_no_calculable or None,
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

        Con PLUGINS_MX_MOCK=1: línea simulada determinística.
        Real: ConfigError (requiere sesión del contribuyente en el portal).
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

        Con PLUGINS_MX_MOCK=1: path simulado. Real: ConfigError (requiere sesión).
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
        return mock_forzado()

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

    # Línea de captura y declaraciones viven tras el login estatal (REC/usuario o
    # e.firma) del contribuyente: grupo G del plan, no se automatizan aquí.
    def _generar_linea_real(self, cfg, periodo, rfc, nomina_gravable):
        raise ConfigError(
            f"Generar línea de captura ISN en {cfg.estado_nombre} requiere sesión del contribuyente "
            "en el portal estatal; no está automatizado. Genérala en el portal.",
            {"estado": cfg.estado_clave, "portal_url": cfg.portal_url, "estado_impl": "requiere_login"},
        )

    def _descargar_declaracion_real(self, cfg, periodo, rfc):
        raise ConfigError(
            f"Descargar declaraciones ISN de {cfg.estado_nombre} requiere sesión del contribuyente; "
            "no está automatizado.",
            {"estado": cfg.estado_clave, "portal_url": cfg.portal_url, "estado_impl": "requiere_login"},
        )
