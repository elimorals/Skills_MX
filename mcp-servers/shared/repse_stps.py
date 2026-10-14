"""Consulta REPSE (Registro Público de empresas de Subcontratación STPS).

Portal: https://repse.stps.gob.mx/ (Laravel). Endpoints JSON detrás del
formulario "Consultar Padrón" (leídos de build/assets/sourceInicio-*.js,
validados en vivo 2026-10-14):

- GET  /busca_razon_social?term=<folio | RFC | razón social>
       → {"success": true, "results": [{"id": 2235, "text": "BIMBO SA DE CV"}]}
- POST /buscar-padron  multipart razon_social=<id>, header X-CSRF-TOKEN
       (meta csrf-token del HTML) + cookie de sesión
       → {"registro": 1, "data": {folio, razon_social, rfc, entidad, municipio,
          abreviatura, num_emi, fecha_registro, fecha_vencimiento_registro},
          "actividades": [{"descripcion": ...}]}

Sin CAPTCHA. Sin login.
"""

from __future__ import annotations

import re
from typing import Any, Optional


URL_REPSE_PORTAL = "https://repse.stps.gob.mx/Publico"
URL_REPSE_BASE = "https://repse.stps.gob.mx"
URL_REPSE_APP = "https://repse.stps.gob.mx/"  # /app/ ya no existe (404 desde 2026)



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


def mapear_detalle(resp: dict[str, Any]) -> dict[str, Any]:
    """Respuesta de /buscar-padron → schema del MCP."""
    d = resp.get("data") or {}
    fecha_reg = (d.get("fecha_registro") or "")[:10] or None
    vigencia = (d.get("fecha_vencimiento_registro") or "")[:10] or None
    aviso = None
    if d.get("abreviatura") and d.get("num_emi") is not None and fecha_reg:
        aviso = f"{d['abreviatura']}-{d['num_emi']}/{fecha_reg[:4]}"
    return {
        "numero_registro": str(d.get("folio")) if d.get("folio") is not None else None,
        "folio": d.get("folio"),
        "razon_social": d.get("razon_social"),
        "rfc": d.get("rfc"),
        "entidad": d.get("entidad"),
        "municipio": d.get("municipio"),
        "aviso_registro": aviso,
        "fecha_aviso": fecha_reg,
        "vigencia": vigencia,
        "servicios": [a.get("descripcion", "").strip() for a in resp.get("actividades") or []],
    }
