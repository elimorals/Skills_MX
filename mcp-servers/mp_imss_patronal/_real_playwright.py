"""Path Playwright real opt-in para mp_imss_patronal.

Este módulo expone un checklist de credenciales y delega a `shared.playwright_stub.respuesta_real_no_implementada`
cuando se invoca un tool sin implementación de browser automation aún.

Documentación: ver SETUP_PLAYWRIGHT_REAL.md
"""
from __future__ import annotations

import os
from typing import Any

from shared.errors import UpstreamError
from shared.playwright_stub import respuesta_real_no_implementada


PORTAL_BASE = "https://idse.imss.gob.mx"
PORTAL_ID = "imss_idse"


def checklist_credenciales() -> dict[str, bool]:
    """Verifica qué credenciales están listas en el entorno."""
    return {
        "rfc_patronal_set": bool(os.environ.get("IMSS_RFC_PATRONAL")),
        "tiene_npie": bool(
            os.environ.get("IMSS_NPIE_PATH") and os.environ.get("IMSS_NPIE_PIN")
        ),
        "tiene_efirma": bool(
            os.environ.get("IMSS_EFIRMA_CERT")
            and os.environ.get("IMSS_EFIRMA_KEY")
            and os.environ.get("IMSS_EFIRMA_PASS")
        ),
        "playwright_real_flag": os.environ.get("PLUGINS_MX_PLAYWRIGHT_REAL") == "1",
        "permitir_escritura": os.environ.get("PLUGINS_MX_IMSS_PERMITIR_ESCRITURA") == "1",
    }


def respuesta_no_implementada(tool: str) -> dict[str, Any]:
    """Wrapper local que añade el checklist específico de IMSS."""
    base = respuesta_real_no_implementada(PORTAL_ID, tool)
    base["portal_url"] = PORTAL_BASE
    base["checklist"] = checklist_credenciales()
    return base


# ---------- stubs por tool ----------

def real_consultar_avisos_pendientes(registro_patronal: str) -> dict[str, Any]:
    return respuesta_no_implementada("imss_consultar_avisos_pendientes")


def real_enviar_movimiento_afiliatorio(
    registro_patronal: str, nss: str, tipo_movimiento: str, **kwargs
) -> dict[str, Any]:
    if os.environ.get("PLUGINS_MX_IMSS_PERMITIR_ESCRITURA") != "1":
        raise UpstreamError(
            "Operación de escritura bloqueada. Setear "
            "PLUGINS_MX_IMSS_PERMITIR_ESCRITURA=1 (NO RECOMENDADO sin sandbox).",
            {"portal": PORTAL_ID, "tipo_movimiento": tipo_movimiento},
        )
    return respuesta_no_implementada("imss_enviar_movimiento_afiliatorio")


def real_descargar_cedula_autodeterminacion(
    registro_patronal: str, bimestre: int, ejercicio: int
) -> dict[str, Any]:
    return respuesta_no_implementada("imss_descargar_cedula_autodeterminacion")


def real_consultar_emcr(
    registro_patronal: str, mes: int, ejercicio: int
) -> dict[str, Any]:
    return respuesta_no_implementada("imss_consultar_emcr")


def real_consultar_sbc(registro_patronal: str, nss: str) -> dict[str, Any]:
    return respuesta_no_implementada("imss_consultar_sbc")


def real_consultar_padron_trabajadores(registro_patronal: str) -> dict[str, Any]:
    return respuesta_no_implementada("imss_consultar_padron_trabajadores")
