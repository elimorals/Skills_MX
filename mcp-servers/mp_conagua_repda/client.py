"""Cliente mp_conagua_repda — REPDA + reportes semestrales + LFD."""
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "conagua_repda"
URL_REPDA = "https://www.gob.mx/conagua/acciones-y-programas/registro-publico-de-derechos-de-agua-repda"

TipoUso = Literal["industrial", "agropecuario", "publico_urbano", "domestico",
                   "acuacola", "servicios", "comercio", "pecuario", "agricola",
                   "multiples_usos", "termoelectrico"]

# Cuotas Ley Federal de Derechos 2026 (mock simplificado por zona disponibilidad)
# Zonas disponibilidad: 1 (mayor escasez) → 9 (mayor disponibilidad)
TARIFA_LFD_2026_POR_M3 = {
    1: 27.50,
    2: 22.10,
    3: 18.00,
    4: 13.20,
    5: 9.80,
    6: 6.50,
    7: 3.20,
    8: 1.50,
    9: 0.62,
}

# Umbrales medición obligatoria (m³/año)
UMBRAL_MEDIDOR_OBLIGATORIO_M3 = 150_000

NUM_TITULO_RE = re.compile(r"^\d{2}[A-Z]{3}\d{6}/\d{2}[A-Z]{4}\d{2}$|^\d{8,12}$")


class CONAGUARepdaClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def consultar_titular(self, identificador: str) -> dict[str, Any]:
        """Consulta titular (por RFC o número de título)."""
        identificador = (identificador or "").strip()
        if len(identificador) < 8:
            raise ValidationError(f"identificador inválido: {identificador!r}")

        suffix = sum(ord(c) for c in identificador) % 10
        n_permisos = max(1, suffix % 4)
        permisos = []
        for i in range(n_permisos):
            permisos.append({
                "num_titulo": f"02SON{100000+i:06d}/{20+i:02d}HSGS{i:02d}",
                "tipo_uso": ["industrial", "agropecuario", "servicios"][i % 3],
                "volumen_concedido_m3_anual": 50_000 + i * 75_000,
                "vigente": True,
                "fecha_vencimiento": "2030-12-31",
            })

        self._bitacora.log("consultar_titular", success=True,
                           params_summary={"id_hash": self._bitacora.hash_sensitive(identificador)})
        return mark_simulated({
            "identificador": identificador,
            "total_permisos": len(permisos),
            "permisos": permisos,
            "fuente": URL_REPDA,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
        })

    def estado_reporte_semestral(self, num_titulo: str, periodo: str) -> dict[str, Any]:
        if not NUM_TITULO_RE.match(num_titulo or ""):
            raise ValidationError(f"num_titulo inválido: {num_titulo!r}")
        if periodo not in {"1er_semestre", "2do_semestre"}:
            raise ValidationError("periodo debe ser '1er_semestre' o '2do_semestre'")

        last = int(num_titulo[-2]) if num_titulo[-2:].isdigit() else 5
        presentado = last % 2 == 0
        return mark_simulated({
            "num_titulo": num_titulo,
            "periodo": periodo,
            "presentado": presentado,
            "fecha_limite": "31-julio" if periodo == "1er_semestre" else "31-enero",
            "accion_si_no_presentado": "Presentar de inmediato + posible multa "
                                       "Art. 119 Ley Aguas Nacionales",
        })

    def calcular_pago_lfd(self, num_titulo: str, m3_extraidos: float,
                          zona_disponibilidad: int) -> dict[str, Any]:
        if not NUM_TITULO_RE.match(num_titulo or ""):
            raise ValidationError(f"num_titulo inválido: {num_titulo!r}")
        if m3_extraidos < 0:
            raise ValidationError("m3 negativos")
        if zona_disponibilidad not in TARIFA_LFD_2026_POR_M3:
            raise ValidationError("zona_disponibilidad debe ser 1-9")

        cuota_m3 = TARIFA_LFD_2026_POR_M3[zona_disponibilidad]
        cuota_total = m3_extraidos * cuota_m3
        return mark_simulated({
            "num_titulo": num_titulo,
            "m3_extraidos": m3_extraidos,
            "zona_disponibilidad": zona_disponibilidad,
            "cuota_m3_mxn": cuota_m3,
            "cuota_total_mxn": round(cuota_total, 2),
            "trimestral_estimado_mxn": round(cuota_total / 4, 2),
            "base_legal": "Ley Federal de Derechos (cuotas 2026)",
        })

    def consultar_vigencia(self, num_titulo: str) -> dict[str, Any]:
        if not NUM_TITULO_RE.match(num_titulo or ""):
            raise ValidationError(f"num_titulo inválido: {num_titulo!r}")
        last = sum(ord(c) for c in num_titulo) % 30
        return mark_simulated({
            "num_titulo": num_titulo,
            "vigente": True,
            "anos_restantes": last,
            "fecha_renovacion_anticipada": "5 años antes del vencimiento",
        })

    def requiere_medidor(self, volumen_anual_m3: float) -> dict[str, Any]:
        if volumen_anual_m3 < 0:
            raise ValidationError("volumen negativo")
        return {
            "volumen_anual_m3": volumen_anual_m3,
            "umbral_mxn": UMBRAL_MEDIDOR_OBLIGATORIO_M3,
            "requiere_medidor_obligatorio": volumen_anual_m3 > UMBRAL_MEDIDOR_OBLIGATORIO_M3,
            "base_legal": "Ley Aguas Nacionales — extracciones >150,000 m³/año",
        }

    def listar_tipos_uso(self) -> dict[str, Any]:
        return {
            "tipos_uso": [
                "industrial", "agropecuario", "publico_urbano", "domestico",
                "acuacola", "servicios", "comercio", "pecuario", "agricola",
                "multiples_usos", "termoelectrico",
            ],
            "fuente": URL_REPDA,
        }
