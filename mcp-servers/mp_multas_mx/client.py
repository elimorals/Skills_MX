"""Cliente unificado para consulta multas tránsito MX (estatal).

Estado real (2026-10-14): los portales vigentes exigen CAPTCHA → handoff humano
tras un GET real. Portal caído o cambiado → UpstreamError. Mock solo con
PLUGINS_MX_MOCK=1.
"""

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
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import SAF_CDMX_ADEUDOS, handoff_humano, mock_forzado  # noqa: E402
from shared.saf_cdmx import adeudos_o_handoff  # noqa: E402

from mp_multas_mx.catalogo_multas import (  # noqa: E402
    ESTADOS_SIN_PORTAL,
    NOTAS_ESTADO,
    PORTALES_MULTAS,
    estados_soportados,
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
        """Multas pendientes por placa: handoff humano al portal oficial."""
        estado_norm = estado.lower().strip()
        placa_norm = placa.upper().strip().replace(" ", "")

        if not PLACA_REGEX.match(placa_norm):
            raise ValidationError(
                f"Placa '{placa}' no tiene formato válido MX. "
                f"Ejemplo válido: ABC-12-34 o ABC1234."
            )
        if estado_norm in ESTADOS_SIN_PORTAL:
            raise ValidationError(f"Estado '{estado}' sin portal vigente: {ESTADOS_SIN_PORTAL[estado_norm]}")
        if estado_norm not in PORTALES_MULTAS:
            raise ValidationError(
                f"Estado '{estado}' no soportado para multas. Soportados: {estados_soportados()}"
            )

        self._log("consultar_multas", {"estado": estado_norm, "placa": placa_norm})
        if mock_forzado():
            return self._mock_response(estado_norm, placa_norm)
        if PORTALES_MULTAS[estado_norm] is SAF_CDMX_ADEUDOS:
            return adeudos_o_handoff(placa_norm, estado=estado_norm, nota=NOTAS_ESTADO.get(estado_norm))
        return handoff_humano(
            PORTALES_MULTAS[estado_norm],
            estado=estado_norm,
            placa=placa_norm.replace("-", ""),
            nota=NOTAS_ESTADO.get(estado_norm),
        )

    def estados_disponibles(self) -> dict[str, Any]:
        """Estados con portal de multas verificado y los retirados."""
        return {
            "soportados": estados_soportados(),
            "total": len(PORTALES_MULTAS),
            "requieren_captcha": sorted(
                e for e, p in PORTALES_MULTAS.items() if p.motivo == "captcha"
            ),
            "sin_portal_vigente": ESTADOS_SIN_PORTAL,
            "notas_por_estado": NOTAS_ESTADO,
        }

    def _mock_response(self, estado: str, placa: str) -> dict[str, Any]:
        """Mock (solo PLUGINS_MX_MOCK=1)."""
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
            "url_consultada": PORTALES_MULTAS[estado].url,
        })
