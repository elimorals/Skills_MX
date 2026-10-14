"""Cliente mp_cdmx_municipal.

Estado real (2026-10-14):
- Predial: OVICA exige ALTCHA → handoff humano (GET real que confirma el portal).
- Tenencia / multas: SAF Consultaciudadana exige CAPTCHA imagen → handoff humano.
- Hoy No Circula: reglas oficiales calculadas localmente (no es mock).

Datos simulados solo con PLUGINS_MX_MOCK=1.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import (  # noqa: E402
    OVICA_CDMX_PREDIAL,
    SAF_CDMX_ADEUDOS,
    handoff_humano,
    mock_forzado,
)
from shared.saf_cdmx import normalizar_placa  # noqa: E402

from mp_cdmx_municipal import mock_data  # noqa: E402


NAMESPACE = "cdmx_municipal_mcp"

FUENTE_HNC = (
    "SEDEMA CDMX — Programa Hoy No Circula "
    "(https://www.sedema.cdmx.gob.mx/programas/programa/hoy-no-circula)"
)
# Día de la semana (0=lunes) → (engomado, terminaciones)
_HNC_ENTRE_SEMANA = {
    0: ("amarillo", "5,6"),
    1: ("rosa", "7,8"),
    2: ("rojo", "3,4"),
    3: ("verde", "1,2"),
    4: ("azul", "9,0"),
}


def reglas_hoy_no_circula(fecha: date) -> dict[str, Any]:
    """Restricción ordinaria (sin contingencia) para una fecha, 5:00–22:00 h."""
    restricciones: list[dict[str, Any]] = []
    if fecha.weekday() in _HNC_ENTRE_SEMANA:
        engomado, digitos = _HNC_ENTRE_SEMANA[fecha.weekday()]
        restricciones.append({
            "ultimo_digito_placa": digitos,
            "engomado": engomado,
            "holograma_aplica": ["1", "2"],
        })
    elif fecha.weekday() == 5:
        n_sabado = (fecha.day - 1) // 7 + 1
        restricciones.append({"ultimo_digito_placa": "todos", "holograma_aplica": ["2"]})
        if n_sabado in (1, 3):
            restricciones.append({"ultimo_digito_placa": "1,3,5,7,9", "holograma_aplica": ["1"]})
        elif n_sabado in (2, 4):
            restricciones.append({"ultimo_digito_placa": "0,2,4,6,8", "holograma_aplica": ["1"]})
    return {
        "fecha": fecha.isoformat(),
        "horario": "05:00-22:00",
        "contingencia_activa": None,
        "nota_contingencia": (
            "Las contingencias ambientales las declara la CAMe el mismo día; "
            "este cálculo no las consulta. Revisa http://www.aire.cdmx.gob.mx."
        ),
        "restricciones_del_dia": restricciones,
        "exentos": [
            "Holograma 00 y 0",
            "Vehículos eléctricos e híbridos con holograma Exento",
            "Servicio público, emergencia y personas con discapacidad con placa/permiso",
        ],
        "fuente": FUENTE_HNC,
        "simulated": False,
    }


class CdmxMunicipalClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        for k in ("placa", "cuenta_predial"):
            if k in safe:
                safe[f"{k}_hash"] = Bitacora.hash_sensitive(str(safe.pop(k)))
        self._bitacora.log(op, success=True, params_summary=safe)

    def consultar_predial(self, cuenta_predial: str) -> dict[str, Any]:
        if not cuenta_predial or len(cuenta_predial) < 5:
            raise ValidationError("cuenta_predial debe tener al menos 5 caracteres")
        self._log("predial", {"cuenta_predial": cuenta_predial})
        if mock_forzado():
            return mark_simulated(mock_data.mock_predial(cuenta_predial))
        return handoff_humano(OVICA_CDMX_PREDIAL, cuenta_predial_hash=cuenta_predial[:4] + "***")

    def consultar_tenencia(self, placa: str) -> dict[str, Any]:
        if not placa or len(placa) < 5:
            raise ValidationError("placa requerida")
        self._log("tenencia", {"placa": placa})
        if mock_forzado():
            return mark_simulated(mock_data.mock_tenencia(placa))
        return handoff_humano(SAF_CDMX_ADEUDOS, placa=normalizar_placa(placa), seccion="Tenencia")

    def consultar_multas(self, placa: str) -> dict[str, Any]:
        if not placa or len(placa) < 5:
            raise ValidationError("placa requerida")
        self._log("multas", {"placa": placa})
        if mock_forzado():
            return mark_simulated(mock_data.mock_multas(placa))
        return handoff_humano(SAF_CDMX_ADEUDOS, placa=normalizar_placa(placa), seccion="Infracciones")

    def consultar_calendario_hoy_no_circula(self, fecha: str) -> dict[str, Any]:
        try:
            f = date.fromisoformat(fecha)
        except ValueError as e:
            raise ValidationError(f"fecha inválida '{fecha}', usa YYYY-MM-DD") from e
        self._log("hoy_no_circula", {"fecha": fecha})
        return reglas_hoy_no_circula(f)
