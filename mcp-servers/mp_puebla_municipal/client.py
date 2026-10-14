"""Cliente mp_puebla_municipal.

Predial: srvappayt.pueblacapital.gob.mx:7016/pabel/iniciopredial pide cuenta +
delegación + LC + CAPTCHA de imagen (campo `answer`), verificado 2026-10-14 →
handoff humano. Multas estatales: sin portal público verificado (usar mp_multas_mx).
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

NAMESPACE = "puebla_mun"
URL_PREDIAL = "https://srvappayt.pueblacapital.gob.mx:7016/pabel/iniciopredial"


class PueblaMunClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self.bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_predial(self, cuenta_predial: str) -> dict:
        self.bitacora.log("consultar_predial", success=True, params_summary={})
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated({"cuenta_predial": cuenta_predial, "adeudo_total_mxn": 1700.0})
        return armar_handoff(
            url=URL_PREDIAL,
            motivo="captcha",
            detalle="El portal exige un CAPTCHA de imagen junto con cuenta, delegación y LC.",
            pasos=[
                f"Abrir {URL_PREDIAL}",
                f"Capturar cuenta {cuenta_predial}, delegación y LC (vienen en el recibo)",
                "Escribir el texto del CAPTCHA y pulsar 'Consultar'",
            ],
        )
