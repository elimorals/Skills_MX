"""Utilidades compartidas para SAT Opinión 32-D (cumplimiento de obligaciones fiscales).

Portal:     https://ptsc32d.clouda.sat.gob.mx/ConsultaPublico
Endpoint:   POST /ConsultaPublico/Index (multipart FormData con Rfc + Curp)
Validación: 2026-06-14 con Playwright MCP — sin CAPTCHA, sin sesión, público.

Por qué importa:
    El Art. 32-D del Código Fiscal de la Federación obliga a que cualquier
    contratista del gobierno federal o que celebre operaciones con la APF debe
    estar al corriente en sus obligaciones fiscales. En el ecosistema B2B la
    consulta es práctica estándar antes de contratar a un proveedor.

    Solo aparece en la consulta pública si el contribuyente AUTORIZÓ
    publicación. Es decisión del contribuyente — no es un padrón forzoso.

Estados posibles de la opinión:
    - "positiva"        — Al corriente en sus obligaciones fiscales.
    - "negativa"        — Tiene adeudos / incumplimientos. NO contratar.
    - "no_autorizado"   — Existe en el padrón pero no autorizó publicación pública.
    - "no_inscrito"     — RFC no existe en el padrón SAT.
    - "error"           — Respuesta inesperada del backend.
"""
from __future__ import annotations

import re
from typing import Any, Literal


PORTAL_URL = "https://ptsc32d.clouda.sat.gob.mx"
CONSULTA_ENDPOINT = "/ConsultaPublico/Index"

# Regex RFC EXACTAS al portal SAT (copiadas de consultapublico.js).
# La regex original usaba entidades HTML &#xD1; (Ñ) y &amp; (&) — en Python
# las traducimos a sus caracteres reales para compilar.
# PM = persona moral (3 letras + fecha + 3 homoclave = 12 chars)
# PF = persona física (4 letras + fecha + 3 homoclave = 13 chars)
_LETRAS_RFC = r"[A-ZÑ&]"

_RFC_PM_PATTERN = re.compile(
    # Meses 31 días + días 01-31
    rf"^(({_LETRAS_RFC}{{3}})([0-9]{{2}})([0][13578]|[1][02])(([0][1-9]|[12][\d])|[3][01])([A-Z0-9]{{3}}))"
    # Meses 30 días + días 01-30
    rf"|(({_LETRAS_RFC}{{3}})([0-9]{{2}})([0][13456789]|[1][012])(([0][1-9]|[12][\d])|[3][0])([A-Z0-9]{{3}}))"
    # Febrero bisiesto: 29 de feb en años múltiplos de 4
    rf"|(({_LETRAS_RFC}{{3}})([02468][048]|[13579][26])[0][2]([0][1-9]|[12][\d])([A-Z0-9]{{3}}))"
    # Febrero no bisiesto: 01-28 de feb
    rf"|(({_LETRAS_RFC}{{3}})([0-9]{{2}})[0][2]([0][1-9]|[1][0-9]|[2][0-8])([A-Z0-9]{{3}}))$"
)

_RFC_PF_PATTERN = re.compile(
    rf"^(({_LETRAS_RFC}{{4}})([0-9]{{2}})([0][13578]|[1][02])(([0][1-9]|[12][\d])|[3][01])([A-Z0-9]{{3}}))"
    rf"|(({_LETRAS_RFC}{{4}})([0-9]{{2}})([0][13456789]|[1][012])(([0][1-9]|[12][\d])|[3][0])([A-Z0-9]{{3}}))"
    rf"|(({_LETRAS_RFC}{{4}})([02468][048]|[13579][26])[0][2]([0][1-9]|[12][\d])([A-Z0-9]{{3}}))"
    rf"|(({_LETRAS_RFC}{{4}})([0-9]{{2}})[0][2]([0][1-9]|[1][0-9]|[2][0-8])([A-Z0-9]{{3}}))$"
)

# CURP regex idéntica al portal SAT
_CURP_PATTERN = re.compile(
    r"^([A-Z][AEIOUX][A-Z]{2}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])"
    r"[HM](?:AS|B[CS]|C[CLMSH]|D[FG]|G[TR]|HG|JC|M[CNS]|N[ETL]|OC|PL|Q[TR]|"
    r"S[PLR]|T[CSL]|VZ|YN|ZS)[B-DF-HJ-NP-TV-Z]{3}[A-Z\d])(\d)$"
)


EstadoOpinion = Literal["positiva", "negativa", "no_autorizado", "no_inscrito", "error"]


def validar_estructura_rfc(rfc: str) -> bool:
    """Valida estructura RFC mexicano (PF 13 chars o PM 12 chars).

    Idéntico al validador del portal SAT — incluye lógica de días por mes y
    años bisiestos. NO valida que el RFC exista en el padrón, solo formato.
    """
    if not rfc:
        return False
    rfc = rfc.strip().upper()
    return bool(_RFC_PM_PATTERN.match(rfc) or _RFC_PF_PATTERN.match(rfc))


def validar_estructura_curp(curp: str) -> bool:
    """Valida estructura CURP — 18 chars con estado válido."""
    if not curp:
        return False
    return bool(_CURP_PATTERN.match(curp.strip().upper()))


def parsear_respuesta_html(html: str) -> dict[str, Any]:
    """Parsea HTML del portal SAT 32-D detectando estado + PDF base64.

    Args:
        html: respuesta `text/html` del endpoint /ConsultaPublico/Index

    Returns:
        {
            "estado": "positiva" | "negativa" | "error",
            "mensaje_oficial": str,
            "pdf_base64": str | None,
        }
    """
    out: dict[str, Any] = {"estado": "error", "mensaje_oficial": "", "pdf_base64": None}

    # Detectar éxito / fracaso por clase Bootstrap del alert
    m_success = re.search(
        r'<div class="alert alert-success"[^>]*>\s*<label>([\s\S]*?)</label>',
        html, re.IGNORECASE,
    )
    m_danger = re.search(
        r'<div class="alert alert-danger"[^>]*>\s*<label>([\s\S]*?)</label>',
        html, re.IGNORECASE,
    )

    if m_success:
        out["estado"] = "positiva"
        out["mensaje_oficial"] = _limpiar_html(m_success.group(1))
    elif m_danger:
        out["estado"] = "negativa"
        out["mensaje_oficial"] = _limpiar_html(m_danger.group(1))

    # PDF base64 embebido en <div id="contenidoBase64">
    m_pdf = re.search(
        r'<div id="contenidoBase64"[^>]*>([A-Za-z0-9+/=\s]+?)</div>',
        html,
    )
    if m_pdf:
        b64 = re.sub(r"\s+", "", m_pdf.group(1))
        # PDFs siempre empiezan con %PDF — en base64: "JVBERi0"
        if b64.startswith("JVBERi0"):
            out["pdf_base64"] = b64

    return out


def parsear_respuesta_json(payload: dict[str, Any]) -> dict[str, Any]:
    """Parsea respuesta JSON cuando el RFC no autorizó publicación o no existe.

    El backend SAT devuelve `{"MsjeIformativo": "..."}` (sí, con typo oficial).
    Necesitamos discriminar entre:
        - No autorizado para publicación (existe en padrón pero no autorizó)
        - No inscrito (RFC no existe en el padrón)

    El mensaje literal del SAT es ambiguo — "no se encuentra autorizado para
    hacerse público" cubre ambos. Sin información adicional, devolvemos
    estado "no_autorizado" que es el caso más común.
    """
    msj = payload.get("MsjeIformativo", "")
    msj_limpio = _limpiar_html(msj)

    estado: EstadoOpinion = "no_autorizado"
    # Heurística defensiva por si el SAT diferencia en el futuro
    # Soporta variantes: "no inscrito", "no se encuentra inscrito", "no existe", etc.
    if re.search(r"\bno\b.{0,40}(inscrit|existe|localiz)", msj_limpio, re.IGNORECASE):
        estado = "no_inscrito"

    return {
        "estado": estado,
        "mensaje_oficial": msj_limpio,
        "pdf_base64": None,
    }


def _limpiar_html(s: str) -> str:
    """Quita tags HTML básicos del mensaje del SAT."""
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)
    # SAT escapa con HTML entities en el JSON
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\s+", " ", s).strip()


__all__ = [
    "PORTAL_URL",
    "CONSULTA_ENDPOINT",
    "EstadoOpinion",
    "validar_estructura_rfc",
    "validar_estructura_curp",
    "parsear_respuesta_html",
    "parsear_respuesta_json",
]
