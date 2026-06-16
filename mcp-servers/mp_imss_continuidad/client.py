"""Cliente mp_imss_continuidad — adapter para licitación IMSS Continuidad Operativa.

Target: licitación IMSS publicada **mayo 2026** "Continuidad Operativa de Sistemas
Sustantivos" (Centro Continuidad Operativa). Subcontrato MIPYME bajo integradora.

Este MCP NO duplica `mp_imss_patronal` — es la capa de **continuidad** que un
integrador necesita encima:
- Health-check programado de 8 sistemas sustantivos IMSS
- Detección temprana de degradación
- Plan de continuidad (DR/BCP) con criterios IMSS
- Reportes ejecutivos compatibles con formato licitación
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


NAMESPACE = "imss_continuidad"
URL_IMSS = "https://www.imss.gob.mx/"
URL_LICITACION = "https://comprasmx.buengobierno.gob.mx/"

# 8 sistemas sustantivos IMSS (extraído de bases de licitación 2026)
SISTEMAS_SUSTANTIVOS_IMSS: list[dict[str, Any]] = [
    {"clave": "idse", "nombre": "IMSS Desde Su Empresa (IDSE)",
     "url": "https://idse.imss.gob.mx/",
     "criticidad": "muy_alta", "rto_horas": 4, "rpo_horas": 1,
     "categoria": "patronal",
     "descripcion": "Sistema de movimientos afiliatorios patronal"},
    {"clave": "sua", "nombre": "Sistema Único de Autodeterminación (SUA)",
     "url": "https://www.imss.gob.mx/patrones/sua",
     "criticidad": "muy_alta", "rto_horas": 4, "rpo_horas": 1,
     "categoria": "patronal",
     "descripcion": "Cálculo automático de cuotas obrero-patronales"},
    {"clave": "semanas_cotizadas", "nombre": "Semanas Cotizadas (consulta ciudadana)",
     "url": "https://serviciosdigitales.imss.gob.mx/semanascotizadas/",
     "criticidad": "alta", "rto_horas": 8, "rpo_horas": 4,
     "categoria": "ciudadano",
     "descripcion": "Consulta semanas IMSS Régimen 73/97"},
    {"clave": "asignacion_nss", "nombre": "Asignación NSS",
     "url": "https://serviciosdigitales.imss.gob.mx/gestionAsegurados/asignacion-nss",
     "criticidad": "alta", "rto_horas": 8, "rpo_horas": 4,
     "categoria": "ciudadano",
     "descripcion": "Asignación Número de Seguridad Social"},
    {"clave": "cita_pension", "nombre": "Cita para Pensión",
     "url": "https://citasimss.com.mx/",
     "criticidad": "alta", "rto_horas": 12, "rpo_horas": 8,
     "categoria": "ciudadano",
     "descripcion": "Agenda citas pensión cesantía/vejez"},
    {"clave": "incapacidades_digitales", "nombre": "Incapacidades Digitales",
     "url": "https://www.imss.gob.mx/incapacidades-digitales",
     "criticidad": "muy_alta", "rto_horas": 4, "rpo_horas": 1,
     "categoria": "medico",
     "descripcion": "Sistema emisión incapacidades médicas"},
    {"clave": "cedula_emcr", "nombre": "Emisión Mensual Cédula Reposicionada (EMCR)",
     "url": "https://www.imss.gob.mx/",
     "criticidad": "muy_alta", "rto_horas": 6, "rpo_horas": 2,
     "categoria": "patronal",
     "descripcion": "Cédula mensual con reposición de cuotas"},
    {"clave": "alfresco_documental", "nombre": "Alfresco Content Services",
     "url": "https://www.imss.gob.mx/",
     "criticidad": "alta", "rto_horas": 12, "rpo_horas": 4,
     "categoria": "interno",
     "descripcion": "Gestión documental institucional (licitación renovación 2026)"},
]


class ImssContinuidadClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    def listar_sistemas_sustantivos(self) -> dict[str, Any]:
        """Los 8 sistemas sustantivos IMSS con RTO/RPO."""
        self._log("listar_sistemas_sustantivos", {})
        return {
            "total": len(SISTEMAS_SUSTANTIVOS_IMSS),
            "sistemas": SISTEMAS_SUSTANTIVOS_IMSS,
            "fuente_licitacion": URL_LICITACION,
        }

    def health_check_sistema(self, clave: str) -> dict[str, Any]:
        """Health-check de un sistema sustantivo (delega a mp_portales_monitor en producción)."""
        self._log("health_check_sistema", {"clave": clave})
        s = next((x for x in SISTEMAS_SUSTANTIVOS_IMSS if x["clave"] == clave), None)
        if not s:
            raise ValidationError(f"clave no reconocida: {clave!r}")

        import hashlib
        h = int(hashlib.sha256(clave.encode()).hexdigest(), 16)
        status = "verde" if (h % 10) > 1 else ("amarillo" if (h % 10) == 1 else "rojo")
        latencia = (h % 5000) + 500
        return mark_simulated(
            {
                **s,
                "status_actual": status,
                "latencia_ms": latencia,
                "dentro_rto": True if status == "verde" else False,
                "ultima_caida_horas": (h % 168),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            note="Mock — en producción delega a mp_portales_monitor.check_http con MP_PLAYWRIGHT_PUBLIC=1",
        )

    def plan_continuidad(self, clave: str) -> dict[str, Any]:
        """Plan de continuidad (DR/BCP) para un sistema sustantivo."""
        self._log("plan_continuidad", {"clave": clave})
        s = next((x for x in SISTEMAS_SUSTANTIVOS_IMSS if x["clave"] == clave), None)
        if not s:
            raise ValidationError(f"clave no reconocida: {clave!r}")
        # Criterios IMSS estándar (basados en NMX-COPANT-ISO 22301)
        plan = {
            "sistema": s["nombre"],
            "criticidad": s["criticidad"],
            "rto_objetivo_horas": s["rto_horas"],
            "rpo_objetivo_horas": s["rpo_horas"],
            "estrategia_recuperacion": (
                "Failover activo-activo multi-AZ"
                if s["criticidad"] == "muy_alta"
                else "Failover activo-pasivo cross-region"
            ),
            "componentes_replica": [
                "Base de datos (PostgreSQL/Oracle Standby)",
                "Application servers (Kubernetes multi-cluster)",
                "Almacenamiento documental (Alfresco S3-compatible)",
                "Capa de cache (Redis Sentinel)",
            ],
            "procedimientos_failover": [
                "1. Detección automática vía health-check cada 60s",
                "2. Switch DNS automático a sitio DR (TTL 60s)",
                "3. Notificación WhatsApp/Email a equipo SRE IMSS",
                "4. Validación de datos en sitio DR (RPO max 1h)",
                "5. Reporte ejecutivo en T+15min",
            ],
            "pruebas_dr_frecuencia": (
                "Trimestral con simulacro de pérdida total"
                if s["criticidad"] == "muy_alta"
                else "Semestral con simulacro parcial"
            ),
            "metricas_sla_mensual": {
                "uptime_objetivo_pct": 99.95 if s["criticidad"] == "muy_alta" else 99.5,
                "downtime_permitido_minutos_mes": 22 if s["criticidad"] == "muy_alta" else 216,
            },
            "fundamento_normativo": [
                "NMX-COPANT-ISO 22301 (Continuidad de Negocio)",
                "Programa Anual de Auditorías 2026 ASF",
                "Lineamientos Generales ATDT 2026",
            ],
        }
        return plan

    def reporte_ejecutivo(self, periodo: str) -> dict[str, Any]:
        """Reporte ejecutivo mensual formato licitación."""
        self._log("reporte_ejecutivo", {"periodo": periodo})
        if not periodo or len(periodo) != 7 or periodo[4] != "-":
            raise ValidationError("periodo debe ser YYYY-MM")

        import hashlib
        h = int(hashlib.sha256(periodo.encode()).hexdigest(), 16)

        incidentes_por_sistema = {}
        total_incidentes = 0
        total_minutos_caida = 0
        for s in SISTEMAS_SUSTANTIVOS_IMSS:
            n_inc = (h >> hash(s["clave"]) % 5) & 0x07  # 0-7 incidentes
            minutos = n_inc * ((h % 30) + 5)
            incidentes_por_sistema[s["clave"]] = {
                "incidentes": n_inc,
                "minutos_caida": minutos,
                "uptime_pct_mes": round((43200 - minutos) / 43200 * 100, 3),
                "cumple_sla": minutos <= (22 if s["criticidad"] == "muy_alta" else 216),
            }
            total_incidentes += n_inc
            total_minutos_caida += minutos

        return mark_simulated(
            {
                "periodo": periodo,
                "total_sistemas_monitoreados": len(SISTEMAS_SUSTANTIVOS_IMSS),
                "total_incidentes_periodo": total_incidentes,
                "total_minutos_caida_acumulados": total_minutos_caida,
                "uptime_promedio_periodo_pct": round(
                    100 - (total_minutos_caida / (43200 * len(SISTEMAS_SUSTANTIVOS_IMSS)) * 100), 3
                ),
                "sistemas_que_cumplieron_sla": sum(
                    1 for v in incidentes_por_sistema.values() if v["cumple_sla"]
                ),
                "detalle_por_sistema": incidentes_por_sistema,
                "recomendaciones": [
                    "Reforzar monitoring en sistemas con incidentes > 3",
                    "Programar simulacro DR siguiente trimestre",
                    "Revisar capacidad en horarios pico (10-13h CDMX)",
                ],
                "formato_compatible_licitacion": True,
                "fuente_normativa": "Anexo Técnico Licitación Continuidad Operativa 2026",
            },
            note="Mock — datos simulados para demostración del formato del reporte.",
        )
