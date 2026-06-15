"""Cliente mp_simplifica_ciudadano."""
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
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "simplifica_ciudadano"
URL_LEY_NACIONAL = "https://www.dof.gob.mx/nota_detalle.php?codigo=ley-nacional-eliminar-tramites-burocraticos-2025"
FECHA_VIGENCIA_LEY = "2025-07-16"  # DOF


# Catálogo curado de simplificaciones reportadas por estado (mock representativo)
PROGRESO_POR_ESTADO_2026: dict[str, dict] = {
    "cdmx":   {"avance_pct": 78, "tramites_simplificados": 124,
                "destacados": ["Llave CDMX SSO", "Predial 100% digital", "Acta nacimiento QR"]},
    "edomex": {"avance_pct": 62, "tramites_simplificados": 96,
                "destacados": ["Tenencia vehicular en línea", "Registro empresa 72h"]},
    "jal":    {"avance_pct": 71, "tramites_simplificados": 108,
                "destacados": ["Visor predial GDL", "Concesiones agua digitales"]},
    "nl":     {"avance_pct": 74, "tramites_simplificados": 102,
                "destacados": ["Control vehicular online", "Padrón empresarial unificado"]},
    "qro":    {"avance_pct": 68, "tramites_simplificados": 87,
                "destacados": ["Webservices predial municipal"]},
    "yuc":    {"avance_pct": 65, "tramites_simplificados": 82,
                "destacados": ["Acta nacimiento qr Mérida"]},
    "bc":     {"avance_pct": 55, "tramites_simplificados": 70,
                "destacados": ["Pagos integrados Mexicali"]},
    "gto":    {"avance_pct": 64, "tramites_simplificados": 85,
                "destacados": ["PAGONET León 100% digital"]},
    "pue":    {"avance_pct": 58, "tramites_simplificados": 75,
                "destacados": ["IRCEP catastro"]},
    "ver":    {"avance_pct": 52, "tramites_simplificados": 68,
                "destacados": ["Reformas hacendarias 2025"]},
    "chih":   {"avance_pct": 60, "tramites_simplificados": 78,
                "destacados": ["JMAS Juárez saldo online"]},
    "mich":   {"avance_pct": 56, "tramites_simplificados": 72,
                "destacados": ["SACPI 95 muns predial"]},
    "son":    {"avance_pct": 50, "tramites_simplificados": 65, "destacados": []},
    "qroo":   {"avance_pct": 67, "tramites_simplificados": 86,
                "destacados": ["Cancún Digital predial+facturas"]},
    "sin":    {"avance_pct": 53, "tramites_simplificados": 68,
                "destacados": ["Predial Mi Clave Culiacán"]},
    "coah":   {"avance_pct": 48, "tramites_simplificados": 60, "destacados": []},
    "tam":    {"avance_pct": 45, "tramites_simplificados": 58, "destacados": []},
    "tab":    {"avance_pct": 42, "tramites_simplificados": 54, "destacados": []},
    "hgo":    {"avance_pct": 55, "tramites_simplificados": 70, "destacados": []},
    "mor":    {"avance_pct": 53, "tramites_simplificados": 68, "destacados": []},
    "gro":    {"avance_pct": 38, "tramites_simplificados": 48, "destacados": []},
    "oax":    {"avance_pct": 35, "tramites_simplificados": 44, "destacados": []},
    "chis":   {"avance_pct": 36, "tramites_simplificados": 46, "destacados": []},
    "cam":    {"avance_pct": 41, "tramites_simplificados": 52, "destacados": []},
    "ags":    {"avance_pct": 58, "tramites_simplificados": 75, "destacados": []},
    "col":    {"avance_pct": 50, "tramites_simplificados": 64, "destacados": []},
    "nay":    {"avance_pct": 46, "tramites_simplificados": 58, "destacados": []},
    "zac":    {"avance_pct": 44, "tramites_simplificados": 56, "destacados": []},
    "slp":    {"avance_pct": 48, "tramites_simplificados": 62, "destacados": []},
    "tlx":    {"avance_pct": 40, "tramites_simplificados": 50, "destacados": []},
    "dur":    {"avance_pct": 43, "tramites_simplificados": 55, "destacados": []},
    "bcs":    {"avance_pct": 47, "tramites_simplificados": 60, "destacados": []},
}


class SimplificaCiudadanoClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def estado(self, estado_clave: str) -> dict[str, Any]:
        ek = (estado_clave or "").lower().strip()
        if ek not in PROGRESO_POR_ESTADO_2026:
            raise ValidationError(f"estado_clave no reconocida: {estado_clave!r}. "
                                   f"Usar abreviatura 2-4 chars (cdmx, edomex, jal, etc.)")
        info = PROGRESO_POR_ESTADO_2026[ek]
        return mark_simulated({
            "estado_clave": ek,
            **info,
            "fecha_vigencia_ley": FECHA_VIGENCIA_LEY,
            "fuente": URL_LEY_NACIONAL,
            "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        })

    def tracker_nacional(self) -> dict[str, Any]:
        total_tramites = sum(v["tramites_simplificados"] for v in PROGRESO_POR_ESTADO_2026.values())
        avance_promedio = sum(v["avance_pct"] for v in PROGRESO_POR_ESTADO_2026.values()) / len(PROGRESO_POR_ESTADO_2026)
        return {
            "total_estados_monitoreados": len(PROGRESO_POR_ESTADO_2026),
            "total_tramites_simplificados_aprox": total_tramites,
            "avance_promedio_nacional_pct": round(avance_promedio, 1),
            "estados_top_3": sorted(PROGRESO_POR_ESTADO_2026.items(),
                                     key=lambda x: x[1]["avance_pct"], reverse=True)[:3],
            "estados_rezagados_top_3": sorted(PROGRESO_POR_ESTADO_2026.items(),
                                               key=lambda x: x[1]["avance_pct"])[:3],
            "fecha_vigencia_ley": FECHA_VIGENCIA_LEY,
            "fuente": URL_LEY_NACIONAL,
        }

    def comparar_estados(self, estados_claves: list[str]) -> dict[str, Any]:
        if not estados_claves:
            raise ValidationError("Lista de estados vacía")
        if len(estados_claves) > 32:
            raise ValidationError("Máximo 32 estados")
        comparacion = []
        for ek in estados_claves:
            e = ek.lower().strip()
            if e not in PROGRESO_POR_ESTADO_2026:
                continue
            comparacion.append({"estado": e, **PROGRESO_POR_ESTADO_2026[e]})
        comparacion.sort(key=lambda x: x["avance_pct"], reverse=True)
        return {
            "comparacion": comparacion,
            "lider": comparacion[0] if comparacion else None,
            "rezagado": comparacion[-1] if comparacion else None,
        }
