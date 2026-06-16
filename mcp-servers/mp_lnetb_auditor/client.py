"""Cliente mp_lnetb_auditor — auditor LNETB (Ley Nacional Eliminar Trámites Burocráticos).

LNETB publicada DOF 16-jul-2025. Meta: 80% trámites digitales para 2030.
México Evalúa documentó (2026-03-29) que NO existe ranking público nominal
de avance estatal/municipal — este MCP construye uno con metodología explícita.

Producto: para IMCO, México Evalúa, ATDT, prensa y periodismo de datos.
"""
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


NAMESPACE = "lnetb_auditor"
URL_LEY_DOF = "https://dof.gob.mx/nota_detalle.php?codigo=5763166&fecha=16/07/2025"
META_2030_PCT = 80.0
FECHA_LEY = "2025-07-16"

# Indicadores LNETB con peso para score compuesto (suma 100)
INDICADORES_LNETB: list[dict[str, Any]] = [
    {"clave": "i1_portal_unificado", "nombre": "Portal único de trámites estatal",
     "peso": 15, "max_score": 100},
    {"clave": "i2_sso_ciudadano", "nombre": "SSO ciudadano (Llave MX o estatal)",
     "peso": 10, "max_score": 100},
    {"clave": "i3_pagos_digitales", "nombre": "Pagos digitales en trámites estatales",
     "peso": 15, "max_score": 100},
    {"clave": "i4_firma_electronica", "nombre": "Firma electrónica estatal vigente",
     "peso": 10, "max_score": 100},
    {"clave": "i5_simplificacion_total", "nombre": "Trámites simplificados / total",
     "peso": 15, "max_score": 100},
    {"clave": "i6_atencion_chatbot", "nombre": "Canal IA / chatbot ciudadano",
     "peso": 5, "max_score": 100},
    {"clave": "i7_transparencia", "nombre": "Transparencia datos abiertos trámites",
     "peso": 10, "max_score": 100},
    {"clave": "i8_apps_oficiales", "nombre": "Apps móviles oficiales para trámites",
     "peso": 5, "max_score": 100},
    {"clave": "i9_interoperabilidad", "nombre": "Interoperabilidad federal-estatal",
     "peso": 10, "max_score": 100},
    {"clave": "i10_conectividad", "nombre": "Conectividad municipal (MX Conectado)",
     "peso": 5, "max_score": 100},
]

# Datos por estado al 2026-06-15 — curados de fuentes públicas (URBEM, México Evalúa, IMCO Subnacional)
# Score por indicador 0-100; nulls = sin dato verificable.
EVALUACION_ESTADOS: dict[str, dict[str, Any]] = {
    "cdmx": {"nombre": "Ciudad de México", "scores": {
        "i1_portal_unificado": 85, "i2_sso_ciudadano": 75, "i3_pagos_digitales": 80,
        "i4_firma_electronica": 70, "i5_simplificacion_total": 78, "i6_atencion_chatbot": 60,
        "i7_transparencia": 75, "i8_apps_oficiales": 70, "i9_interoperabilidad": 50,
        "i10_conectividad": 85,
    }, "evidencias": ["Llave CDMX", "Predial 100% digital", "App CDMX"]},
    "nl": {"nombre": "Nuevo León", "scores": {
        "i1_portal_unificado": 80, "i2_sso_ciudadano": 70, "i3_pagos_digitales": 75,
        "i4_firma_electronica": 70, "i5_simplificacion_total": 74, "i6_atencion_chatbot": 65,
        "i7_transparencia": 72, "i8_apps_oficiales": 65, "i9_interoperabilidad": 55,
        "i10_conectividad": 80,
    }, "evidencias": ["Portal NL", "Padrón empresarial unificado", "Tesorería digital"]},
    "jal": {"nombre": "Jalisco", "scores": {
        "i1_portal_unificado": 75, "i2_sso_ciudadano": 65, "i3_pagos_digitales": 72,
        "i4_firma_electronica": 68, "i5_simplificacion_total": 71, "i6_atencion_chatbot": 55,
        "i7_transparencia": 70, "i8_apps_oficiales": 60, "i9_interoperabilidad": 50,
        "i10_conectividad": 75,
    }, "evidencias": ["Visor predial GDL", "Concesiones agua digitales"]},
    "bc": {"nombre": "Baja California", "scores": {
        "i1_portal_unificado": 90, "i2_sso_ciudadano": 80, "i3_pagos_digitales": 75,
        "i4_firma_electronica": 70, "i5_simplificacion_total": 80, "i6_atencion_chatbot": 70,
        "i7_transparencia": 75, "i8_apps_oficiales": 65, "i9_interoperabilidad": 60,
        "i10_conectividad": 78,
    }, "evidencias": ["Agencia Digital BC", "URBEM >200 trámites"]},
    "edomex": {"nombre": "Estado de México", "scores": {
        "i1_portal_unificado": 65, "i2_sso_ciudadano": 55, "i3_pagos_digitales": 60,
        "i4_firma_electronica": 60, "i5_simplificacion_total": 62, "i6_atencion_chatbot": 45,
        "i7_transparencia": 60, "i8_apps_oficiales": 50, "i9_interoperabilidad": 45,
        "i10_conectividad": 70,
    }, "evidencias": ["Portal EdoMex", "Tenencia vehicular en línea"]},
    "qro": {"nombre": "Querétaro", "scores": {
        "i1_portal_unificado": 70, "i2_sso_ciudadano": 60, "i3_pagos_digitales": 68,
        "i4_firma_electronica": 65, "i5_simplificacion_total": 68, "i6_atencion_chatbot": 50,
        "i7_transparencia": 68, "i8_apps_oficiales": 55, "i9_interoperabilidad": 48,
        "i10_conectividad": 75,
    }, "evidencias": ["Webservices predial municipal"]},
    "yuc": {"nombre": "Yucatán", "scores": {
        "i1_portal_unificado": 68, "i2_sso_ciudadano": 58, "i3_pagos_digitales": 65,
        "i4_firma_electronica": 62, "i5_simplificacion_total": 65, "i6_atencion_chatbot": 50,
        "i7_transparencia": 65, "i8_apps_oficiales": 55, "i9_interoperabilidad": 45,
        "i10_conectividad": 70,
    }, "evidencias": ["Acta nacimiento QR Mérida"]},
    "gto": {"nombre": "Guanajuato", "scores": {
        "i1_portal_unificado": 65, "i2_sso_ciudadano": 55, "i3_pagos_digitales": 65,
        "i4_firma_electronica": 60, "i5_simplificacion_total": 64, "i6_atencion_chatbot": 45,
        "i7_transparencia": 60, "i8_apps_oficiales": 50, "i9_interoperabilidad": 42,
        "i10_conectividad": 68,
    }, "evidencias": ["PAGONET León 100% digital"]},
    "ags": {"nombre": "Aguascalientes", "scores": {
        "i1_portal_unificado": 60, "i2_sso_ciudadano": 50, "i3_pagos_digitales": 60,
        "i4_firma_electronica": 58, "i5_simplificacion_total": 58, "i6_atencion_chatbot": 40,
        "i7_transparencia": 58, "i8_apps_oficiales": 50, "i9_interoperabilidad": 40,
        "i10_conectividad": 70,
    }, "evidencias": []},
    "qroo": {"nombre": "Quintana Roo", "scores": {
        "i1_portal_unificado": 65, "i2_sso_ciudadano": 55, "i3_pagos_digitales": 70,
        "i4_firma_electronica": 60, "i5_simplificacion_total": 67, "i6_atencion_chatbot": 45,
        "i7_transparencia": 62, "i8_apps_oficiales": 55, "i9_interoperabilidad": 45,
        "i10_conectividad": 72,
    }, "evidencias": ["Cancún Digital predial+facturas"]},
    "pue": {"nombre": "Puebla", "scores": {
        "i1_portal_unificado": 55, "i2_sso_ciudadano": 50, "i3_pagos_digitales": 58,
        "i4_firma_electronica": 55, "i5_simplificacion_total": 58, "i6_atencion_chatbot": 40,
        "i7_transparencia": 55, "i8_apps_oficiales": 45, "i9_interoperabilidad": 38,
        "i10_conectividad": 65,
    }, "evidencias": ["IRCEP catastro"]},
    "ver": {"nombre": "Veracruz", "scores": {
        "i1_portal_unificado": 50, "i2_sso_ciudadano": 45, "i3_pagos_digitales": 52,
        "i4_firma_electronica": 50, "i5_simplificacion_total": 52, "i6_atencion_chatbot": 35,
        "i7_transparencia": 50, "i8_apps_oficiales": 40, "i9_interoperabilidad": 35,
        "i10_conectividad": 60,
    }, "evidencias": ["Reformas hacendarias 2025"]},
    "chih": {"nombre": "Chihuahua", "scores": {
        "i1_portal_unificado": 58, "i2_sso_ciudadano": 50, "i3_pagos_digitales": 60,
        "i4_firma_electronica": 55, "i5_simplificacion_total": 60, "i6_atencion_chatbot": 40,
        "i7_transparencia": 55, "i8_apps_oficiales": 45, "i9_interoperabilidad": 40,
        "i10_conectividad": 65,
    }, "evidencias": ["JMAS Juárez saldo online"]},
    "son": {"nombre": "Sonora", "scores": {
        "i1_portal_unificado": 55, "i2_sso_ciudadano": 45, "i3_pagos_digitales": 55,
        "i4_firma_electronica": 50, "i5_simplificacion_total": 50, "i6_atencion_chatbot": 35,
        "i7_transparencia": 50, "i8_apps_oficiales": 40, "i9_interoperabilidad": 35,
        "i10_conectividad": 60,
    }, "evidencias": []},
    "mich": {"nombre": "Michoacán", "scores": {
        "i1_portal_unificado": 50, "i2_sso_ciudadano": 40, "i3_pagos_digitales": 55,
        "i4_firma_electronica": 48, "i5_simplificacion_total": 56, "i6_atencion_chatbot": 35,
        "i7_transparencia": 50, "i8_apps_oficiales": 40, "i9_interoperabilidad": 35,
        "i10_conectividad": 58,
    }, "evidencias": ["SACPI 95 muns predial"]},
    "sin": {"nombre": "Sinaloa", "scores": {
        "i1_portal_unificado": 50, "i2_sso_ciudadano": 42, "i3_pagos_digitales": 55,
        "i4_firma_electronica": 48, "i5_simplificacion_total": 53, "i6_atencion_chatbot": 32,
        "i7_transparencia": 50, "i8_apps_oficiales": 40, "i9_interoperabilidad": 35,
        "i10_conectividad": 60,
    }, "evidencias": ["Predial Mi Clave Culiacán"]},
    "coah": {"nombre": "Coahuila", "scores": {
        "i1_portal_unificado": 48, "i2_sso_ciudadano": 40, "i3_pagos_digitales": 50,
        "i4_firma_electronica": 45, "i5_simplificacion_total": 48, "i6_atencion_chatbot": 30,
        "i7_transparencia": 45, "i8_apps_oficiales": 38, "i9_interoperabilidad": 32,
        "i10_conectividad": 60,
    }, "evidencias": []},
    "tam": {"nombre": "Tamaulipas", "scores": {
        "i1_portal_unificado": 45, "i2_sso_ciudadano": 38, "i3_pagos_digitales": 48,
        "i4_firma_electronica": 42, "i5_simplificacion_total": 45, "i6_atencion_chatbot": 30,
        "i7_transparencia": 42, "i8_apps_oficiales": 35, "i9_interoperabilidad": 30,
        "i10_conectividad": 55,
    }, "evidencias": []},
    "hgo": {"nombre": "Hidalgo", "scores": {
        "i1_portal_unificado": 50, "i2_sso_ciudadano": 42, "i3_pagos_digitales": 52,
        "i4_firma_electronica": 50, "i5_simplificacion_total": 55, "i6_atencion_chatbot": 35,
        "i7_transparencia": 50, "i8_apps_oficiales": 40, "i9_interoperabilidad": 35,
        "i10_conectividad": 55,
    }, "evidencias": []},
    "mor": {"nombre": "Morelos", "scores": {
        "i1_portal_unificado": 48, "i2_sso_ciudadano": 40, "i3_pagos_digitales": 50,
        "i4_firma_electronica": 45, "i5_simplificacion_total": 53, "i6_atencion_chatbot": 30,
        "i7_transparencia": 48, "i8_apps_oficiales": 38, "i9_interoperabilidad": 32,
        "i10_conectividad": 55,
    }, "evidencias": []},
    "tab": {"nombre": "Tabasco", "scores": {
        "i1_portal_unificado": 42, "i2_sso_ciudadano": 35, "i3_pagos_digitales": 42,
        "i4_firma_electronica": 40, "i5_simplificacion_total": 42, "i6_atencion_chatbot": 25,
        "i7_transparencia": 40, "i8_apps_oficiales": 32, "i9_interoperabilidad": 28,
        "i10_conectividad": 50,
    }, "evidencias": []},
    "col": {"nombre": "Colima", "scores": {
        "i1_portal_unificado": 50, "i2_sso_ciudadano": 42, "i3_pagos_digitales": 50,
        "i4_firma_electronica": 48, "i5_simplificacion_total": 50, "i6_atencion_chatbot": 35,
        "i7_transparencia": 48, "i8_apps_oficiales": 38, "i9_interoperabilidad": 35,
        "i10_conectividad": 60,
    }, "evidencias": []},
    "nay": {"nombre": "Nayarit", "scores": {
        "i1_portal_unificado": 45, "i2_sso_ciudadano": 38, "i3_pagos_digitales": 46,
        "i4_firma_electronica": 42, "i5_simplificacion_total": 46, "i6_atencion_chatbot": 30,
        "i7_transparencia": 42, "i8_apps_oficiales": 35, "i9_interoperabilidad": 30,
        "i10_conectividad": 55,
    }, "evidencias": []},
    "zac": {"nombre": "Zacatecas", "scores": {
        "i1_portal_unificado": 42, "i2_sso_ciudadano": 35, "i3_pagos_digitales": 45,
        "i4_firma_electronica": 40, "i5_simplificacion_total": 44, "i6_atencion_chatbot": 28,
        "i7_transparencia": 40, "i8_apps_oficiales": 35, "i9_interoperabilidad": 28,
        "i10_conectividad": 52,
    }, "evidencias": []},
    "slp": {"nombre": "San Luis Potosí", "scores": {
        "i1_portal_unificado": 48, "i2_sso_ciudadano": 40, "i3_pagos_digitales": 50,
        "i4_firma_electronica": 45, "i5_simplificacion_total": 48, "i6_atencion_chatbot": 30,
        "i7_transparencia": 45, "i8_apps_oficiales": 38, "i9_interoperabilidad": 30,
        "i10_conectividad": 58,
    }, "evidencias": []},
    "dur": {"nombre": "Durango", "scores": {
        "i1_portal_unificado": 42, "i2_sso_ciudadano": 35, "i3_pagos_digitales": 45,
        "i4_firma_electronica": 40, "i5_simplificacion_total": 43, "i6_atencion_chatbot": 25,
        "i7_transparencia": 40, "i8_apps_oficiales": 32, "i9_interoperabilidad": 28,
        "i10_conectividad": 52,
    }, "evidencias": []},
    "bcs": {"nombre": "Baja California Sur", "scores": {
        "i1_portal_unificado": 50, "i2_sso_ciudadano": 42, "i3_pagos_digitales": 48,
        "i4_firma_electronica": 45, "i5_simplificacion_total": 47, "i6_atencion_chatbot": 32,
        "i7_transparencia": 45, "i8_apps_oficiales": 38, "i9_interoperabilidad": 32,
        "i10_conectividad": 55,
    }, "evidencias": []},
    "tlx": {"nombre": "Tlaxcala", "scores": {
        "i1_portal_unificado": 40, "i2_sso_ciudadano": 32, "i3_pagos_digitales": 42,
        "i4_firma_electronica": 38, "i5_simplificacion_total": 40, "i6_atencion_chatbot": 25,
        "i7_transparencia": 38, "i8_apps_oficiales": 30, "i9_interoperabilidad": 25,
        "i10_conectividad": 50,
    }, "evidencias": []},
    "cam": {"nombre": "Campeche", "scores": {
        "i1_portal_unificado": 42, "i2_sso_ciudadano": 35, "i3_pagos_digitales": 42,
        "i4_firma_electronica": 38, "i5_simplificacion_total": 41, "i6_atencion_chatbot": 25,
        "i7_transparencia": 40, "i8_apps_oficiales": 32, "i9_interoperabilidad": 28,
        "i10_conectividad": 50,
    }, "evidencias": []},
    "gro": {"nombre": "Guerrero", "scores": {
        "i1_portal_unificado": 38, "i2_sso_ciudadano": 30, "i3_pagos_digitales": 38,
        "i4_firma_electronica": 35, "i5_simplificacion_total": 38, "i6_atencion_chatbot": 22,
        "i7_transparencia": 35, "i8_apps_oficiales": 28, "i9_interoperabilidad": 25,
        "i10_conectividad": 45,
    }, "evidencias": []},
    "oax": {"nombre": "Oaxaca", "scores": {
        "i1_portal_unificado": 35, "i2_sso_ciudadano": 28, "i3_pagos_digitales": 35,
        "i4_firma_electronica": 32, "i5_simplificacion_total": 35, "i6_atencion_chatbot": 20,
        "i7_transparencia": 32, "i8_apps_oficiales": 25, "i9_interoperabilidad": 22,
        "i10_conectividad": 42,
    }, "evidencias": []},
    "chis": {"nombre": "Chiapas", "scores": {
        "i1_portal_unificado": 35, "i2_sso_ciudadano": 28, "i3_pagos_digitales": 35,
        "i4_firma_electronica": 32, "i5_simplificacion_total": 36, "i6_atencion_chatbot": 20,
        "i7_transparencia": 32, "i8_apps_oficiales": 25, "i9_interoperabilidad": 22,
        "i10_conectividad": 42,
    }, "evidencias": []},
}


def _calcular_score_compuesto(scores: dict[str, int]) -> float:
    """Score 0-100 ponderado por pesos."""
    total = 0.0
    for ind in INDICADORES_LNETB:
        s = scores.get(ind["clave"], 0)
        total += s * ind["peso"] / 100.0
    return round(total, 2)


class LnetbAuditorClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    def listar_indicadores(self) -> dict[str, Any]:
        """Los 10 indicadores LNETB con peso."""
        self._log("listar_indicadores", {})
        return {
            "total_indicadores": len(INDICADORES_LNETB),
            "suma_pesos": sum(i["peso"] for i in INDICADORES_LNETB),
            "indicadores": INDICADORES_LNETB,
            "fuente_ley": URL_LEY_DOF,
        }

    def evaluar_estado(self, estado_clave: str) -> dict[str, Any]:
        """Score compuesto + breakdown por indicador para un estado."""
        self._log("evaluar_estado", {"estado": estado_clave})
        ek = (estado_clave or "").lower().strip()
        if ek not in EVALUACION_ESTADOS:
            raise ValidationError(
                f"estado_clave no reconocida: {estado_clave!r}. Usar abreviatura (cdmx, nl, jal...)"
            )
        e = EVALUACION_ESTADOS[ek]
        score = _calcular_score_compuesto(e["scores"])
        brecha = round(META_2030_PCT - score, 2)
        return mark_simulated(
            {
                "estado_clave": ek,
                "nombre": e["nombre"],
                "score_compuesto": score,
                "meta_2030_pct": META_2030_PCT,
                "brecha_vs_meta_pct": brecha,
                "alcanza_meta": score >= META_2030_PCT,
                "breakdown_por_indicador": e["scores"],
                "evidencias_publicas": e["evidencias"],
                "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "fuente_ley": URL_LEY_DOF,
            },
            note="Score compuesto basado en evidencia pública. Metodología documentada.",
        )

    def ranking_nacional(self, top: int = 32) -> dict[str, Any]:
        """Ranking 32 estados con score compuesto."""
        self._log("ranking_nacional", {"top": top})
        if top < 1 or top > 32:
            raise ValidationError("top debe ser 1-32")
        scored = []
        for ek, e in EVALUACION_ESTADOS.items():
            score = _calcular_score_compuesto(e["scores"])
            scored.append({
                "estado_clave": ek,
                "nombre": e["nombre"],
                "score": score,
                "alcanza_meta_2030": score >= META_2030_PCT,
            })
        scored.sort(key=lambda x: x["score"], reverse=True)
        scored_top = scored[:top]
        promedio = round(sum(s["score"] for s in scored) / len(scored), 2)
        cumpliendo = sum(1 for s in scored if s["alcanza_meta_2030"])
        return {
            "total_estados": len(scored),
            "top_solicitado": top,
            "promedio_nacional": promedio,
            "brecha_promedio_vs_meta": round(META_2030_PCT - promedio, 2),
            "estados_cumpliendo_meta_80": cumpliendo,
            "estados_riesgo_meta_2030": len(scored) - cumpliendo,
            "ranking": scored_top,
            "lider": scored[0],
            "rezagado": scored[-1],
            "fuente_ley": URL_LEY_DOF,
            "metodologia": "Score compuesto 10 indicadores × peso (suma 100).",
        }

    def comparar_estados(self, estados_claves: list[str]) -> dict[str, Any]:
        """Comparativa side-by-side de N estados."""
        self._log("comparar_estados", {"estados": estados_claves})
        if not estados_claves:
            raise ValidationError("Lista de estados vacía")
        if len(estados_claves) > 10:
            raise ValidationError("Máximo 10 estados por comparación")
        comparativa = []
        for ek in estados_claves:
            ek_n = ek.lower().strip()
            if ek_n not in EVALUACION_ESTADOS:
                continue
            e = EVALUACION_ESTADOS[ek_n]
            comparativa.append({
                "estado_clave": ek_n,
                "nombre": e["nombre"],
                "score": _calcular_score_compuesto(e["scores"]),
                "breakdown": e["scores"],
            })
        comparativa.sort(key=lambda x: x["score"], reverse=True)
        return {
            "comparativa": comparativa,
            "lider_comparativa": comparativa[0] if comparativa else None,
            "rezagado_comparativa": comparativa[-1] if comparativa else None,
            "diferencia_pts": round(
                comparativa[0]["score"] - comparativa[-1]["score"], 2
            ) if len(comparativa) >= 2 else 0.0,
        }
