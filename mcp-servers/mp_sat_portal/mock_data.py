"""Respuestas mock plausibles para mp_sat_portal.

Cada tool del MCP que requiere auth retorna estos shapes cuando corre sin
credenciales o con PLUGINS_MX_MOCK=1. Las respuestas llevan `simulated: true`
para que skills downstream no las confundan con datos reales.

⚠ Los nombres y RFCs aquí son ficticios pero respetan estructura SAT válida.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any


def mock_csf(rfc: str) -> dict[str, Any]:
    """Mock de Constancia de Situación Fiscal."""
    rfc_norm = rfc.strip().upper()
    es_persona_fisica = len(rfc_norm) == 13
    return {
        "rfc": rfc_norm,
        "nombre": "ELIAS USUARIO DEMO" if es_persona_fisica else "EMPRESA DEMO SA DE CV",
        "fecha_emision_csf": date.today().isoformat(),
        "fecha_inicio_operaciones": "2018-01-01",
        "status_padron": "ACTIVO",
        "regimen_actual": "626 — Régimen Simplificado de Confianza" if es_persona_fisica else "601 — General de Ley Personas Morales",
        "obligaciones_vigentes": [
            "ISR_PROVISIONAL",
            "IVA_MENSUAL",
            "DECLARACION_INFORMATIVA",
        ],
        "domicilio_fiscal": {
            "calle": "AV. INSURGENTES SUR",
            "numero_exterior": "1234",
            "numero_interior": "PISO 5",
            "colonia": "DEL VALLE",
            "municipio": "BENITO JUAREZ",
            "estado": "CIUDAD DE MEXICO",
            "codigo_postal": "03100",
        },
        "actividades_economicas": [
            {
                "orden": 1,
                "porcentaje": 70,
                "descripcion": "Desarrollo de software y servicios de consultoría",
            },
            {
                "orden": 2,
                "porcentaje": 30,
                "descripcion": "Capacitación profesional",
            },
        ],
        "url_pdf_csf": None,
    }


def mock_padron(rfc: str) -> dict[str, Any]:
    """Mock de consulta al padrón de contribuyentes (público)."""
    rfc_norm = rfc.strip().upper()
    return {
        "rfc": rfc_norm,
        "encontrado": True,
        "status": "ACTIVO",
        "nombre": "EMPRESA DEMO SA DE CV" if len(rfc_norm) == 12 else "ELIAS USUARIO DEMO",
        "regimen_capital": "S.A. DE C.V." if len(rfc_norm) == 12 else None,
        "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
    }


def mock_69b(rfc: str | None = None) -> dict[str, Any]:
    """Mock de lista 69-B EFOS.

    Si pasa un RFC y coincide con un demo, lo retorna como presunto.
    """
    rfc_norm = (rfc or "").strip().upper()
    presuntos_demo = [
        {
            "rfc": "EFD850101001",
            "nombre": "FACTURADORA DEMO PRESUNTA SA DE CV",
            "estado_69b": "PRESUNTO",
            "oficio_presuncion": "500-05-2025-12345 del 15-Feb-2025",
            "fecha_publicacion_presuncion": "2025-02-20",
            "oficio_definitivo": None,
            "fecha_publicacion_definitivo": None,
        },
        {
            "rfc": "EFD850202002",
            "nombre": "FACTURADORA DEMO DEFINITIVA SA",
            "estado_69b": "DEFINITIVO",
            "oficio_presuncion": "500-05-2024-98765 del 10-Oct-2024",
            "fecha_publicacion_presuncion": "2024-10-15",
            "oficio_definitivo": "500-05-2025-54321 del 03-Mar-2025",
            "fecha_publicacion_definitivo": "2025-03-08",
        },
    ]

    if rfc_norm:
        for r in presuntos_demo:
            if r["rfc"] == rfc_norm:
                return {
                    "rfc_consultado": rfc_norm,
                    "encontrado": True,
                    "registro": r,
                    "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
                }
        return {
            "rfc_consultado": rfc_norm,
            "encontrado": False,
            "registro": None,
            "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
        }

    return {
        "rfc_consultado": None,
        "total_registros": len(presuntos_demo),
        "registros": presuntos_demo,
        "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
    }


def mock_69_incumplidos(rfc: str | None = None) -> dict[str, Any]:
    """Mock de lista 69 incumplidos."""
    rfc_norm = (rfc or "").strip().upper()
    incumplidos_demo = [
        {
            "rfc": "INC900101001",
            "nombre": "INCUMPLIDO DEMO SA DE CV",
            "supuesto": "NO_LOCALIZADO",
            "entidad": "CIUDAD DE MEXICO",
        },
        {
            "rfc": "INC910202002",
            "nombre": "INCUMPLIDO DOMICILIO FALSO SA",
            "supuesto": "DOMICILIO_FALSO",
            "entidad": "JALISCO",
        },
    ]

    if rfc_norm:
        for r in incumplidos_demo:
            if r["rfc"] == rfc_norm:
                return {
                    "rfc_consultado": rfc_norm,
                    "encontrado": True,
                    "registro": r,
                    "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
                }
        return {
            "rfc_consultado": rfc_norm,
            "encontrado": False,
            "registro": None,
            "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
        }

    return {
        "total_registros": len(incumplidos_demo),
        "registros": incumplidos_demo,
        "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
    }


def mock_buzon_tributario(rfc: str) -> dict[str, Any]:
    """Mock de notificaciones del Buzón Tributario."""
    rfc_norm = rfc.strip().upper()
    return {
        "rfc": rfc_norm,
        "total_pendientes": 2,
        "notificaciones": [
            {
                "folio": "BZ-2026-001234",
                "tipo": "REQUERIMIENTO",
                "fecha_notificacion": (date.today() - timedelta(days=3)).isoformat(),
                "fecha_limite_respuesta": (date.today() + timedelta(days=12)).isoformat(),
                "asunto": "Requerimiento de información — Devolución IVA solicitada en abril",
                "urgencia": "MEDIA",
                "no_leida": True,
            },
            {
                "folio": "BZ-2026-001120",
                "tipo": "INVITACION",
                "fecha_notificacion": (date.today() - timedelta(days=10)).isoformat(),
                "fecha_limite_respuesta": None,
                "asunto": "Invitación a regularizar — Declaración informativa pendiente",
                "urgencia": "BAJA",
                "no_leida": True,
            },
        ],
        "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
    }


def mock_cfdi_masivo(
    rfc: str, ejercicio: int, mes: int, tipo: str
) -> dict[str, Any]:
    """Mock de descarga masiva de CFDIs."""
    rfc_norm = rfc.strip().upper()
    return {
        "rfc": rfc_norm,
        "ejercicio": ejercicio,
        "mes": mes,
        "tipo": tipo.lower(),
        "solicitud_id": f"SOL-MOCK-{ejercicio}{mes:02d}-{tipo[:3].upper()}",
        "estado_solicitud": "ACEPTADA",
        "fecha_solicitud": datetime.now().isoformat(timespec="seconds"),
        "fecha_estimada_disponibilidad": (datetime.now() + timedelta(hours=2)).isoformat(timespec="seconds"),
        "total_estimado_cfdis": 47 if tipo.lower() == "emitidos" else 153,
        "url_descarga_zip": None,
        "instrucciones": "En modo real, el SAT entrega un .zip con metadata + XMLs en 1-4 horas tras solicitud.",
    }


def mock_cita_sat(rfc: str, tipo_tramite: str, entidad: str | None = None) -> dict[str, Any]:
    """Mock de búsqueda de cita SAT."""
    return {
        "rfc": rfc.strip().upper(),
        "tipo_tramite": tipo_tramite,
        "entidad": entidad or "CIUDAD DE MEXICO",
        "citas_disponibles": [
            {
                "fecha": (date.today() + timedelta(days=4)).isoformat(),
                "hora": "10:30",
                "oficina": "ADSC CDMX 1 — INSURGENTES SUR",
                "direccion": "Av. Insurgentes Sur 2000, Col. Del Valle, CDMX",
                "agendable": True,
            },
            {
                "fecha": (date.today() + timedelta(days=7)).isoformat(),
                "hora": "13:00",
                "oficina": "ADSC CDMX 2 — POLANCO",
                "direccion": "Av. Ejército Nacional 800, Col. Polanco, CDMX",
                "agendable": True,
            },
        ],
        "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
    }


def mock_verificacion_uuid(
    uuid: str, rfc_emisor: str, rfc_receptor: str, total: str
) -> dict[str, Any]:
    """Mock de verificación de UUID contra el portal SAT."""
    return {
        "uuid": uuid.strip().upper(),
        "rfc_emisor": rfc_emisor.strip().upper(),
        "rfc_receptor": rfc_receptor.strip().upper(),
        "total_consultado": str(total),
        "estado_cfdi": "Vigente",
        "estado_cancelacion": None,
        "fecha_consulta": datetime.now().isoformat(timespec="seconds"),
        "fuente": "verificacfdi.facturaelectronica.sat.gob.mx (mock)",
    }


def mock_efirma_status(rfc: str) -> dict[str, Any]:
    """Mock de status de e.firma."""
    vencimiento = date.today() + timedelta(days=720)
    return {
        "rfc": rfc.strip().upper(),
        "status_efirma": "VIGENTE",
        "fecha_emision": (date.today() - timedelta(days=300)).isoformat(),
        "fecha_vencimiento": vencimiento.isoformat(),
        "dias_para_vencer": 720,
        "numero_serie": "00001000000412345678",
        "alerta_renovacion": False,
    }


def mock_acuse(folio: str) -> dict[str, Any]:
    """Mock de descarga de acuse de declaración/trámite."""
    return {
        "folio": folio.strip(),
        "tipo_acuse": "DECLARACION_PROVISIONAL",
        "fecha_presentacion": date.today().isoformat(),
        "estado": "ACEPTADO",
        "linea_captura": "0123 4567 8901 2345 6789",
        "fecha_pago_limite": (date.today() + timedelta(days=17)).isoformat(),
        "url_pdf_acuse": None,
    }


def mock_actualizar_obligaciones(rfc: str, accion: str) -> dict[str, Any]:
    """Mock de aviso de cambio de obligaciones (acción peligrosa: solo simulación)."""
    return {
        "rfc": rfc.strip().upper(),
        "accion_solicitada": accion,
        "estado": "SIMULADA_NO_ENVIADA",
        "advertencia_critica": (
            "Esta operación modifica el padrón de contribuyentes en SAT. "
            "En modo real requiere e.firma activa y triggers cambio de régimen, "
            "alta/baja de obligaciones o cierre de operaciones. Verificar 2 veces "
            "antes de ejecutar contra portal real."
        ),
        "fecha_simulacion": datetime.now().isoformat(timespec="seconds"),
    }
