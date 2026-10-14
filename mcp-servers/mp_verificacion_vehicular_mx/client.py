"""Cliente mp_verificacion_vehicular_mx.

Estado real (2026-10-14):
- `consultar_estatus` CDMX: SAF Consultaciudadana exige CAPTCHA imagen →
  handoff humano tras un GET real. Ya no se pide el CAPTCHA por env/stdin.
- Otros estados: sin consulta pública automatizable → UpstreamError explícito.
- `proximo_periodo`: calendario oficial 2026 calculado localmente.

Datos simulados solo con PLUGINS_MX_MOCK=1.
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
from shared.errors import NotFoundError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import SAF_CDMX_ADEUDOS, handoff_humano, mock_forzado  # noqa: E402
from shared.verificacion_vehicular import (  # noqa: E402
    CATALOGO_VERIFICACION,
    FUENTES_CALENDARIO_2026,
    buscar_programa,
    calcular_proximo_periodo,
    mes_proxima_verificacion,
)


NAMESPACE = "verificacion_vehicular"
ESTADOS_MEGALOPOLIS = {"cdmx", "edomex", "hgo", "mor", "pue", "tlax"}


def _normalizar(placa: str) -> str:
    return placa.strip().upper().replace(" ", "").replace("-", "")


class VerificacionVehicularClient:
    def __init__(self, cache: FileCache | None = None, bitacora: Bitacora | None = None) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_estatus(self, placa: str, estado: str) -> dict[str, Any]:
        """Estatus de verificación/adeudos del vehículo."""
        placa = _normalizar(placa)
        if len(placa) < 5:
            raise ValidationError(f"Placa muy corta: {placa}")
        p = buscar_programa(estado)
        if p is None:
            raise NotFoundError(f"Estado '{estado}' no en catálogo verificación.")
        self._bitacora.log("consultar_estatus", success=True,
                           params_summary={"estado": p.clave, "placa_hash": self._bitacora.hash_sensitive(placa)})
        if mock_forzado():
            return self._mock(p, placa)
        if p.clave == "cdmx":
            return handoff_humano(SAF_CDMX_ADEUDOS, placa=placa, seccion="Sanciones ambientales")
        raise UpstreamError(
            f"{p.nombre_estado} no publica consulta de estatus de verificación por placa automatizable.",
            {"estado": p.clave, "portal": p.portal_url, "estado_impl": "no_disponible"},
        )

    def proximo_periodo(self, placa: str, estado: str = "cdmx") -> dict[str, Any]:
        """Próximo periodo de verificación según el calendario 2026 de la Megalópolis."""
        placa = _normalizar(placa)
        if not placa:
            raise ValidationError("Placa requerida")
        if estado.strip().lower() not in ESTADOS_MEGALOPOLIS:
            raise ValidationError(f"El calendario de engomados solo aplica a la Megalópolis: {sorted(ESTADOS_MEGALOPOLIS)}")
        terminacion = next((int(c) for c in reversed(placa) if c.isdigit()), None)
        if terminacion is None:
            raise ValidationError(f"Placa '{placa}' sin dígitos.")
        now = datetime.now(timezone.utc)
        color, meses = calcular_proximo_periodo(terminacion, now.month)
        proximo = mes_proxima_verificacion(terminacion, now.month)
        return {
            "placa": placa,
            "estado": estado,
            "terminacion": terminacion,
            "color_engomado": color,
            "meses_obligatorios": meses,
            "proximo_mes_verificacion": proximo if proximo <= 12 else proximo - 12,
            "proximo_anio_verificacion": now.year if proximo <= 12 else now.year + 1,
            "fuentes": list(FUENTES_CALENDARIO_2026),
            "fecha_consulta": now.isoformat(),
            "simulated": False,
        }

    def listar_programas(self) -> dict[str, Any]:
        return {
            "total": len(CATALOGO_VERIFICACION),
            "programas": [{
                "clave": p.clave, "estado": p.nombre_estado, "activo": p.activo,
                "frecuencia_meses": p.frecuencia_meses, "costo_mxn": p.costo_mxn,
                "verificado_2026": p.verificado_2026, "fuentes": list(p.fuentes),
                "portal": p.portal_url, "notas": p.notas,
            } for p in CATALOGO_VERIFICACION],
        }

    def _mock(self, p, placa: str) -> dict[str, Any]:
        last_d = next((c for c in reversed(placa) if c.isdigit()), "5")
        hologramas = {"0": "00", "1": "0", "2": "1", "3": "2", "4": "00", "5": "0",
                      "6": "1", "7": "2", "8": "Rechazo", "9": "0"}
        h = hologramas.get(last_d, "0")
        return mark_simulated({
            "placa": placa,
            "estado": p.clave,
            "ultima_verificacion": "2026-04-15",
            "holograma_actual": h,
            "vigencia_hasta": "2026-10-15",
            "vigente": h != "Rechazo",
            "costo_proxima_verificacion_mxn": p.costo_mxn,
            "fuente": p.portal_url,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })
