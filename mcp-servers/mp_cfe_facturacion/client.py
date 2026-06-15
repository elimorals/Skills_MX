"""Cliente mp_cfe_facturacion — Playwright + human-in-loop para CAPTCHA.

CFE Mi Espacio requiere: usuario + password + CAPTCHA. NO existe API pública.
La única forma de automatizar es:
  1. Playwright HEADED (no headless) — abre el browser para que el humano vea el CAPTCHA
  2. Humano resuelve el CAPTCHA manualmente, presiona login
  3. Script captura cookies de sesión y las cachea (TTL 30 min — vida típica)
  4. Llamadas subsecuentes usan las cookies cacheadas → sin re-login

3 modos:
  - mock (default): respuestas determinísticas
  - human_loop (PLUGINS_MX_CFE_LIVE=1): Playwright headed, humano resuelve CAPTCHA
  - api_session (PLUGINS_MX_CFE_COOKIES=<json>): re-usa cookies inyectadas

Universo: 42M usuarios CFE. Caso de uso típico:
  - Hogares: descargar recibo mensual + tracking de consumo
  - PyMEs: facturación mensual + detección de anomalías
  - Property managers: 5-20 inmuebles, conciliación
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import (  # noqa: E402
    ConfigError,
    McpError,
    UpstreamError,
    ValidationError,
)
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "cfe_fact"
CRED_VARS = ["CFE_RPU", "CFE_PASSWORD"]
SESSION_TTL_MINUTES = 30  # CFE Mi Espacio expira sesión a los 10-30 min de inactividad
LIVE_ENV_FLAG = "PLUGINS_MX_CFE_LIVE"

# Validado Playwright MCP 2026-06-13:
URL_CFE_MIESPACIO_LOGIN = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Login.aspx"
URL_CFE_MIESPACIO_HOME = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Default.aspx"
URL_CFE_MIESPACIO_FACTURA = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/Pagar.aspx"
URL_CFE_MIESPACIO_CONSUMO = "https://app.cfe.mx/Aplicaciones/CCFE/MiEspacio/HistorialConsumo.aspx"

SELECTORES_CFE_LOGIN = {
    "usuario": "input[name='ctl00$MainContent$txtUsuario']",
    "password": "input[name='ctl00$MainContent$txtPassword']",
    "captcha": "input[name='ctl00$MainContent$txtCaptcha']",
    "submit": "input[name='ctl00$MainContent$btnIngresar']",
    "captcha_img": "img[id*='Captcha']",
}
# Re-confirmado 2026-06-15 vía Playwright. ASP.NET WebForms con __VIEWSTATE +
# __EVENTVALIDATION ocultos; CAPTCHA alfanumérico de imagen (no reCAPTCHA).
# Ver docs/discovery-portales-2026-06-15.md.

# RPU = Registro Permanente Único (identificador de servicio CFE)
# Formato: 12 dígitos típicamente (no estricto — algunos servicios viejos pueden ser menos)
RPU_PATTERN = re.compile(r"^\d{6,16}$")


def validar_rpu(rpu: str) -> str:
    """Valida RPU del servicio CFE."""
    rpu = (rpu or "").strip().replace(" ", "").replace("-", "")
    if not RPU_PATTERN.match(rpu):
        raise ValidationError(
            f"RPU '{rpu}' inválido. Debe ser 6-16 dígitos numéricos.",
            {"rpu_recibido": rpu, "esperado": "6-16 dígitos"},
        )
    return rpu


class CfeFactClient:
    """Cliente CFE Mi Espacio con session caching y human-in-loop."""

    def __init__(
        self,
        bitacora: Bitacora | None = None,
        cache: FileCache | None = None,
    ) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self.cache = cache or FileCache(NAMESPACE)

    def _is_mock(self) -> bool:
        """CFE necesita credenciales — usa default_when_no_creds=True (mock)."""
        return is_mock_mode(CRED_VARS, default_when_no_creds=True)

    # ============================================================
    # Tools
    # ============================================================

    def descargar_factura_mes(
        self,
        rpu: str,
        periodo: str = "",
    ) -> dict[str, Any]:
        """Descarga el recibo CFE del mes en curso o de un periodo específico.

        Args:
            rpu: Registro Permanente Único (12 dígitos).
            periodo: opcional "YYYY-MM" (mes a descargar). Default: último mes.

        Returns:
            {
              "rpu": str,
              "periodo": str,
              "monto_total": float,
              "consumo_kwh": int,
              "vencimiento": str,
              "pdf_base64": str | None,
              "estatus": "PAGADA" | "PENDIENTE" | "VENCIDA",
              "session_used": "cached" | "fresh_login" | "mock",
              "simulated": bool,
            }
        """
        rpu = validar_rpu(rpu)
        if periodo and not re.match(r"^\d{4}-\d{2}$", periodo):
            raise ValidationError(f"Periodo debe ser YYYY-MM, recibido: {periodo}")

        self.bitacora.log(
            "descargar_factura_mes",
            success=True,
            params_summary={
                "rpu_hash": self.bitacora.hash_sensitive(rpu),
                "periodo": periodo or "ultimo",
            },
        )

        if self._is_mock():
            return self._mock_factura(rpu, periodo)
        return self._real_factura(rpu, periodo)

    def consumo_historico(
        self,
        rpu: str,
        meses: int = 12,
    ) -> dict[str, Any]:
        """Consulta el histórico de consumo (kWh) por mes.

        Args:
            rpu: Registro Permanente Único.
            meses: cantidad de meses históricos a regresar (1-24).

        Returns:
            {
              "rpu": str,
              "meses_solicitados": int,
              "consumo_kwh_por_mes": [{"mes": "2026-04", "kwh": 245, "monto": 612.50}, ...],
              "promedio_kwh_mensual": float,
              "tendencia": "ESTABLE" | "AUMENTO" | "DISMINUCION",
              "anomalia_detectada": bool,
              "session_used": str,
              "simulated": bool,
            }
        """
        rpu = validar_rpu(rpu)
        if not 1 <= meses <= 24:
            raise ValidationError(f"meses debe estar entre 1 y 24, recibido: {meses}")

        self.bitacora.log(
            "consumo_historico",
            success=True,
            params_summary={
                "rpu_hash": self.bitacora.hash_sensitive(rpu),
                "meses": meses,
            },
        )

        if self._is_mock():
            return self._mock_consumo(rpu, meses)
        return self._real_consumo(rpu, meses)

    def validar_session(self, rpu: str) -> dict[str, Any]:
        """Verifica si hay una sesión válida cacheada para este RPU.

        Útil para que el caller decida si ejecutar human-in-loop o reusar cookies.

        Returns:
            {
              "rpu": str,
              "session_cached": bool,
              "expires_at": ISO-8601 | None,
              "minutes_until_expiry": int,
            }
        """
        rpu = validar_rpu(rpu)
        session_key = f"session:{rpu}"
        cached = self.cache.get(session_key)
        if cached is None:
            return {
                "rpu": rpu,
                "session_cached": False,
                "expires_at": None,
                "minutes_until_expiry": 0,
            }
        expires_at = cached.get("expires_at", "")
        try:
            exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            mins = max(0, int((exp_dt - now).total_seconds() / 60))
        except Exception:
            mins = 0
        return {
            "rpu": rpu,
            "session_cached": mins > 0,
            "expires_at": expires_at,
            "minutes_until_expiry": mins,
        }

    # ============================================================
    # Real path (Playwright + human-in-loop)
    # ============================================================

    def _real_factura(self, rpu: str, periodo: str) -> dict[str, Any]:
        """Path real — requiere PLUGINS_MX_CFE_LIVE + credenciales en env."""
        cookies = self._get_or_create_session(rpu)
        if not cookies:
            raise UpstreamError(
                "No fue posible obtener sesión CFE. Verifica CFE_RPU + CFE_PASSWORD "
                "y que el humano completó el CAPTCHA durante el flow.",
                {"hint": "Setea PLUGINS_MX_CFE_LIVE=1 para activar Playwright headed."},
            )
        # En v1 el browser captura cookies — el scraping específico de Pagar.aspx
        # / HistorialConsumo.aspx queda como extension point.
        raise McpError(
            "descargar_factura_mes path real requiere implementación del scraper "
            "de Pagar.aspx — placeholder en v1. Mock funciona normal.",
            {"siguiente_paso": "implementar parser HTML de la página de factura"},
        )

    def _real_consumo(self, rpu: str, meses: int) -> dict[str, Any]:
        cookies = self._get_or_create_session(rpu)
        if not cookies:
            raise UpstreamError("No fue posible obtener sesión CFE.")
        raise McpError(
            "consumo_historico path real requiere parser HistorialConsumo.aspx — placeholder.",
        )

    def _get_or_create_session(self, rpu: str) -> Optional[list[dict]]:
        """Obtiene cookies de sesión cacheadas o lanza human-in-loop para crear."""
        session_key = f"session:{rpu}"
        cached = self.cache.get(session_key)
        if cached and self._session_aun_viva(cached):
            return cached.get("cookies")

        # Path human-in-loop con Playwright headed
        try:
            from shared.playwright_session import PortalSession  # noqa
        except ImportError as e:
            raise ConfigError(
                "Playwright no disponible. Instala: pip install playwright && playwright install chromium",
                {"raw": str(e)},
            ) from e

        password = os.environ.get("CFE_PASSWORD", "")
        if not password:
            raise ConfigError(
                "CFE_PASSWORD no está en env. Para path real CFE necesitas: "
                "CFE_RPU + CFE_PASSWORD + PLUGINS_MX_CFE_LIVE=1.",
                {"env_vars_requeridas": CRED_VARS},
            )

        cookies = self._human_in_loop_login(rpu, password)
        if cookies:
            self.cache.set(
                session_key,
                {
                    "cookies": cookies,
                    "rpu": rpu,
                    "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=SESSION_TTL_MINUTES)).isoformat(),
                },
                ttl_hours=SESSION_TTL_MINUTES / 60.0,
            )
        return cookies

    def _human_in_loop_login(self, rpu: str, password: str) -> Optional[list[dict]]:
        """Lanza Playwright HEADED para que humano resuelva CAPTCHA + login.

        Flujo:
          1. Abre Chromium headed con CFE Mi Espacio Login.
          2. Pre-llena usuario (RPU) y password.
          3. PAUSA — espera input del humano (manual CAPTCHA + click submit).
          4. Verifica que la URL post-login sea /Default.aspx (sesión válida).
          5. Captura cookies del contexto.

        NOTA v1: este método está skeleton — la pausa requiere un mecanismo
        de notificación (signal, file, env var) que no puede ser bloqueante
        infinito en un MCP server. Producción usar: input() local + browser
        headed visible al usuario.
        """
        raise McpError(
            "Human-in-loop login para CFE está en skeleton (v1). "
            "Para implementar: lanzar Playwright headed via subprocess, "
            "esperar marker file (ej. ~/.cfe_login_complete) creado por el humano, "
            "luego extraer cookies. Por ahora, set PLUGINS_MX_MOCK=1 (default) o "
            "implementar el handler humano completo.",
            {"reference": "shared/playwright_session.py + CFE_RPU + CFE_PASSWORD"},
        )

    def _session_aun_viva(self, cached: dict) -> bool:
        try:
            exp = datetime.fromisoformat(cached["expires_at"].replace("Z", "+00:00"))
            return exp > datetime.now(timezone.utc)
        except Exception:
            return False

    # ============================================================
    # Mock layer
    # ============================================================

    def _mock_factura(self, rpu: str, periodo: str) -> dict[str, Any]:
        periodo = periodo or datetime.now(timezone.utc).strftime("%Y-%m")
        # Determinístico por último char del RPU
        last = rpu[-1]
        kwh = 200 + int(last) * 30
        monto = round(kwh * 2.85, 2)
        estatus_map = {"0": "PAGADA", "1": "PENDIENTE", "2": "PAGADA", "3": "VENCIDA"}
        estatus = estatus_map.get(last, "PAGADA")
        return mark_simulated({
            "rpu": rpu,
            "periodo": periodo,
            "monto_total": monto,
            "consumo_kwh": kwh,
            "vencimiento": "2026-08-15",
            "pdf_base64": "JVBERi0xLjQK<<MOCK_PDF>>",
            "estatus": estatus,
            "tarifa": "01" if int(last) < 5 else "DAC",
            "session_used": "mock",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": URL_CFE_MIESPACIO_LOGIN,
        })

    def _mock_consumo(self, rpu: str, meses: int) -> dict[str, Any]:
        last = rpu[-1]
        base = 200 + int(last) * 30
        meses_data = []
        suma = 0
        now = datetime.now(timezone.utc)
        for i in range(meses):
            kwh = base + ((i * 7) % 80) - 40  # variación pseudo-aleatoria
            kwh = max(50, kwh)
            mes = (now.year - (i // 12), (now.month - i - 1) % 12 + 1)
            meses_data.append({
                "mes": f"{mes[0]}-{mes[1]:02d}",
                "kwh": kwh,
                "monto": round(kwh * 2.85, 2),
            })
            suma += kwh
        promedio = round(suma / meses, 1) if meses else 0
        # Tendencia: comparar primer vs último mes
        primer = meses_data[-1]["kwh"] if meses_data else 0
        ultimo = meses_data[0]["kwh"] if meses_data else 0
        delta_pct = ((ultimo - primer) / max(primer, 1)) * 100
        if delta_pct > 25:
            tendencia = "AUMENTO"
        elif delta_pct < -25:
            tendencia = "DISMINUCION"
        else:
            tendencia = "ESTABLE"
        anomalia = any(m["kwh"] > promedio * 1.5 for m in meses_data)
        return mark_simulated({
            "rpu": rpu,
            "meses_solicitados": meses,
            "consumo_kwh_por_mes": meses_data,
            "promedio_kwh_mensual": promedio,
            "tendencia": tendencia,
            "anomalia_detectada": anomalia,
            "session_used": "mock",
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": URL_CFE_MIESPACIO_LOGIN,
        })
