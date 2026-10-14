"""Cliente REPUVE — consulta NIV/placa robados.

Portal: https://www2.repuve.gob.mx:8443/ciudadania/ (Angular + reCAPTCHA v3).
Endpoint observado 2026-10-14: POST https://www2.repuve.gob.mx:8443/consulta/consulta/repuve
con body JSON {criterio, llave, ...} cifrado en el navegador y token reCAPTCHA;
un navegador automatizado recibe 401 "El reCaptcha no fue superado".

No se evade el CAPTCHA: el modo real devuelve un **handoff humano** (URL,
pasos, criterio prellenado). Mock solo con PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import os
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
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import armar_handoff  # noqa: E402
from shared.repuve import (  # noqa: E402
    PORTAL_URL,
    VehiculoREPUVE,
    validar_niv,
    validar_placa,
)


NAMESPACE = "repuve"
CACHE_TTL_HOURS = 24 * 7  # 7 días
TIMEOUT_SECONDS = 30.0


class RepuveClient:
    """Cliente unificado REPUVE."""


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

        if detalle.get("requiere_humano"):
            return {
                "identificador_buscado": identificador,
                "tipo": tipo,
                "consultado": False,
                "tiene_reporte_robo": None,  # desconocido: no se pudo consultar
                "advertencias": ["REPUVE exige reCAPTCHA: una persona debe completar la consulta."],
                "detalle": detalle,
            }

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

        if os.environ.get("PLUGINS_MX_MOCK") != "1":
            return self._handoff(tipo, valor)  # no se cachea: no hay dato

        result = self._mock(tipo, valor)

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

    @staticmethod
    def _handoff(tipo: str, valor: str) -> dict[str, Any]:
        campo = "Número de Identificación Vehicular (NIV)" if tipo == "niv" else "Número de Placa"
        return armar_handoff(
            motivo="captcha",
            url=PORTAL_URL,
            pasos=[
                "Abrir la URL en un navegador.",
                f"Capturar solo el campo '{campo}' con el valor prellenado.",
                "Pulsar 'Buscar' (el reCAPTCHA invisible se valida en el navegador).",
                "Leer 'Estatus' / reporte de robo en el resultado.",
            ],
            campos_prellenados={tipo: valor},
            tipo=tipo,
            valor=valor,
            encontrado=None,
            fecha_consulta=datetime.now(timezone.utc).isoformat(),
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
