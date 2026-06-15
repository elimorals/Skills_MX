"""Cliente mp_concilianet_profeco."""
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


NAMESPACE = "concilianet"
URL_CONCILIANET = "https://burocomercial.profeco.gob.mx"

PROVEEDORES_CONVENIO_2026 = [
    "Aeromexico", "Volaris", "VivaAerobus", "Telcel", "AT&T",
    "Movistar", "Telmex", "Megacable", "Izzi", "Totalplay",
    "Liverpool", "Palacio de Hierro", "Sears", "Coppel", "Elektra",
    "Rappi", "Uber Eats", "DiDi Food",
    "Mercado Libre", "Amazon Mexico",
    "Sephora", "Six Flags", "Cinepolis", "Cinemex",
    "BBVA", "Citibanamex", "Santander", "Banorte", "HSBC",
    "Hoteles City Express", "Booking", "Expedia", "Despegar",
]


class ConcilianetClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_proveedor(self, razon_social: str) -> dict[str, Any]:
        if not razon_social or len(razon_social) < 3:
            raise ValidationError(f"razon_social muy corta: {razon_social!r}")
        rs = (razon_social or "").strip().lower()
        tiene_convenio = any(p.lower() in rs or rs in p.lower() for p in PROVEEDORES_CONVENIO_2026)
        match = next((p for p in PROVEEDORES_CONVENIO_2026
                       if p.lower() in rs or rs in p.lower()), None)
        return mark_simulated({
            "razon_social_buscada": razon_social,
            "tiene_convenio_concilianet": tiene_convenio,
            "proveedor_matcheado": match,
            "ventaja_si_convenio": "Conciliación online sin necesidad de oficinas",
            "fuente": URL_CONCILIANET,
        })

    def estatus_caso(self, folio: str) -> dict[str, Any]:
        if not folio or len(folio) < 6:
            raise ValidationError(f"folio inválido: {folio!r}")
        last = sum(ord(c) for c in folio) % 5
        fases = ["registrada", "asignada_a_conciliador", "audiencia_programada",
                 "en_conciliacion", "resuelta"]
        return mark_simulated({
            "folio": folio,
            "fase_actual": fases[last],
            "porcentaje_avance": (last + 1) * 20,
            "proxima_audiencia": "2026-06-30 10:00" if last < 4 else None,
            "fuente": URL_CONCILIANET,
        })

    def listar_proveedores_convenio(self) -> dict[str, Any]:
        return {
            "total": len(PROVEEDORES_CONVENIO_2026),
            "proveedores": sorted(PROVEEDORES_CONVENIO_2026),
            "fuente": URL_CONCILIANET,
            "actualizado": "2026",
        }

    def registrar_queja(self, consumidor_curp_hash: str | None, proveedor: str,
                         descripcion: str, monto_reclamado_mxn: float | None = None) -> dict[str, Any]:
        if not proveedor:
            raise ValidationError("proveedor requerido")
        if not descripcion or len(descripcion) < 20:
            raise ValidationError("descripcion debe ser ≥20 caracteres")
        ahora = datetime.now(timezone.utc)
        folio = f"PROF-{ahora.strftime('%Y%m%d%H%M%S')}"
        return mark_simulated({
            "folio_queja": folio,
            "proveedor": proveedor,
            "monto_reclamado_mxn": monto_reclamado_mxn,
            "fase": "registrada",
            "tiempo_estimado_resolucion": "30-90 días naturales",
            "fecha_registro": ahora.isoformat(),
            "fuente": URL_CONCILIANET,
        })
