"""Cliente mp_guadalajara_municipal.

Predial: pagoenlinea.guadalajara.gob.mx/impuestopredial (Angular) exige reCAPTCHA
v2 antes de `consulta_adeudo` (main.js, verificado 2026-10-14) → handoff humano.
Adeudos vehiculares Jalisco (estatal): gobiernoenlinea1.jalisco.gob.mx también con
reCAPTCHA → handoff humano.
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

NAMESPACE = "guadalajara_mun"
URL_PREDIAL = "https://pagoenlinea.guadalajara.gob.mx/impuestopredial/"
URL_VEHICULAR_JAL = "https://gobiernoenlinea1.jalisco.gob.mx/serviciosVehiculares/adeudos"


class GuadalajaraMunClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_predial(self, cuenta_predial: str) -> dict:
        self.bitacora.log("consultar_predial", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"cuenta_predial": cuenta_predial, "adeudo_total_mxn": 2100.0})
        return armar_handoff(
            url=URL_PREDIAL,
            motivo="captcha",
            detalle="El portal exige reCAPTCHA v2 antes de mostrar el adeudo.",
            pasos=[
                f"Abrir {URL_PREDIAL}",
                f"Elegir recaudadora y tipo, capturar la cuenta {cuenta_predial}",
                "Resolver el reCAPTCHA y pulsar 'Consultar Adeudo Predial'",
            ],
        )

    def consultar_adeudos_vehiculares(self, placa: str) -> dict:
        self.bitacora.log("consultar_adeudos_vehiculares", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"placa": placa, "adeudo_total_mxn": 640.0})
        return armar_handoff(
            url=URL_VEHICULAR_JAL,
            motivo="captcha",
            detalle="Adeudos vehiculares de Jalisco (refrendo/multas estatales); el portal exige reCAPTCHA.",
            pasos=[
                f"Abrir {URL_VEHICULAR_JAL}",
                f"Capturar la placa {placa} (y número de serie si lo pide)",
                "Resolver el reCAPTCHA y pulsar 'Consultar'",
            ],
        )
