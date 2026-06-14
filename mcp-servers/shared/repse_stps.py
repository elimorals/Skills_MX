"""Consulta REPSE (Registro Público de empresas de Subcontratación STPS).

Validado Playwright MCP 2026-06-14: portal https://repse.stps.gob.mx/app/
- reCAPTCHA v1beta1 marcado deprecated por Google → NO valida nada actualmente
- Consulta totalmente automatizable sin humano-en-loop
- Universo: TODA empresa MX que provee servicios especializados (Art. 15 LFT)

Selectores DOM reales validados:
- input búsqueda: textbox[name="Razón social"]
- botón Buscar: button:has-text("Buscar")
- tabla resultados: table > tbody > tr con celdas (razon_social, num_registro, [Seleccionar])
- detalle: heading "REGISTRO LOCALIZADO FOLIO: {n}", paragraphs con etiquetas:
  - "Nombre o Razón Social"
  - "Entidad / Municipio"
  - "Aviso de registro N. / Fecha de aviso de registro"  → "AR{nnnn} / YYYY-MM-DD"
  - "Vigencia del Registro" → YYYY-MM-DD
  - "Ofreciendo los siguientes servicios" → list items

Sin auth. Sin pago. Gratis. Endpoint AJAX no documentado pero ruta /app/ y SPA.
"""

from __future__ import annotations

import re
from typing import Any, Optional


URL_REPSE_PORTAL = "https://repse.stps.gob.mx/Publico"
URL_REPSE_APP = "https://repse.stps.gob.mx/app/"

SELECTORES_REPSE = {
    "input_razon_social": "input[placeholder*='Razón social'], textbox[name='Razón social']",
    "boton_buscar": "button:has-text('Buscar')",
    "tabla_resultados": "table tbody tr",
    "boton_seleccionar": "button:has-text('Seleccionar')",
    "detalle_folio_heading": "h3:has-text('REGISTRO LOCALIZADO FOLIO')",
    "detalle_razon_label": "p:has-text('Nombre o Razón Social')",
    "detalle_entidad_label": "p:has-text('Entidad / Municipio')",
    "detalle_aviso_label": "p:has-text('Aviso de registro N.')",
    "detalle_vigencia_label": "p:has-text('Vigencia del Registro')",
    "detalle_servicios_label": "p:has-text('Ofreciendo los siguientes servicios')",
    "boton_regresar": "button:has-text('Regresar')",
}


def normalizar_razon_social(razon: str) -> str:
    """Normaliza razón social: uppercase, sin sufijos legales redundantes para búsqueda fuzzy."""
    if not razon:
        return ""
    norm = razon.strip().upper()
    # Quitar puntuación común
    norm = re.sub(r"[\.,;]", " ", norm)
    norm = re.sub(r"\s+", " ", norm)
    return norm.strip()


def parsear_aviso_registro(texto: str) -> tuple[Optional[str], Optional[str]]:
    """Parsea "AR6169 / 2024-06-12" → ("AR6169", "2024-06-12")."""
    if not texto:
        return None, None
    m = re.match(r"\s*(AR\d+)\s*/\s*(\d{4}-\d{2}-\d{2})\s*", texto)
    if m:
        return m.group(1), m.group(2)
    return None, None


def parsear_entidad_municipio(texto: str) -> tuple[Optional[str], Optional[str]]:
    """Parsea "Ciudad de México / Benito Juárez" → ("Ciudad de México", "Benito Juárez")."""
    if not texto or "/" not in texto:
        return texto.strip() if texto else None, None
    partes = [p.strip() for p in texto.split("/", 1)]
    return partes[0], partes[1] if len(partes) > 1 else None


def consultar_repse(razon_social: str) -> dict[str, Any]:
    """Consulta REPSE por razón social.

    En este módulo shared SIN Playwright runtime: devuelve estructura mock para tests.
    El path real está en mp_repse_stps/client.py con Playwright wrapper.

    Returns:
        {
            "razon_social_buscada": str,
            "encontrados": [
                {
                    "razon_social": str,
                    "numero_registro": str,
                    "folio": Optional[str],
                    "aviso_registro": Optional[str],
                    "fecha_aviso": Optional[str],
                    "vigencia": Optional[str],
                    "entidad": Optional[str],
                    "municipio": Optional[str],
                    "servicios": List[str],
                    "vigente": bool,  # True si vigencia >= hoy
                }
            ],
            "url_consultado": URL_REPSE_APP,
            "simulated": bool,
        }
    """
    return {
        "razon_social_buscada": normalizar_razon_social(razon_social),
        "encontrados": [],
        "url_consultado": URL_REPSE_APP,
        "simulated": True,
        "nota": "Módulo shared sin Playwright. Usar mp_repse_stps.client para path real.",
    }
