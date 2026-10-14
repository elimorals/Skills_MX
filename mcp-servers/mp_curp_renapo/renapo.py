"""Consulta RENAPO — verificación de existencia en padrón oficial.

Portal oficial: https://www.gob.mx/curp/ (verificado 2026-10-14):
- www.gob.mx está detrás de un challenge anti-bot de Akamai (`/_sec/verify`).
- El formulario carga reCAPTCHA Enterprise
  (site key 6Lfi0jcpAAAAAPfBiQkGzQR3gv8mDRkqPDHAy8hS).

No se resuelve ni se evade ninguno de los dos. Por eso el modo real devuelve un
**handoff humano**: URL, pasos y la CURP ya validada localmente (estructura +
dígito verificador) para que una persona complete la consulta.

Mock solo con PLUGINS_MX_MOCK=1 (respuestas `simulated: true`).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mp_curp_renapo.catalogos import ESTADOS_CURP  # noqa: E402
from mp_curp_renapo.validacion import (  # noqa: E402
    derivar_estado,
    derivar_fecha_nacimiento,
    derivar_sexo,
    validar_estructura,
)
from shared.bitacora import Bitacora  # noqa: E402
from shared.cache import FileCache  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import armar_handoff  # noqa: E402

NAMESPACE = "curp_renapo_mcp"
CACHE_DIAS = 90


PORTAL_URL = "https://www.gob.mx/curp/"


def handoff_renapo(curp: str, motivo: str = "consulta") -> dict[str, Any]:
    """RENAPO exige reCAPTCHA Enterprise + challenge Akamai: lo completa una persona."""
    pasos = [
        "Abrir https://www.gob.mx/curp/ en un navegador.",
        "Elegir la pestaña 'Clave Única de Registro de Población' y pegar la CURP.",
        "Completar la verificación de seguridad (reCAPTCHA) y pulsar 'Buscar'.",
    ]
    if motivo == "constancia":
        pasos.append("En el resultado, pulsar 'Descargar PDF' para obtener la constancia.")
    return armar_handoff(
        motivo="captcha",
        url=PORTAL_URL,
        pasos=pasos,
        campos_prellenados={"curp": curp},
    )


class RenapoClient:
    """Wrapper sobre la consulta a RENAPO con cache + modo mock."""

    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    @property
    def is_mock(self) -> bool:
        return os.environ.get("PLUGINS_MX_MOCK") == "1"

    @property
    def _mock_mode(self) -> bool:
        return self.is_mock

    async def consultar(self, curp: str) -> dict[str, Any]:
        """Consulta una CURP en RENAPO. Cache 90 días."""
        # Validación estructural primero — no tiene sentido consultar RENAPO
        # si la CURP ni siquiera pasa el dígito verificador.
        estructura = validar_estructura(curp)
        if not estructura["valido_estructura"]:
            raise ValidationError(
                "CURP inválida estructuralmente — RENAPO va a rechazar la consulta. "
                f"Errores: {'; '.join(estructura['errores'])}"
            )

        curp_norm = estructura["curp_normalizado"]
        cache_key = f"renapo_{curp_norm}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return dict(cached)

        if self._mock_mode:
            response = self._mock_consulta(curp_norm, estructura)
            self._cache.set(cache_key, response, ttl_hours=24 * CACHE_DIAS)
            self._bitacora.log(
                "consultar_renapo",
                success=True,
                params_summary={
                    "curp_hash": Bitacora.hash_sensitive(curp_norm),
                    "mode": "mock",
                },
            )
            return response

        self._bitacora.log(
            "consultar_renapo",
            success=True,
            params_summary={"curp_hash": Bitacora.hash_sensitive(curp_norm), "mode": "handoff"},
        )
        return {**handoff_renapo(curp_norm), "validacion_local": estructura}

    async def descargar_constancia(self, curp: str) -> dict[str, Any]:
        """Descarga el PDF de constancia CURP oficial.

        En mock devuelve metadata simulada. En real devuelve handoff humano
        (el portal exige reCAPTCHA Enterprise).
        """
        estructura = validar_estructura(curp)
        if not estructura["valido_estructura"]:
            raise ValidationError(
                "CURP inválida estructuralmente — no se puede descargar constancia."
            )

        if self._mock_mode:
            return mark_simulated(
                {
                    "curp": estructura["curp_normalizado"],
                    "constancia_pdf_path": (
                        f"/mock/constancias/{estructura['curp_normalizado']}.pdf"
                    ),
                    "constancia_pdf_bytes": 0,
                    "vigente_al": datetime.now(timezone.utc).isoformat(),
                    "nota": (
                        "Modo mock — no se generó PDF real. En modo Playwright "
                        "habría descargado y persistido el PDF en cache."
                    ),
                }
            )

        return handoff_renapo(estructura["curp_normalizado"], motivo="constancia")

    # ---------- mock helpers ----------

    @staticmethod
    def _mock_consulta(curp: str, estructura: dict[str, Any]) -> dict[str, Any]:
        """Construye respuesta plausible derivada de la propia CURP."""
        fecha = derivar_fecha_nacimiento(curp)
        sexo = derivar_sexo(curp)
        estado_t = derivar_estado(curp)

        # Heurística determinística para "estado": las CURPs que terminan en
        # 0-3 son "vigente" (90% de los casos reales), 4 = "duplicado", 5+ = vigente
        digito = int(curp[-1])
        if digito == 4:
            estado_renapo = "DUPLICADO"
            estado_descripcion = "CURP duplicada — existe otra persona con esta CURP."
        else:
            estado_renapo = "VIGENTE"
            estado_descripcion = "CURP vigente en padrón RENAPO."

        return mark_simulated(
            {
                "curp": curp,
                "estado_renapo": estado_renapo,
                "estado_descripcion": estado_descripcion,
                "datos_persona": {
                    "fecha_nacimiento": fecha.isoformat() if fecha else None,
                    "sexo": sexo,
                    "entidad_registro": estado_t[1] if estado_t else None,
                    "nacionalidad": "MEXICANA"
                    if estado_t and estado_t[0] != "NE"
                    else "EXTRANJERA",
                },
                "consultado_en": datetime.now(timezone.utc).isoformat(),
                "cache_ttl_dias": CACHE_DIAS,
            }
        )
