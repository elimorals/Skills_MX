"""Cliente mp_tenencia_mx — cálculo offline + lookup catálogo."""
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
from shared.tenencia_mx import (  # noqa: E402
    CATALOGO_TENENCIA,
    EstadoTenencia,
    buscar_estado,
    calcular_tenencia,
    listar_estados,
)


NAMESPACE = "tenencia_mx"


class TenenciaMxClient:
    """Cliente unificado tenencia/refrendo MX."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def calcular(
        self,
        estado: str,
        valor_factura: float,
        anio_modelo: int,
        anio_actual: int | None = None,
    ) -> dict[str, Any]:
        """Calcula tenencia + refrendo proyectado.

        Returns:
            dict con tenencia_mxn, refrendo_mxn, subtotal_mxn, exento, etc.
        """
        try:
            result = calcular_tenencia(estado, valor_factura, anio_modelo, anio_actual)
        except ValueError as e:
            if "no en catálogo" in str(e):
                raise NotFoundError(str(e)) from e
            raise ValidationError(str(e)) from e
        result["fecha_consulta"] = datetime.now(timezone.utc).isoformat()
        self._bitacora.log(
            "calcular",
            success=True,
            params_summary={"estado": estado, "valor_factura": valor_factura, "antiguedad": result["antiguedad_anios"]},
        )
        return result

    def info_estado(self, estado: str) -> dict[str, Any]:
        """Devuelve la configuración completa de un estado."""
        e = buscar_estado(estado)
        if e is None:
            raise NotFoundError(f"Estado '{estado}' no en catálogo.")
        return self._estado_to_dict(e)

    def listar_estados(self, solo_con_tenencia: bool = False) -> dict[str, Any]:
        """Lista los estados del catálogo."""
        estados = listar_estados(solo_con_tenencia=solo_con_tenencia)
        return {
            "total": len(estados),
            "solo_con_tenencia": solo_con_tenencia,
            "estados": [self._estado_to_dict(e) for e in estados],
        }

    def comparar_estados(
        self,
        estados_claves: list[str],
        valor_factura: float,
        anio_modelo: int,
    ) -> dict[str, Any]:
        """Compara costo tenencia/refrendo entre N estados.

        Útil para flotillas multi-estado decidiendo dónde re-emplacar.
        """
        if not estados_claves:
            raise ValidationError("Lista de estados vacía.")
        if len(estados_claves) > 20:
            raise ValidationError("Máx 20 estados por comparación.")

        resultados = []
        for clave in estados_claves:
            try:
                r = self.calcular(clave, valor_factura, anio_modelo)
                resultados.append({
                    "estado": r["estado"],
                    "estado_nombre": r["estado_nombre"],
                    "subtotal_mxn": r["subtotal_mxn"],
                    "tenencia_mxn": r["tenencia_mxn"],
                    "refrendo_mxn": r["refrendo_mxn"],
                    "exento_tenencia": r["exento_de_tenencia"],
                })
            except NotFoundError:
                resultados.append({"estado": clave, "error": "no_en_catalogo"})

        # Ordenar de barato a caro
        validos = [r for r in resultados if "error" not in r]
        validos.sort(key=lambda r: r["subtotal_mxn"])

        return {
            "valor_factura": valor_factura,
            "anio_modelo": anio_modelo,
            "comparados": len(resultados),
            "barato_a_caro": validos,
            "errores": [r for r in resultados if "error" in r],
            "ahorro_max_mxn": round(
                (validos[-1]["subtotal_mxn"] - validos[0]["subtotal_mxn"]) if len(validos) >= 2 else 0,
                2,
            ),
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _estado_to_dict(e: EstadoTenencia) -> dict[str, Any]:
        return {
            "clave": e.clave,
            "estado": e.nombre_estado,
            "cobra_tenencia": e.cobra_tenencia,
            "cobra_refrendo": e.cobra_refrendo,
            "cobra_control_vehicular": e.cobra_control_vehicular,
            "tasa_tenencia_pct": e.tasa_tenencia_pct,
            "costo_refrendo_mxn": e.costo_refrendo_mxn,
            "umbral_exencion_factura": e.umbral_exencion_factura,
            "portal_url": e.portal_url,
            "metodo": e.metodo,
            "notas": e.notas,
        }
