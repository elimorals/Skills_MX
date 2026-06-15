"""Cliente mp_telmex_facturacion — mock-first + Playwright real path."""
from __future__ import annotations

import os
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
from shared.errors import McpError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.telmex_portal import (  # noqa: E402
    LIVE_ENV_FLAG,
    SESSION_TTL_HOURS,
    TelmexCredentials,
    URL_MI_TELMEX_FACTURAS,
    URL_MI_TELMEX_LOGIN,
    validar_telefono,
)


NAMESPACE = "telmex_fact"
CRED_VARS = ["TELMEX_TELEFONO", "TELMEX_PASSWORD"]


class TelmexFactClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _is_mock(self) -> bool:
        # Live opt-in requiere flag + ambas credenciales.
        live = os.getenv(LIVE_ENV_FLAG, "").strip() == "1"
        if not live:
            return True
        return is_mock_mode(CRED_VARS, default_when_no_creds=True)

    def _get_credentials(self) -> Optional[TelmexCredentials]:
        tel = os.getenv("TELMEX_TELEFONO", "").strip()
        pwd = os.getenv("TELMEX_PASSWORD", "").strip()
        if not tel or not pwd:
            return None
        try:
            return TelmexCredentials(telefono=tel, password=pwd)
        except ValueError:
            return None

    def descargar_factura_mes(self, telefono: str, periodo: str = "") -> dict[str, Any]:
        """Descarga PDF + XML de la factura del periodo (YYYY-MM)."""
        tel_norm = validar_telefono(telefono)
        cache_key = f"factura:{tel_norm}:{periodo or 'ultimo'}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if self._is_mock():
            result = self._mock_factura(tel_norm, periodo)
        else:
            result = self._real_factura(tel_norm, periodo)

        ttl = 24 * 30 if not periodo else 24 * 365
        self._cache.set(cache_key, result, ttl_hours=ttl)
        self._bitacora.log(
            "descargar_factura_mes",
            success=True,
            params_summary={
                "telefono_hash": self._bitacora.hash_sensitive(tel_norm),
                "periodo": periodo or "ultimo",
                "modo": "mock" if self._is_mock() else "live",
            },
        )
        return result

    def consumo_historico(self, telefono: str, meses: int = 6) -> dict[str, Any]:
        """Histórico de consumos por mes."""
        if not (1 <= meses <= 24):
            raise ValidationError("meses debe estar entre 1 y 24")
        tel_norm = validar_telefono(telefono)
        cache_key = f"consumo:{tel_norm}:{meses}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if self._is_mock():
            result = self._mock_consumo(tel_norm, meses)
        else:
            result = self._real_consumo(tel_norm, meses)

        self._cache.set(cache_key, result, ttl_hours=24)
        self._bitacora.log("consumo_historico", success=True,
                           params_summary={"telefono_hash": self._bitacora.hash_sensitive(tel_norm), "meses": meses})
        return result

    def listar_facturas(self, telefono: str) -> dict[str, Any]:
        """Lista facturas disponibles (últimos 12 meses)."""
        tel_norm = validar_telefono(telefono)
        cache_key = f"lista:{tel_norm}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        if self._is_mock():
            result = self._mock_listado(tel_norm)
        else:
            result = self._real_listado(tel_norm)

        self._cache.set(cache_key, result, ttl_hours=12)
        self._bitacora.log("listar_facturas", success=True,
                           params_summary={"telefono_hash": self._bitacora.hash_sensitive(tel_norm)})
        return result

    # ---- MOCK paths ----
    def _mock_factura(self, telefono: str, periodo: str) -> dict[str, Any]:
        per = periodo or "2026-05"
        last = telefono[-1]
        monto = 389.00 + int(last) * 50
        return mark_simulated({
            "operation": "descargar_factura_mes",
            "telefono": telefono,
            "periodo": per,
            "monto_total_mxn": round(monto, 2),
            "fecha_emision": f"{per}-15",
            "fecha_vencimiento": f"{per}-30",
            "estatus": "PAGADA" if int(last) % 2 == 0 else "PENDIENTE",
            "url_pdf": f"https://miespacio.telmex.com/factura/{telefono}/{per}.pdf",
            "url_xml": f"https://miespacio.telmex.com/factura/{telefono}/{per}.xml",
            "uuid_cfdi": f"XXXX-MOCK-{telefono[-4:]}-{per}",
            "fuente": URL_MI_TELMEX_FACTURAS,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_consumo(self, telefono: str, meses: int) -> dict[str, Any]:
        base = 389.0 + int(telefono[-1]) * 50
        return mark_simulated({
            "operation": "consumo_historico",
            "telefono": telefono,
            "meses": meses,
            "consumos": [
                {"periodo": f"2026-{m:02d}", "monto_mxn": round(base + m * 5.0, 2)}
                for m in range(max(1, 6 - meses + 1), 7)
            ],
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def _mock_listado(self, telefono: str) -> dict[str, Any]:
        return mark_simulated({
            "operation": "listar_facturas",
            "telefono": telefono,
            "facturas_disponibles": [
                {"periodo": f"2026-{m:02d}", "disponible": True} for m in range(1, 7)
            ],
            "fuente": URL_MI_TELMEX_FACTURAS,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    # ---- REAL paths (Playwright) ----
    def _real_factura(self, telefono: str, periodo: str) -> dict[str, Any]:
        creds = self._get_credentials()
        if creds is None:
            raise McpError("Credenciales Telmex ausentes: TELMEX_TELEFONO + TELMEX_PASSWORD requeridas.",
                           {"hint": "Configure variables de entorno."})
        try:
            from shared.playwright_session import PortalSession  # type: ignore
        except ImportError as e:
            raise McpError("Playwright no disponible para path real.", {"hint": str(e)})

        # Esqueleto del flujo Playwright; selectores reales TBD.
        raise McpError(
            "descargar_factura_mes path real (Playwright) requiere verificación de selectores "
            "en miespacio.telmex.com (login + descarga PDF). Activar PLUGINS_MX_TELMEX_LIVE=1 después.",
            {"telefono_hash": self._bitacora.hash_sensitive(telefono), "periodo": periodo or "ultimo",
             "portal": URL_MI_TELMEX_LOGIN},
        )

    def _real_consumo(self, telefono: str, meses: int) -> dict[str, Any]:
        raise McpError("consumo_historico path real pendiente — usar mock por ahora.",
                       {"hint": "Selectores TBD en miespacio.telmex.com/consumo"})

    def _real_listado(self, telefono: str) -> dict[str, Any]:
        raise McpError("listar_facturas path real pendiente — usar mock por ahora.",
                       {"hint": "Selectores TBD en miespacio.telmex.com/factura-electronica"})
