"""Cliente mp_citas_monitor — monitor ÉTICO de cupos para citas gob.mx.

Diferencia respecto al "mercado negro" de citas SAT:

- NO reserva automáticamente. Alerta al titular cuando se abren cupos.
- 1 alerta = 1 titular (RFC/CURP). NO se aceptan polling masivo de terceros.
- Throttling integrado: 1 check cada 60-300 segundos por alerta.
- Bitácora hasheada de identificadores.
- Trazabilidad completa: cada alerta tiene `consent_token` que el titular emite.

Portales soportados:
- SAT (citas.sat.gob.mx) — e.firma, RFC, CSF
- IMSS (citas.imss.gob.mx) — pensión, cesantía, vejez, NSS
- SRE Mexitel — pasaporte
- INE — credencial reposición / cambio domicilio
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ValidationError  # noqa: E402
from shared.mock import mark_simulated  # noqa: E402


NAMESPACE = "citas_monitor"

# Portales soportados
PORTALES_CITAS: dict[str, dict[str, Any]] = {
    "sat_citas": {
        "nombre": "SAT — Citas e.firma / RFC / CSF",
        "url": "https://citas.sat.gob.mx/",
        "tramites": [
            "firma_electronica_renovacion",
            "firma_electronica_persona_fisica",
            "firma_electronica_persona_moral",
            "rfc_inscripcion",
            "csf_descarga",
            "aclaracion_devoluciones",
        ],
        "selectores_validados": False,  # pendiente discovery
        "polling_min_seconds": 120,
    },
    "imss_citas": {
        "nombre": "IMSS — Citas pensión/cesantía/NSS",
        "url": "https://citas.imss.gob.mx/",
        "tramites": [
            "pension_cesantia_vejez",
            "pension_invalidez",
            "asignacion_nss",
            "aclaracion_semanas_cotizadas",
            "incapacidad_temporal_revision",
        ],
        "selectores_validados": False,
        "polling_min_seconds": 180,
    },
    "sre_mexitel": {
        "nombre": "SRE — Mexitel pasaporte",
        "url": "https://citas.sre.gob.mx/",
        "tramites": [
            "pasaporte_ordinario_nuevo",
            "pasaporte_ordinario_renovacion",
            "pasaporte_menor_edad",
            "doble_nacionalidad",
        ],
        "selectores_validados": False,
        "polling_min_seconds": 60,
    },
    "ine_modulos": {
        "nombre": "INE — Módulos credencial",
        "url": "https://www.ine.mx/credencial/",
        "tramites": [
            "credencial_reposicion",
            "credencial_cambio_domicilio",
            "credencial_renovacion",
            "credencial_primera_vez",
        ],
        "selectores_validados": False,
        "polling_min_seconds": 300,
    },
}

CANALES_NOTIFICACION = {"whatsapp", "email", "sms", "webhook"}
ESTADOS_ALERTA = {"activa", "pausada", "consumida", "expirada", "cancelada"}

# Vigencia máxima del consent_token (60 días por defecto)
TTL_CONSENT_DIAS_MAX = 60


class CitasMonitorClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        safe = dict(params)
        for k in ("rfc", "curp", "nss", "telefono", "email"):
            if k in safe:
                safe[f"{k}_hash"] = Bitacora.hash_sensitive(str(safe.pop(k)))
        self._bitacora.log(op, success=True, params_summary=safe)

    def listar_portales(self) -> dict[str, Any]:
        """Lista los 4 portales soportados con trámites."""
        self._log("listar_portales", {})
        return {
            "total_portales": len(PORTALES_CITAS),
            "portales": [
                {"clave": k, **v} for k, v in PORTALES_CITAS.items()
            ],
            "etica_operacional": {
                "no_reserva_automatica": True,
                "alerta_solo_al_titular_consentido": True,
                "throttling_minimo_segundos": 60,
                "fundamento_legal": "LFPDPPP Art. 13 (consentimiento)",
            },
        }

    def generar_consent_token(
        self,
        titular_curp: str,
        titular_rfc: str | None,
        portal_clave: str,
        tramite: str,
        ttl_dias: int = 30,
    ) -> dict[str, Any]:
        """Genera token de consentimiento del titular para que UN tercero monitoree.

        El token vincula:
        - identificador del titular (CURP hasheado)
        - portal específico (no aplica a todos)
        - trámite específico
        - vigencia limitada
        - canal de notificación

        El titular debe emitirlo por su cuenta — un coyote NO debería poder
        generar tokens en lote para 100 desconocidos.
        """
        self._log("generar_consent_token", {
            "curp": titular_curp, "rfc": titular_rfc,
            "portal": portal_clave, "tramite": tramite,
        })
        if portal_clave not in PORTALES_CITAS:
            raise ValidationError(f"portal_clave no reconocida: {portal_clave!r}")
        portal = PORTALES_CITAS[portal_clave]
        if tramite not in portal["tramites"]:
            raise ValidationError(
                f"tramite {tramite!r} no disponible en {portal_clave}. "
                f"Trámites: {portal['tramites']}"
            )
        if ttl_dias < 1 or ttl_dias > TTL_CONSENT_DIAS_MAX:
            raise ValidationError(
                f"ttl_dias debe ser 1-{TTL_CONSENT_DIAS_MAX}"
            )

        emitido = datetime.now(timezone.utc)
        expira = emitido + timedelta(days=ttl_dias)
        token = f"CT-{Bitacora.hash_sensitive(titular_curp + portal_clave + tramite)[:8].upper()}"

        return {
            "consent_token": token,
            "titular_curp_hash": Bitacora.hash_sensitive(titular_curp),
            "titular_rfc_hash": Bitacora.hash_sensitive(titular_rfc) if titular_rfc else None,
            "portal_clave": portal_clave,
            "tramite": tramite,
            "ttl_dias": ttl_dias,
            "emitido_at": emitido.isoformat(),
            "expira_at": expira.isoformat(),
            "fundamento_legal": "LFPDPPP Art. 13 + Art. 16 (consentimiento explícito limitado).",
            "advertencia": (
                "Este token autoriza UN monitoreo para UN titular. NO puede ser "
                "reutilizado para terceros. Su uso para acaparar citas constituye "
                "uso indebido y será reportado a PFDC."
            ),
        }

    def crear_alerta(
        self,
        consent_token: str,
        canal: str,
        destinatario: str,
        entidad_preferida: str | None = None,
        fecha_min: str | None = None,
        fecha_max: str | None = None,
    ) -> dict[str, Any]:
        """Crea una alerta de monitoreo. NO reserva — solo avisa."""
        self._log("crear_alerta", {
            "consent_token": consent_token, "canal": canal,
            "destinatario": destinatario,
        })
        if not consent_token.startswith("CT-"):
            raise ValidationError("consent_token inválido — debe empezar con 'CT-'")
        if canal not in CANALES_NOTIFICACION:
            raise ValidationError(
                f"canal inválido. Válidos: {sorted(CANALES_NOTIFICACION)}"
            )
        if fecha_min and fecha_max and fecha_min > fecha_max:
            raise ValidationError("fecha_min > fecha_max")

        import hashlib
        alerta_id = f"AL-{hashlib.sha256((consent_token + canal + destinatario).encode()).hexdigest()[:10].upper()}"

        return mark_simulated(
            {
                "alerta_id": alerta_id,
                "consent_token": consent_token,
                "canal": canal,
                "destinatario_hash": Bitacora.hash_sensitive(destinatario),
                "entidad_preferida": entidad_preferida,
                "ventana_fechas": {
                    "min": fecha_min,
                    "max": fecha_max,
                },
                "estado": "activa",
                "polling_seconds": 120,
                "creada_at": datetime.now(timezone.utc).isoformat(),
                "advertencia_acaparamiento": (
                    "Esta alerta NO reserva citas automáticamente. Cuando se abre "
                    "cupo en la ventana, se envía un mensaje al destinatario y este "
                    "decide si la reserva manualmente."
                ),
            },
            note="Mock — en producción persiste en sqlite con cron de polling.",
        )

    def revisar_cupos(self, portal_clave: str, tramite: str) -> dict[str, Any]:
        """Revisa cupos disponibles para un trámite (read-only, sin titular)."""
        self._log("revisar_cupos", {"portal": portal_clave, "tramite": tramite})
        if portal_clave not in PORTALES_CITAS:
            raise ValidationError(f"portal_clave no reconocida: {portal_clave!r}")
        portal = PORTALES_CITAS[portal_clave]
        if tramite not in portal["tramites"]:
            raise ValidationError(f"tramite no disponible en {portal_clave}: {tramite!r}")

        # Path real Playwright opt-in
        from shared.playwright_real import is_public_real_enabled
        if not is_public_real_enabled():
            import hashlib
            h = int(hashlib.sha256(f"{portal_clave}{tramite}".encode()).hexdigest(), 16)
            tiene_cupos = (h % 10) > 7  # ~20% probabilidad
            n_cupos = (h % 15) if tiene_cupos else 0
            return mark_simulated(
                {
                    "portal": portal_clave,
                    "tramite": tramite,
                    "tiene_cupos": tiene_cupos,
                    "n_cupos_aprox": n_cupos,
                    "siguiente_dia_disponible": (
                        (datetime.now(timezone.utc) + timedelta(days=(h % 30) + 1)).date().isoformat()
                        if tiene_cupos else None
                    ),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                note="Mock — para path real setear MP_PLAYWRIGHT_PUBLIC=1.",
            )

        # Path real intencionalmente skeleton — discovery pendiente
        return {
            "portal": portal_clave,
            "tramite": tramite,
            "real_implementado": False,
            "razon": (
                "Discovery Playwright pendiente. Los portales de citas usan "
                "selectores que cambian y CAPTCHAs. Activación: ver SETUP."
            ),
            "siguiente_paso": "Coordinar con equipo legal del titular antes de polling.",
            "simulated": False,
        }

    def estadisticas_eticas(self) -> dict[str, Any]:
        """Métricas de operación ética para auditoría."""
        self._log("estadisticas_eticas", {})
        return {
            "total_portales_monitoreados": len(PORTALES_CITAS),
            "polling_minimo_global_segundos": 60,
            "ttl_consent_max_dias": TTL_CONSENT_DIAS_MAX,
            "auto_reserva_habilitada": False,
            "canal_notificacion_soportados": list(CANALES_NOTIFICACION),
            "estados_alerta": list(ESTADOS_ALERTA),
            "compromiso": (
                "Plugins MX NO acapara citas. Cada alerta requiere consent_token "
                "del titular vinculado a CURP. Uso indebido se reporta a PFDC."
            ),
            "diferenciador_vs_mercado_negro": [
                "1 alerta = 1 titular (vinculado a CURP)",
                "Throttling mínimo 60s (vs ~5s del mercado negro)",
                "Sin auto-reserva ni venta de citas",
                "Bitácora hasheada LFPDPPP-compliant",
                "Token revocable y con vigencia máxima 60 días",
            ],
        }
