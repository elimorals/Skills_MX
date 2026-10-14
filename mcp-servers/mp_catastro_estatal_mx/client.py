"""Cliente mp_catastro_estatal_mx.

Estado real (2026-10-14): ningún catastro estatal del catálogo expone consulta
pública de valor por clave. IGECEM → handoff humano tras GET real; el resto →
UpstreamError explícito con el motivo (login, info-only, portal caído).
Datos simulados solo con PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import re
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
from shared.catastro_estatal import (  # noqa: E402
    CatastroEstatal,
    buscar_catastro,
    listar_catastros,
)
from shared.errors import NotFoundError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402
from shared.portal_handoff import IGECEM_EDOMEX, handoff_humano, mock_forzado  # noqa: E402

NAMESPACE = "catastro_estatal_mx"


class CatastroEstatalClient:
    def __init__(self, cache: FileCache | None = None, bitacora: Bitacora | None = None) -> None:
        self._cache = cache or FileCache(NAMESPACE)
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_valor(self, sistema: str, cuenta_catastral: str) -> dict[str, Any]:
        """Consulta valor catastral por clave catastral."""
        c = buscar_catastro(sistema)
        if c is None:
            raise NotFoundError(f"Sistema catastral '{sistema}' no en catálogo.")
        cuenta_catastral = cuenta_catastral.strip()
        if not re.match(c.identificador_regex, cuenta_catastral):
            raise ValidationError(
                f"Cuenta '{cuenta_catastral}' no matchea formato de {c.clave}: {c.identificador_regex}",
            )

        self._bitacora.log("consultar_valor", success=True,
                           params_summary={"sistema": c.clave, "cuenta_hash": self._bitacora.hash_sensitive(cuenta_catastral)})
        if mock_forzado():
            return self._mock(c, cuenta_catastral)
        if c.clave == "igecem":
            return handoff_humano(IGECEM_EDOMEX, sistema=c.clave)
        raise UpstreamError(
            f"{c.organismo} no expone consulta pública de valor catastral ({c.metodo}). {c.notas}",
            {"sistema": c.clave, "metodo": c.metodo, "portal": c.url_portal},
        )

    def listar_sistemas(self) -> dict[str, Any]:
        sistemas = listar_catastros()
        return {
            "total": len(sistemas),
            "sistemas": [{
                "clave": c.clave, "estado": c.nombre_estado, "organismo": c.organismo,
                "muns_cubre": c.cobertura_muns, "portal": c.url_portal,
                "metodo": c.metodo, "identificador": c.identificador_label,
            } for c in sistemas],
        }

    def _mock(self, c: CatastroEstatal, cuenta: str) -> dict[str, Any]:
        # Determinístico por último digit
        last = cuenta[-1] if cuenta and cuenta[-1].isdigit() else "5"
        valor_base = (int(last) + 1) * 850000  # 850K - 8.5M
        return mark_simulated({
            "sistema": c.clave,
            "estado": c.nombre_estado,
            "cuenta_catastral": cuenta,
            "valor_catastral_mxn": valor_base,
            "valor_comercial_aprox_mxn": round(valor_base * 1.45, 2),
            "superficie_terreno_m2": 250 + (int(last) * 35),
            "superficie_construccion_m2": 180 + (int(last) * 25),
            "uso_suelo": "HABITACIONAL" if int(last) < 6 else "MIXTO",
            "fecha_avaluo": "2025-08-15",
            "fuente": c.url_portal,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })
