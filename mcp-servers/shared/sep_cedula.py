"""Validación de cédula profesional vía SEP (Registro Nacional de Profesionistas).

⚠ Validado Playwright MCP 2026-06-13: portal público cedulaprofesional.sep.gob.mx.
SIN CAPTCHA — automatizable con Playwright.

USO desde telemedicina-mx (verificar médico antes de consulta):
    from shared.sep_cedula import consultar_cedula_sep
    info = consultar_cedula_sep(cedula="12345678")
    if not info["vigente"]:
        raise ConsultaIlegal("Cédula no válida")

URL: https://cedulaprofesional.sep.gob.mx/
Selectores:
- input#cedula (8 chars) — modo búsqueda por cédula
- input#nombre, input#primerApellido, input#segundoApellido (50 c/u) — modo por datos
- input#curp (18 chars)
- button:has-text("Buscar")
- button:has-text("Descargar CSV") — permite extracción masiva

Schema respuesta esperada (tabla resultados):
- nombre completo
- número de cédula
- profesión
- institución de origen
- fecha de expedición
- estado vigencia
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.errors import UpstreamError, ValidationError


URL_SEP_CEDULA = "https://cedulaprofesional.sep.gob.mx/"

SELECTORES = {
    "cedula": "input#cedula",
    "nombre": "input#nombre",
    "primer_apellido": "input#primerApellido",
    "segundo_apellido": "input#segundoApellido",
    "curp": "input#curp",
    "submit": "button:has-text('Buscar')",
    "descargar_csv": "button:has-text('Descargar CSV')",
    "result_table": "table, .resultado, .tabla-resultados",
}


def validar_formato_cedula(cedula: str) -> bool:
    """Cédula SEP es 7-8 dígitos numéricos."""
    if not cedula or not isinstance(cedula, str):
        return False
    return bool(re.match(r"^\d{7,8}$", cedula.strip()))


def consultar_cedula_sep(
    cedula: Optional[str] = None,
    nombre: Optional[str] = None,
    primer_apellido: Optional[str] = None,
    segundo_apellido: Optional[str] = None,
    curp: Optional[str] = None,
) -> dict[str, Any]:
    """Consulta cédula profesional SEP via Playwright.

    Args:
        cedula: 7-8 dígitos. Si se provee, ignora el resto.
        nombre/primer_apellido/segundo_apellido: búsqueda por datos.
        curp: alternativa de búsqueda.

    Requiere MP_PLAYWRIGHT_PUBLIC=1. Sin esa env var → modo mock.

    Returns:
        Dict con: cedula, nombre_completo, profesion, institucion,
                  fecha_expedicion, vigente, fuente, simulated
    """
    from shared.playwright_real import (
        playwright_session, is_public_real_enabled, safe_text,
    )

    if cedula and not validar_formato_cedula(cedula):
        raise ValidationError(f"Cédula '{cedula}' no tiene formato válido (7-8 dígitos).")

    if not any([cedula, nombre, curp]):
        raise ValidationError(
            "Debe proveer al menos uno: cedula, nombre+apellido, o curp."
        )

    if not is_public_real_enabled():
        return _mock_response(cedula, nombre, primer_apellido)

    with playwright_session() as page:
        try:
            page.goto(URL_SEP_CEDULA, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
        except Exception as e:
            raise UpstreamError(f"No se pudo cargar SEP cédula: {e}", {})

        # Llenar campos
        if cedula:
            page.locator(SELECTORES["cedula"]).fill(cedula)
        else:
            if nombre:
                page.locator(SELECTORES["nombre"]).fill(nombre)
            if primer_apellido:
                page.locator(SELECTORES["primer_apellido"]).fill(primer_apellido)
            if segundo_apellido:
                page.locator(SELECTORES["segundo_apellido"]).fill(segundo_apellido)
            if curp:
                page.locator(SELECTORES["curp"]).fill(curp)

        # Click buscar
        page.locator(SELECTORES["submit"]).first.click()

        try:
            page.wait_for_selector(SELECTORES["result_table"], timeout=15000)
        except Exception:
            raise UpstreamError("Timeout esperando resultados SEP.", {})

        # Parsear primera fila de resultados
        rows = page.locator(SELECTORES["result_table"] + " tr").all()
        for row in rows:
            celdas = row.locator("td").all()
            if len(celdas) >= 4:
                return {
                    "cedula": safe_text(celdas[0]),
                    "nombre_completo": safe_text(celdas[1]),
                    "profesion": safe_text(celdas[2]) if len(celdas) > 2 else None,
                    "institucion": safe_text(celdas[3]) if len(celdas) > 3 else None,
                    "fecha_expedicion": safe_text(celdas[4]) if len(celdas) > 4 else None,
                    "vigente": True,
                    "fuente": "SEP-RNP",
                    "url_consultada": URL_SEP_CEDULA,
                    "simulated": False,
                }

        return {
            "vigente": False,
            "razon": "No se encontraron resultados",
            "fuente": "SEP-RNP",
            "simulated": False,
        }


def _mock_response(
    cedula: Optional[str], nombre: Optional[str], primer_apellido: Optional[str]
) -> dict[str, Any]:
    """Respuesta mock realista para desarrollo."""
    return {
        "cedula": cedula or "1234567",
        "nombre_completo": f"{nombre or 'JUAN'} {primer_apellido or 'PEREZ'} GARCIA",
        "profesion": "Médico Cirujano",
        "institucion": "Universidad Nacional Autónoma de México",
        "fecha_expedicion": "2015-06-15",
        "vigente": True,
        "fuente": "SEP-RNP",
        "url_consultada": URL_SEP_CEDULA,
        "simulated": True,
    }
