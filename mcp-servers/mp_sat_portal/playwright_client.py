"""Cliente Playwright para el portal SAT (path real, opt-in).

⚠ ESTE MÓDULO ES EL ESQUELETO DEL PATH REAL.

Los métodos de scraping del portal SAT (CSF, Buzón Tributario, descarga masiva
CFDIs, etc.) están implementados como stubs que retornan dict con
`real_implementation_pending: true` cuando se invocan en modo real.

La razón es deliberada: los selectores del portal SAT cambian cada 3-6 meses.
Implementar el scraper sin tests específicos contra el portal vigente al
momento garantiza romper en producción. Este esqueleto:

1. Establece la arquitectura (clase, métodos, contratos)
2. Carga + valida e.firma con `EfirmaLoader`
3. Hace setup/teardown del browser cuando Playwright está disponible
4. Implementa detector de breakage de selectores
5. Falla limpio si Playwright no está instalado o e.firma vencida

Para implementar el path real:
- Instalar: `pip install playwright playwright-stealth`
- Ejecutar: `playwright install chromium`
- Setear `SAT_EFIRMA_CERT`, `SAT_EFIRMA_KEY`, `SAT_EFIRMA_PASSWORD`, `SAT_RFC`
- Setear `PLUGINS_MX_PLAYWRIGHT_REAL=1`
- Implementar cada `_real_*` del SatPlaywrightClient con selectores vigentes

Ver `docs/specs/02-sat-portal-playwright-real.md` para el plan completo.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared.bitacora import Bitacora
from shared.errors import AuthError, ConfigError, McpError, UpstreamError
from shared.mock import is_mock_mode, mark_simulated

from mp_sat_portal.efirma_loader import EfirmaLoader, EfirmaMetadata
from mp_sat_portal.selectors import SelectorsV1, default_selectors


NAMESPACE = "sat_portal_pw"

# Cache de sesión local
DEFAULT_SESSION_CACHE = Path("~/.cache/plugins-mx/sat_portal/session.json").expanduser()

URL_PORTAL_SAT = "https://siat.sat.gob.mx"
URL_BUZON_TRIBUTARIO = "https://buzonservicios.sat.gob.mx"

CREDENTIAL_ENV_VARS = ["SAT_EFIRMA_CERT", "SAT_EFIRMA_KEY", "SAT_EFIRMA_PASSWORD"]


class EfirmaVencidaError(AuthError):
    """e.firma del usuario está vencida o aún no es válida."""

    code = "efirma_vencida"


class SelectorBreakageError(UpstreamError):
    """Un selector del portal cambió. Mejor caer a mock que dar dato incorrecto."""

    code = "selector_breakage"


class PlaywrightNotAvailableError(ConfigError):
    """Playwright no está instalado en el entorno."""

    code = "playwright_not_available"


class SatPlaywrightClient:
    """Cliente Playwright para portal SAT.

    Construir con `from_env()` para auto-detectar credenciales.
    Cada método retorna dict con shape consistente:
        { "operation": str, "data": {...}, "simulated": bool, "notes": [str] }

    En modo mock retorna data sintética. En modo real:
    - Si selector está implementado y funcionando: retorna data scrapeada
    - Si selector aún no implementado: retorna mock con flag `real_implementation_pending`
    - Si selector implementado pero rompió: lanza SelectorBreakageError
    """

    def __init__(
        self,
        *,
        efirma: EfirmaLoader | None = None,
        bitacora: Bitacora | None = None,
        session_cache_path: Path | None = None,
        headless: bool = True,
        selectors: SelectorsV1 | None = None,
    ) -> None:
        self.efirma = efirma
        self.bitacora = bitacora or Bitacora(NAMESPACE)
        self.session_cache_path = session_cache_path or DEFAULT_SESSION_CACHE
        self.headless = headless
        self.selectors = selectors or default_selectors()
        self._browser_context = None  # type: ignore[var-annotated]

    @classmethod
    def from_env(cls, **kwargs: Any) -> "SatPlaywrightClient":
        """Construye el cliente leyendo SAT_EFIRMA_* del entorno.

        Si falta cualquier env, deja `efirma=None` — el cliente entrará en modo mock.
        """
        try:
            efirma = EfirmaLoader.from_env()
        except ConfigError:
            efirma = None
        return cls(efirma=efirma, **kwargs)

    # ---------- modo detection ----------

    def get_mode(self) -> str:
        """Retorna "mock" | "blocked" | "real".

        - "mock": no hay credenciales (o PLUGINS_MX_MOCK=1)
        - "real": credenciales + PLUGINS_MX_PLAYWRIGHT_REAL=1 + playwright instalado
        - "blocked": credenciales pero falta opt-in o falta playwright
        """
        # PLUGINS_MX_MOCK=1 override total
        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            return "mock"
        if self.efirma is None:
            return "mock"
        if os.environ.get("PLUGINS_MX_PLAYWRIGHT_REAL") != "1":
            return "blocked"
        if not _playwright_available():
            return "blocked"
        return "real"

    def precheck_efirma(self) -> EfirmaMetadata | None:
        """Valida que la e.firma esté vigente antes de cualquier operación.

        Lanza EfirmaVencidaError si está vencida.
        Retorna None si no hay e.firma cargada (modo mock).
        """
        if self.efirma is None:
            return None
        meta = self.efirma.metadata()
        if not meta.is_valid_now:
            raise EfirmaVencidaError(
                f"e.firma {meta.rfc} no vigente. Vence {meta.not_after.date().isoformat()}. "
                f"Renovar antes de continuar.",
                {"rfc": meta.rfc, "expiry": meta.not_after.isoformat()},
            )
        if meta.days_until_expiry < 30:
            # Warning level — sigue funcionando
            self.bitacora.log(
                "precheck_efirma",
                success=True,
                params_summary={"rfc_hash": Bitacora.hash_sensitive(meta.rfc)},
                result_summary={"days_until_expiry": meta.days_until_expiry},
                extra={"warning": "e.firma vence pronto"},
            )
        return meta

    # ---------- public methods (mock-aware) ----------

    def descargar_csf(self, rfc: str) -> dict[str, Any]:
        """Descarga Constancia de Situación Fiscal (PDF)."""
        return self._dispatch("descargar_csf", {"rfc": rfc}, self._real_descargar_csf)

    def descargar_buzon_tributario(self, rfc: str) -> dict[str, Any]:
        return self._dispatch(
            "descargar_buzon_tributario", {"rfc": rfc}, self._real_descargar_buzon_tributario
        )

    def descargar_cfdi_masivo(
        self, rfc: str, ejercicio: int, mes: int, tipo: str
    ) -> dict[str, Any]:
        params = {"rfc": rfc, "ejercicio": ejercicio, "mes": mes, "tipo": tipo}
        return self._dispatch("descargar_cfdi_masivo", params, self._real_descargar_cfdi_masivo)

    def verificar_efirma_vigente(self, rfc: str) -> dict[str, Any]:
        """Caso especial: si tenemos e.firma cargada, podemos responder sin Playwright."""
        if self.efirma is not None:
            try:
                meta = self.efirma.metadata()
                self.bitacora.log(
                    "verificar_efirma_vigente",
                    success=True,
                    params_summary={"rfc_hash": Bitacora.hash_sensitive(rfc)},
                    result_summary={"days_until_expiry": meta.days_until_expiry},
                )
                return {
                    "operation": "verificar_efirma_vigente",
                    "data": meta.to_dict(),
                    "simulated": False,
                    "notes": ["data obtenida del .cer local, no del portal SAT"],
                }
            except Exception:
                pass
        return self._dispatch(
            "verificar_efirma_vigente", {"rfc": rfc}, self._real_verificar_efirma_vigente
        )

    def descargar_acuse(self, folio: str) -> dict[str, Any]:
        return self._dispatch("descargar_acuse", {"folio": folio}, self._real_descargar_acuse)

    # ---------- dispatch internal ----------

    def _dispatch(
        self, op: str, params: dict[str, Any], real_impl
    ) -> dict[str, Any]:
        """Decide mock vs real y registra en bitácora."""
        mode = self.get_mode()
        safe_params = self._summarize_params(params)
        try:
            if mode == "mock" or mode == "blocked":
                result = self._mock_response(op, params, blocked=mode == "blocked")
                self.bitacora.log(op, success=True, params_summary=safe_params, result_summary={"mode": mode})
                return result
            # mode == "real"
            self.precheck_efirma()
            result = real_impl(params)
            self.bitacora.log(op, success=True, params_summary=safe_params, result_summary={"mode": "real"})
            return result
        except McpError as exc:
            self.bitacora.log(op, success=False, params_summary=safe_params, error=exc.to_dict())
            raise
        except Exception as exc:
            wrapped = UpstreamError(f"{op} falló inesperadamente: {type(exc).__name__}")
            self.bitacora.log(op, success=False, params_summary=safe_params, error=wrapped.to_dict())
            raise wrapped from exc

    def _summarize_params(self, params: dict[str, Any]) -> dict[str, Any]:
        out = {}
        for k, v in params.items():
            if k == "rfc" and isinstance(v, str):
                out["rfc_hash"] = Bitacora.hash_sensitive(v)
            else:
                out[k] = v
        return out

    def _mock_response(self, op: str, params: dict[str, Any], *, blocked: bool) -> dict[str, Any]:
        notes = ["mock — sin Playwright real activo"]
        if blocked:
            notes.append(
                "credenciales detectadas pero falta PLUGINS_MX_PLAYWRIGHT_REAL=1 o playwright no instalado"
            )
        if op == "descargar_csf":
            data = {
                "rfc": params.get("rfc"),
                "razon_social": "MOCK NOMBRE EJEMPLO",
                "regimen_fiscal": "612",
                "fecha_constancia": datetime.now(timezone.utc).date().isoformat(),
                "pdf_path": None,
            }
        elif op == "descargar_buzon_tributario":
            data = {"rfc": params.get("rfc"), "notificaciones": [], "no_leidas": 0}
        elif op == "descargar_cfdi_masivo":
            data = {
                "rfc": params.get("rfc"),
                "ejercicio": params.get("ejercicio"),
                "mes": params.get("mes"),
                "tipo": params.get("tipo"),
                "solicitud_id": "MOCK-SOL-001",
                "estado": "solicitada",
                "fecha_solicitud": datetime.now(timezone.utc).isoformat(),
                "total_cfdis": None,
                "url_descarga_zip": None,
            }
        elif op == "verificar_efirma_vigente":
            data = {
                "rfc": params.get("rfc"),
                "vigente": True,
                "dias_para_vencer": 365,
                "vigencia_hasta": "2027-12-31T00:00:00+00:00",
            }
        elif op == "descargar_acuse":
            data = {
                "folio": params.get("folio"),
                "pdf_path": None,
                "fecha_presentacion": datetime.now(timezone.utc).date().isoformat(),
            }
        else:
            data = {}
        return mark_simulated(
            {"operation": op, "data": data, "notes": notes, "real_implementation_pending": True},
            "; ".join(notes),
        )

    # ---------- real implementations (stubs) ----------

    def _real_descargar_csf(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._real_not_implemented("descargar_csf", params)

    def _real_descargar_buzon_tributario(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._real_not_implemented("descargar_buzon_tributario", params)

    def _real_descargar_cfdi_masivo(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._real_not_implemented("descargar_cfdi_masivo", params)

    def _real_verificar_efirma_vigente(self, params: dict[str, Any]) -> dict[str, Any]:
        """Verifica e.firma vigente haciendo login real al portal SAT.

        Flujo: abrir browser → login con .cer/.key/password → si login OK,
        e.firma vigente; si rechaza, e.firma vencida o inválida.

        Este es el `_real_*` más simple porque sólo necesita el flujo de login
        — no requiere navegación a ninguna sección específica del portal.

        ⚠ Selectores en `selectors.py` son hipótesis. Validar contra el portal
        vigente al momento de activar producción.
        """
        from mp_sat_portal._browser_helpers import (
            LoginFailedError,
            browser_context,
            dump_failure_artifacts,
            login_efirma,
        )

        if self.efirma is None:
            # Defensive: get_mode() ya filtró este caso, pero por si acaso.
            return self._real_not_implemented("verificar_efirma_vigente", params)

        with browser_context(headless=self.headless) as (_browser, _ctx, page):
            try:
                login_efirma(page, efirma=self.efirma, selectors=self.selectors)
            except LoginFailedError as exc:
                artifacts = dump_failure_artifacts(
                    page, operation="verificar_efirma_vigente"
                )
                return {
                    "operation": "verificar_efirma_vigente",
                    "data": {
                        "rfc": params.get("rfc"),
                        "vigente": False,
                        "razon": str(exc),
                    },
                    "simulated": False,
                    "notes": [
                        "login rechazado por portal SAT",
                        f"artifacts guardados en {artifacts}",
                    ],
                }
            # Login OK → la e.firma está vigente. Complementamos con metadata local.
            meta = self.efirma.metadata()
            return {
                "operation": "verificar_efirma_vigente",
                "data": {
                    "rfc": meta.rfc,
                    "vigente": True,
                    "vigencia_hasta": meta.not_after.isoformat(),
                    "dias_para_vencer": meta.days_until_expiry,
                    "verificado_contra_portal": True,
                },
                "simulated": False,
                "notes": ["login exitoso en portal SAT, e.firma vigente"],
            }

    def _real_descargar_acuse(self, params: dict[str, Any]) -> dict[str, Any]:
        return self._real_not_implemented("descargar_acuse", params)

    def _real_not_implemented(self, op: str, params: dict[str, Any]) -> dict[str, Any]:
        """Placeholder honest: el método existe pero scraper específico no.

        En lugar de retornar data inventada en modo real, retorna mock + flag
        explícito. Mejor que crash silencioso. Esto permite que el resto de la
        app siga funcionando mientras se implementa el scraper.
        """
        return self._mock_response(op, params, blocked=False)


# ---------- module-level helpers ----------

def _playwright_available() -> bool:
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


def detector_breakage(
    selectors_esperados: list[str], html_snapshot: str
) -> dict[str, Any]:
    """Detecta si selectores esperados existen en el HTML actual del portal.

    Útil para correr periódicamente (cron mensual) y alertar antes de que
    el scraper rompa en producción.

    Returns:
        {
            "ok": bool,
            "missing": [selectors_no_encontrados],
            "total_esperados": int,
            "encontrados": int,
        }
    """
    missing = []
    for sel in selectors_esperados:
        # Heurística simple: busca el texto del selector como substring del HTML.
        # En implementación real esto usaría BeautifulSoup o Playwright.
        if sel not in html_snapshot:
            missing.append(sel)
    return {
        "ok": len(missing) == 0,
        "missing": missing,
        "total_esperados": len(selectors_esperados),
        "encontrados": len(selectors_esperados) - len(missing),
    }
