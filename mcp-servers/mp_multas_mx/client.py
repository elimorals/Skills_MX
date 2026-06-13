"""Cliente unificado para consulta multas tránsito MX (estatal)."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import McpError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.playwright_municipal_generic import consulta_portal  # noqa: E402
from shared.playwright_real import is_public_real_enabled, with_real_or_fallback  # noqa: E402

from mp_multas_mx.catalogo_multas import (  # noqa: E402
    ESTADOS_CON_CAPTCHA,
    NOTAS_ESTADO,
    PORTALES_MULTAS,
    estados_soportados,
    get_portal_multas,
    requiere_captcha,
)


NAMESPACE = "multas_mx"

# Regex placa MX (varios formatos: ABC-12-34, ABC-1234, AB-12-345, etc.)
PLACA_REGEX = re.compile(r"^[A-Z0-9]{2,4}-?[A-Z0-9]{2,4}-?[A-Z0-9]{1,3}$", re.IGNORECASE)


class MultasMxClient:
    """Cliente multas estatales unificado."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        if "placa" in safe:
            safe["placa_hash"] = Bitacora.hash_sensitive(str(safe.pop("placa")))
        self._bitacora.log(op, success=True, params_summary=safe)

    def consultar_multas(self, estado: str, placa: str) -> dict[str, Any]:
        """Consulta multas pendientes por placa en un estado.

        Args:
            estado: clave estado (cdmx, nl, jal, etc.)
            placa: placa vehicular formato MX

        Returns:
            Dict con: placa_hash, estatus, adeudo_total_mxn, multas: [...]

        Raises:
            ValidationError si placa o estado inválido
            UpstreamError si estado requiere CAPTCHA (humano-en-loop) o portal falla
        """
        estado_norm = estado.lower().strip()
        placa_norm = placa.upper().strip().replace(" ", "")

        if not PLACA_REGEX.match(placa_norm):
            raise ValidationError(
                f"Placa '{placa}' no tiene formato válido MX. "
                f"Ejemplo válido: ABC-12-34 o ABC1234."
            )

        if estado_norm not in PORTALES_MULTAS:
            raise ValidationError(
                f"Estado '{estado}' no soportado para multas. "
                f"Soportados: {estados_soportados()}"
            )

        self._log("consultar_multas", {"estado": estado_norm, "placa": placa_norm})

        # CAPTCHA → humano-en-loop, NO automatizar
        if requiere_captcha(estado_norm):
            return mark_simulated({
                "estado": estado_norm,
                "placa_hash": placa_norm[:3] + "***",
                "status": "requiere_humano",
                "razon": NOTAS_ESTADO.get(estado_norm, "Estado con CAPTCHA"),
                "url_consulta_manual": PORTALES_MULTAS[estado_norm]["default"].url,
                "instrucciones": "Abrir URL en navegador real, completar CAPTCHA, ingresar placa.",
            })

        # Mock si Playwright real no habilitado
        if not is_public_real_enabled():
            return self._mock_response(estado_norm, placa_norm)

        # Real
        portal = get_portal_multas(estado_norm)
        if portal is None:
            raise UpstreamError(
                f"Estado {estado_norm} no tiene PortalConfig.",
                {"estado": estado_norm},
            )

        return with_real_or_fallback(
            real_fn=lambda: consulta_portal(portal, placa_norm),
            fallback_fn=lambda: self._mock_response(estado_norm, placa_norm),
            portal=f"multas_{estado_norm}",
        )

    def estados_disponibles(self) -> dict[str, Any]:
        """Lista estados con multas consultables + cuáles requieren CAPTCHA."""
        return {
            "soportados": estados_soportados(),
            "total": len(PORTALES_MULTAS),
            "requieren_captcha": sorted(ESTADOS_CON_CAPTCHA),
            "notas_por_estado": NOTAS_ESTADO,
        }

    def _mock_response(self, estado: str, placa: str) -> dict[str, Any]:
        """Mock realista de respuesta de multas."""
        seed = sum(ord(c) for c in placa) % 100
        n_multas = max(0, (seed - 50) // 15) if seed > 50 else 0
        adeudo = sum(450 + i * 150 for i in range(n_multas))
        return mark_simulated({
            "estado": estado,
            "placa_hash": placa[:3] + "***",
            "estatus": "al_corriente" if n_multas == 0 else "con_multas",
            "total_multas_pendientes": n_multas,
            "adeudo_total_mxn": adeudo,
            "multas": [
                {
                    "folio": f"INF-{estado.upper()}-{i+1:06d}",
                    "fecha": "2026-0{}-{:02d}".format((i % 6) + 1, (i * 7 % 28) + 1),
                    "motivo": ["Velocidad", "No respetar luz roja", "Mal estacionamiento", "Sin verificación"][i % 4],
                    "monto_mxn": 450 + i * 150,
                }
                for i in range(n_multas)
            ],
            "url_consultada": PORTALES_MULTAS[estado]["default"].url,
        })
