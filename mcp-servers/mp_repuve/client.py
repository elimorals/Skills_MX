"""Cliente REPUVE — consulta NIV/placa robados.

Portal: https://www2.repuve.gob.mx:8443/ciudadania/ (Angular + reCAPTCHA v3).
POST /consulta/consulta/repuve (vehículo) y /pgj (estatus de robo) con body
{criterio, llave} cifrado RSA PKCS#1 v1.5 con llaves públicas fijas del bundle
+ token reCAPTCHA v3 (acción "login"). Detalle en shared/repuve.py.

- Solver opt-in activo (`solver_activo("repuve")`): token vía 2captcha, cifrado
  y consulta real; si REPUVE rechaza el token se reintenta 2 veces → UpstreamError.
- Sin solver: **handoff humano** (URL, pasos, criterio prellenado).
Mock solo con PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared import repuve as rp  # noqa: E402
from shared.captcha_solver import CaptchaSolver, TokenRechazado, con_token, solver_activo  # noqa: E402
from shared.errors import UpstreamError, ValidationError  # noqa: E402
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
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)


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
        tiene_robo = veh.get("tiene_reporte_robo")
        if tiene_robo is not None:
            tiene_robo = bool(tiene_robo)

        advertencias: list[str] = list(detalle.get("advertencias") or [])
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

        if os.environ.get("PLUGINS_MX_MOCK") == "1":
            result = self._mock(tipo, valor)
        elif solver_activo("repuve"):
            result = self._real(tipo, valor)
        else:
            return self._handoff(tipo, valor)  # no se cachea: no hay dato

        if not result.get("advertencias"):  # robo desconocido no se cachea
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

    def _real(self, tipo: str, valor: str) -> dict[str, Any]:
        """Consulta real con token del solver. /pgj aparte: si falla, robo = None (desconocido)."""
        with httpx.Client(timeout=TIMEOUT_SECONDS, verify=rp.ssl_legacy(),
                          headers={"User-Agent": USER_AGENT}) as http:
            cfg = rp.config_portal(http)
            solver = CaptchaSolver()

            def token() -> str:
                return solver.recaptcha(cfg["sitekey"], rp.PORTAL_URL, version="v3", accion=rp.RECAPTCHA_ACCION)

            # ponytail: un token por endpoint (el portal reusa uno); compartirlo si en vivo REPUVE lo acepta.
            filas = con_token(token, lambda t: rp.enviar(http, rp.API_URL, cfg["rep"], tipo, valor, t), "REPUVE")
            advertencias: list[str] = []
            try:
                estatus, robo = rp.estatus_robo(
                    con_token(token, lambda t: rp.enviar(http, rp.API_PGJ, cfg["pgj"], tipo, valor, t), "REPUVE PGJ"))
            except (UpstreamError, TokenRechazado):
                estatus, robo = "", None
                advertencias.append("No se pudo consultar el estatus de robo (PGJ vía REPUVE): resultado desconocido.")

        base = {"tipo": tipo, "valor": valor, "fecha_consulta": datetime.now(timezone.utc).isoformat(),
                "fuente": rp.PORTAL_URL, "modo": "real", "simulated": False, "advertencias": advertencias}
        if not filas:
            return {**base, "encontrado": False, "vehiculo": None}
        f = filas[0]
        veh = VehiculoREPUVE(
            niv=f.get("VIN") or "", placa=f.get("PLACA") or "", marca=f.get("MARCA") or "",
            submarca=f.get("MODELO") or "", modelo=str(f.get("ANIO_MODELO") or ""), tipo=f.get("TIPO") or "",
            estado=f.get("ENTIDAD_EMPLACO") or "", estatus_robo=estatus, raw=f,
        ).to_dict()
        veh["tiene_reporte_robo"] = robo  # None = PGJ no respondió
        veh["linea"], veh["clase"] = f.get("LINEA"), f.get("CLASE")
        return {**base, "encontrado": True, "vehiculo": veh}

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
