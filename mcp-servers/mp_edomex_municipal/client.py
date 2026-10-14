"""Cliente mp_edomex_municipal.

Estado real (2026-10-14):
- Predial Toluca: httpx contra el portal de Tesorería (sin CAPTCHA).
- Predial otros municipios: Playwright genérico del catálogo central; si el
  portal falla se levanta UpstreamError (sin fallback a mock).
- Tenencia: portal estatal sin flujo automatizable verificado → handoff humano.
- Multas: Cloudflare Turnstile → handoff humano.

Datos simulados solo con PLUGINS_MX_MOCK=1.
"""

from __future__ import annotations

import sys
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
    EDOMEX_INFRACCIONES,
    EDOMEX_RECAUDACION,
    handoff_humano,
    mock_forzado,
)

from mp_edomex_municipal import mock_data, playwright_real, toluca  # noqa: E402
from mp_edomex_municipal.catalogos import MUNICIPIOS_PREDIAL_DIGITAL  # noqa: E402


NAMESPACE = "edomex_municipal_mcp"

# Fuente: notas de prensa 2026 que citan a la Secretaría de Finanzas EdoMex
# (N+, UnoTV). Confianza media: no se localizó el acuerdo de subsidio en Gaceta.
TENENCIA_EDOMEX_2026 = {
    "subsidio_100_pct_si_valor_factura_hasta_mxn": 638_000,
    "condiciones_subsidio": "Placas 2021 o posteriores (50% placas 2020), registro estatal y sin adeudos.",
    "refrendo_automovil_mxn": 990,
    "fuentes": [
        "https://www.nmas.com.mx/estado-de-mexico/cual-es-el-costo-refrendo-edomex-2026-como-obtener-subsidio-100-tenencia/",
        "https://www.unotv.com/estados/estado-de-mexico/subsidio-a-la-tenecia-en-edomex-2026-fechas-clave-y-quienes-pueden-tramitarlo/",
    ],
    "confianza": "media",
}


class EdomexMunicipalClient:
    def __init__(
        self,
        cache: FileCache | None = None,
        bitacora: Bitacora | None = None,
    ) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        for k in ("placa", "cuenta"):
            if k in safe:
                safe[f"{k}_hash"] = Bitacora.hash_sensitive(str(safe.pop(k)))
        self._bitacora.log(op, success=True, params_summary=safe)

    def consultar_predial(self, municipio: str, cuenta_predial: str) -> dict[str, Any]:
        if not municipio:
            raise ValidationError("municipio requerido")
        self._log("predial", {"municipio": municipio, "cuenta": cuenta_predial})
        if mock_forzado():
            return mark_simulated(mock_data.mock_predial_edomex(municipio, cuenta_predial))
        if playwright_real._normalizar_clave_municipio(municipio) == "toluca":
            return toluca.consultar(cuenta_predial)
        return playwright_real.predial_real(municipio, cuenta_predial)

    def consultar_tenencia(self, placa: str, ejercicio: int) -> dict[str, Any]:
        if not placa:
            raise ValidationError("placa requerida")
        self._log("tenencia", {"placa": placa, "ejercicio": ejercicio})
        if mock_forzado():
            return mark_simulated(mock_data.mock_tenencia_edomex(placa, ejercicio))
        return handoff_humano(
            EDOMEX_RECAUDACION,
            ejercicio=ejercicio,
            reglas_2026=TENENCIA_EDOMEX_2026 if ejercicio == 2026 else None,
        )

    def municipios_soportados_estructurado(self) -> list[dict[str, Any]]:
        """Lista municipios EdoMex con estado de validación desde el catálogo central."""
        return playwright_real.municipios_soportados()

    def consultar_multas(self, placa: str) -> dict[str, Any]:
        if not placa:
            raise ValidationError("placa requerida")
        self._log("multas", {"placa": placa})
        if mock_forzado():
            return mark_simulated(mock_data.mock_multas_edomex(placa))
        return handoff_humano(EDOMEX_INFRACCIONES)

    def municipios_soportados(self) -> list[str]:
        return MUNICIPIOS_PREDIAL_DIGITAL
