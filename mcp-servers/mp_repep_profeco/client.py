"""Cliente mp_repep_profeco — REPEP no-llamadas + filtro lote."""
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
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "repep_profeco"
URL_REPEP = "https://repep.profeco.gob.mx"

TEL_RE = re.compile(r"^\d{10}$")


def _normalizar_telefono(tel: str) -> str:
    t = (tel or "").strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if t.startswith("+52"):
        t = t[3:]
    if t.startswith("52") and len(t) == 12:
        t = t[2:]
    if not TEL_RE.match(t):
        raise ValidationError(f"Teléfono inválido (10 dígitos esperados): {tel!r}")
    return t


class REPEPClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar(self, telefono: str) -> dict[str, Any]:
        tel = _normalizar_telefono(telefono)
        last = int(tel[-1])
        inscrito = last % 3 != 0  # ~66% inscritos en mock
        self._bitacora.log("consultar", success=True,
                           params_summary={"tel_hash": self._bitacora.hash_sensitive(tel)})
        return mark_simulated({
            "telefono": tel,
            "inscrito_repep": inscrito,
            "puede_contactar": not inscrito,
            "consecuencia_si_contactas": (
                "Multa PROFECO 100-5000 UMAs" if inscrito else "Ninguna"
            ),
            "fuente": URL_REPEP,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def filtrar_lote(self, telefonos: list[str]) -> dict[str, Any]:
        if not telefonos:
            raise ValidationError("Lote vacío")
        if len(telefonos) > 5000:
            raise ValidationError("Lote excede límite de 5000 teléfonos")
        contactables = []
        bloqueados = []
        for t in telefonos:
            try:
                t_norm = _normalizar_telefono(t)
            except ValidationError:
                continue
            last = int(t_norm[-1])
            if last % 3 != 0:
                bloqueados.append(t_norm)
            else:
                contactables.append(t_norm)
        return mark_simulated({
            "total_input": len(telefonos),
            "contactables": contactables,
            "bloqueados_repep": bloqueados,
            "stats": {
                "contactables_count": len(contactables),
                "bloqueados_count": len(bloqueados),
                "tasa_bloqueo_pct": round(100 * len(bloqueados) / max(1, len(telefonos)), 1),
            },
        })

    def inscribir(self, telefono: str, propietario_curp: str | None = None) -> dict[str, Any]:
        tel = _normalizar_telefono(telefono)
        return mark_simulated({
            "telefono": tel,
            "inscripcion_exitosa": True,
            "fecha_efectiva": "30 días naturales",
            "vigencia": "2 años renovables",
            "fuente": URL_REPEP,
        })

    def estadisticas(self) -> dict[str, Any]:
        return {
            "universo_aproximado_lineas_mx": 130_000_000,
            "inscritos_repep_aprox_mock": 22_000_000,
            "multa_min_uma": 100,
            "multa_max_uma": 5000,
            "fuente": URL_REPEP,
        }
