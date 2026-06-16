"""Path Playwright real opt-in para mp_infonavit_patronal.

Mismo patrón que mp_imss_patronal._real_playwright. Delega a
`shared.playwright_stub.respuesta_real_no_implementada` cuando aún no hay
implementación de browser automation.

Documentación: ver SETUP_PLAYWRIGHT_REAL.md
"""
from __future__ import annotations

import os
from typing import Any

from shared.playwright_stub import respuesta_real_no_implementada


PORTAL_BASE = "https://empresarios.infonavit.org.mx"
PORTAL_ID = "infonavit_empresarial"


def checklist_credenciales() -> dict[str, bool]:
    return {
        "rfc_patronal_set": bool(os.environ.get("INFONAVIT_RFC_PATRONAL")),
        "tiene_usuario_password": bool(
            os.environ.get("INFONAVIT_USUARIO")
            and os.environ.get("INFONAVIT_PASSWORD")
        ),
        "tiene_efirma_opcional": bool(os.environ.get("INFONAVIT_EFIRMA_CERT")),
        "playwright_real_flag": os.environ.get("PLUGINS_MX_PLAYWRIGHT_REAL") == "1",
    }


def respuesta_no_implementada(tool: str) -> dict[str, Any]:
    base = respuesta_real_no_implementada(PORTAL_ID, tool)
    base["portal_url"] = PORTAL_BASE
    base["checklist"] = checklist_credenciales()
    return base


# ---------- stubs por tool ----------

def real_consultar_creditos_trabajadores(registro_patronal: str) -> dict[str, Any]:
    return respuesta_no_implementada("infonavit_consultar_creditos_trabajadores")


def real_descargar_emis(
    registro_patronal: str, mes: int, ejercicio: int
) -> dict[str, Any]:
    return respuesta_no_implementada("infonavit_descargar_emis")


def real_consultar_descuentos_mensuales(
    registro_patronal: str, nss: str, mes: int, ejercicio: int
) -> dict[str, Any]:
    return respuesta_no_implementada("infonavit_consultar_descuentos_mensuales")


def real_consultar_avisos_pendientes(registro_patronal: str) -> dict[str, Any]:
    return respuesta_no_implementada("infonavit_consultar_avisos_pendientes")
