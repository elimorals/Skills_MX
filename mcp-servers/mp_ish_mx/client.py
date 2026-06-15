"""Cliente mp_ish_mx — cálculo offline ISH por estado."""
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
from shared.errors import NotFoundError, ValidationError  # noqa: E402
from shared.ish_mx import buscar_ish, calcular_ish, listar_ish  # noqa: E402

NAMESPACE = "ish_mx"


class IshMxClient:
    def __init__(self, cache: FileCache | None = None, bitacora: Bitacora | None = None) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def calcular(self, estado: str, monto_hospedaje: float) -> dict[str, Any]:
        try:
            r = calcular_ish(estado, monto_hospedaje)
        except ValueError as e:
            if "no en catálogo" in str(e):
                raise NotFoundError(str(e)) from e
            raise ValidationError(str(e)) from e
        r["fecha_consulta"] = datetime.now(timezone.utc).isoformat()
        self._bitacora.log("calcular", success=True,
                           params_summary={"estado": estado, "monto": monto_hospedaje})
        return r

    def info_estado(self, estado: str) -> dict[str, Any]:
        e = buscar_ish(estado)
        if e is None:
            raise NotFoundError(f"Estado '{estado}' no en catálogo.")
        return {
            "clave": e.clave, "estado": e.nombre_estado, "cobra_ish": e.cobra_ish,
            "tasa_pct": e.tasa_pct, "portal_url": e.portal_url, "notas": e.notas,
        }

    def listar_estados(self, solo_aplicables: bool = False) -> dict[str, Any]:
        estados = listar_ish(solo_aplicables=solo_aplicables)
        return {
            "total": len(estados),
            "solo_aplicables": solo_aplicables,
            "estados": [{
                "clave": e.clave, "estado": e.nombre_estado, "tasa_pct": e.tasa_pct,
                "cobra_ish": e.cobra_ish, "portal": e.portal_url,
            } for e in estados],
        }

    def comparar_estados(self, estados: list[str], monto_hospedaje: float) -> dict[str, Any]:
        """Compara ISH entre N estados para un mismo monto de hospedaje."""
        if not estados or len(estados) > 32:
            raise ValidationError("Entre 1 y 32 estados.")
        resultados = []
        for clave in estados:
            try:
                r = self.calcular(clave, monto_hospedaje)
                resultados.append({"estado": r["estado"], "tasa_pct": r["tasa_pct"], "ish_mxn": r["ish_mxn"]})
            except NotFoundError:
                resultados.append({"estado": clave, "error": "no_en_catalogo"})
        validos = [r for r in resultados if "error" not in r]
        validos.sort(key=lambda r: r["ish_mxn"])
        return {
            "monto_hospedaje": monto_hospedaje,
            "comparados": len(resultados),
            "barato_a_caro": validos,
            "errores": [r for r in resultados if "error" in r],
        }
