"""Cliente REPUVE — consulta NIV/placa robados.

3 modos:
  - mock (default): respuestas determinísticas por sufijo del NIV/placa.
  - playwright (PLUGINS_MX_REPUVE_LIVE=1): browser real, reCAPTCHA v3 auto.
  - 2captcha (TWOCAPTCHA_API_KEY): solver externo, batch grande (futuro).

NOTA del discovery 2026-06-15: el endpoint backend exacto de REPUVE no
quedó capturado en sesión inicial (Angular timing race). El modo real
queda preparado vía PortalSession; cuando el endpoint exacto se confirme,
solo hay que ajustar `API_URL_PATTERN` en shared/repuve.py.

Cache 7 días — el estatus de robo cambia mensualmente o menos.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402
from shared.playwright_session import (  # noqa: E402
    PlaywrightNotAvailable,
    PortalSession,
    should_use_real_browser,
)
from shared.repuve import (  # noqa: E402
    API_URL_PATTERN,
    PORTAL_URL,
    SEARCH_BUTTON,
    SEARCH_INPUT_NIV,
    SEARCH_INPUT_PLACA,
    VehiculoREPUVE,
    validar_niv,
    validar_placa,
)


NAMESPACE = "repuve"
CACHE_TTL_HOURS = 24 * 7  # 7 días
TIMEOUT_SECONDS = 30.0


class RepuveClient:
    """Cliente unificado REPUVE."""

    LIVE_ENV_FLAG = "PLUGINS_MX_REPUVE_LIVE"

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_niv(self, niv: str) -> dict[str, Any]:
        """Consulta REPUVE por NIV/VIN (17 chars)."""
        niv = validar_niv(niv)
        return self._consultar("niv", niv)

    def consultar_placa(self, placa: str) -> dict[str, Any]:
        """Consulta REPUVE por placa."""
        placa = validar_placa(placa)
        return self._consultar("placa", placa)

    def verificar_robado(self, niv: str = "", placa: str = "") -> dict[str, Any]:
        """Decisión binaria: ¿este vehículo tiene reporte de robo?

        Útil para flujos de:
          - Aseguradoras: rechazar póliza si tiene_reporte_robo
          - Marketplaces: bloquear listing si el VIN aparece robado
          - Movilidad: rechazar socio si el auto está robado

        Returns:
            {
              "identificador_buscado": str (niv o placa),
              "tipo": "niv" | "placa",
              "consultado": bool,
              "tiene_reporte_robo": bool,
              "advertencias": [str],
              "detalle": {...}
            }
        """
        if not niv and not placa:
            raise ValidationError(
                "Debe proporcionarse NIV o placa.",
                {"campos": ["niv", "placa"]},
            )
        if niv:
            tipo = "niv"
            detalle = self.consultar_niv(niv)
            identificador = validar_niv(niv)
        else:
            tipo = "placa"
            detalle = self.consultar_placa(placa)
            identificador = validar_placa(placa)

        veh = detalle.get("vehiculo") or {}
        tiene_robo = bool(veh.get("tiene_reporte_robo"))

        advertencias: list[str] = []
        if tiene_robo:
            advertencias.append(
                f"⛔ REPORTE DE ROBO ACTIVO en REPUVE — NO suscribir, NO contratar, "
                f"NO listar. Identificador: {identificador}. Reportar a Ministerio Público "
                f"si el contribuyente lo tiene en su posesión actualmente."
            )
        elif not detalle.get("encontrado", True):
            advertencias.append(
                "Vehículo NO encontrado en REPUVE. Posible: (1) recién importado, "
                "(2) registro estatal no replicado nacionalmente, (3) NIV/placa erróneos. "
                "Solicitar Constancia de Inscripción al usuario antes de operar."
            )

        return {
            "identificador_buscado": identificador,
            "tipo": tipo,
            "consultado": detalle.get("encontrado", False),
            "tiene_reporte_robo": tiene_robo,
            "advertencias": advertencias,
            "detalle": detalle,
        }

    # ============================================================
    # Internal: routing mock / real
    # ============================================================

    def _consultar(self, tipo: str, valor: str) -> dict[str, Any]:
        cache_key = f"{tipo}:{valor}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._bitacora.log(
                "consultar",
                success=True,
                params_summary={"tipo": tipo, "id_hash": self._bitacora.hash_sensitive(valor), "cache": "hit"},
            )
            return cached

        if not should_use_real_browser(self.LIVE_ENV_FLAG):
            result = self._mock(tipo, valor)
        else:
            result = self._real_playwright(tipo, valor)

        self._cache.set(cache_key, result, ttl_hours=CACHE_TTL_HOURS)
        self._bitacora.log(
            "consultar",
            success=True,
            params_summary={
                "tipo": tipo,
                "id_hash": self._bitacora.hash_sensitive(valor),
                "encontrado": result.get("encontrado"),
                "cache": "miss",
                "modo": result.get("modo"),
            },
        )
        return result

    # ============================================================
    # Playwright path
    # ============================================================

    def _real_playwright(self, tipo: str, valor: str) -> dict[str, Any]:
        selector = SEARCH_INPUT_NIV if tipo == "niv" else SEARCH_INPUT_PLACA
        try:
            with PortalSession(
                portal_url=PORTAL_URL,
                api_url_pattern=API_URL_PATTERN,
                ready_selector=selector,
            ) as sess:
                captured = sess.query(
                    fill_action=lambda page: self._fill(page, selector, valor),
                    submit_action=lambda page: self._click_buscar(page, tipo),
                    wait_after_submit_ms=6000,
                )
        except PlaywrightNotAvailable as e:
            raise UpstreamError(
                "Playwright no disponible. Instala: pip install playwright && playwright install chromium",
                {"raw": str(e)},
            ) from e
        except Exception as e:
            raise UpstreamError(
                f"Error sesión Playwright REPUVE: {type(e).__name__}: {e}",
            ) from e

        if not captured:
            # NOTA: endpoint exacto pendiente discovery. Cuando se confirme,
            # actualizar API_URL_PATTERN en shared/repuve.py.
            raise UpstreamError(
                "Ningún XHR matched API_URL_PATTERN. Probable que el patrón regex "
                "necesite ajuste — capturar endpoint exacto con Playwright MCP y "
                "actualizar shared/repuve.py::API_URL_PATTERN.",
            )

        # Heurística: la primera respuesta JSON suele ser la del consulta
        resp = captured[0]
        return {
            "tipo": tipo,
            "valor": valor,
            "encontrado": resp.status == 200,
            "vehiculo": {"raw_response": resp.body[:500]},  # placeholder hasta confirmar schema
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": PORTAL_URL,
            "modo": "playwright",
            "simulated": False,
        }

    @staticmethod
    def _fill(page, selector: str, valor: str) -> None:
        page.evaluate(
            """({selector, value}) => {
                const el = document.querySelector(selector);
                if (!el) throw new Error('input not found: ' + selector);
                el.focus();
                const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                setter.call(el, value);
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }""",
            {"selector": selector, "value": valor},
        )

    @staticmethod
    def _click_buscar(page, tipo: str) -> None:
        # 2do botón "Buscar" corresponde al NIV; 1ro corresponde a placa.
        idx = 1 if tipo == "niv" else 0
        page.evaluate(
            f"""() => {{
                const btns = Array.from(document.querySelectorAll('button')).filter(b => b.textContent?.trim() === 'Buscar');
                if (btns[{idx}]) btns[{idx}].click();
                else if (btns[0]) btns[0].click();
            }}"""
        )

    # ============================================================
    # Mock path
    # ============================================================

    def _mock(self, tipo: str, valor: str) -> dict[str, Any]:
        """Mock determinístico:
          - Sufijo 1 → tiene reporte de robo
          - Sufijo otro → sin reporte
          - "FAKE"/"NOEXIST" en valor → no encontrado
        """
        last = valor[-1]
        if "FAKE" in valor.upper() or "NOEXIST" in valor.upper():
            return mark_simulated({
                "tipo": tipo,
                "valor": valor,
                "encontrado": False,
                "vehiculo": None,
                "fecha_consulta": datetime.now(timezone.utc).isoformat(),
                "fuente": PORTAL_URL,
                "modo": "mock",
            })

        veh = VehiculoREPUVE(
            niv=valor if tipo == "niv" else "3VWFE21C04M000001",
            placa=valor if tipo == "placa" else "ABC-12-34",
            marca="VOLKSWAGEN",
            submarca="JETTA",
            modelo="2018",
            color="GRIS",
            tipo="SEDAN",
            estado="CIUDAD DE MEXICO",
            estatus_robo="REPORTE DE ROBO ACTIVO" if last == "1" else "SIN REPORTE DE ROBO",
            tiene_reporte_robo=(last == "1"),
        )
        return mark_simulated({
            "tipo": tipo,
            "valor": valor,
            "encontrado": True,
            "vehiculo": veh.to_dict(),
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "fuente": PORTAL_URL,
            "modo": "mock",
        })
