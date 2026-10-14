"""Cliente mp_merida_municipal.

Predial: isla.merida.gob.mx/serviciosinternet/predialmid está detrás de Radware
Bot Manager, que redirige a un reto hCaptcha (verificado 2026-10-14) → handoff
humano. La búsqueda es por dirección (calle + número), no por cuenta.
Multas estatales: sin portal público verificado (usar mp_multas_mx).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.portal_handoff import armar_handoff  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

NAMESPACE = "merida_mun"
URL_PREDIAL = "https://isla.merida.gob.mx/serviciosinternet/predialmid/index.php"


class MeridaMunClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_predial(self, calle: str, numero: str) -> dict:
        self.bitacora.log("consultar_predial", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"calle": calle, "numero": numero, "adeudo_total_mxn": 890.0})
        return armar_handoff(
            url=URL_PREDIAL,
            motivo="bot_manager",
            detalle="Radware Bot Manager presenta un reto hCaptcha antes del formulario.",
            pasos=[
                f"Abrir {URL_PREDIAL} y resolver el reto de verificación",
                f"Buscar por calle {calle} y número {numero}",
                "Leer el adeudo del predio en la tabla de resultados",
            ],
        )
