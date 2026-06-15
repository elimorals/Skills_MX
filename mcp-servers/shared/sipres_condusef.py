"""Utilidades compartidas para CONDUSEF SIPRES.

SIPRES = Sistema de Registro de Prestadores de Servicios Financieros.
Padrón público de entidades financieras autorizadas en México (bancos,
SOFOMes, fintech IFPE, casas de cambio, aseguradoras, AFOREs, etc.).

Universo: KYC institucional, validación de proveedores fintech, due-diligence
de aseguradoras/SOFOMes antes de contratar.

Portal: https://webapps.condusef.gob.mx/SIPRES/jsp/pub/index.jsp
Endpoint backend (descubierto con Playwright MCP 2026-06-15):
    POST /SIPRES/jsp/pub/resulbusq.jsp
    Body (urlencoded): tipo=1&pnom=<nombre>&pedo=&psec=&psta=
    Response: text/html charset=ISO-8859-1 (no UTF-8 ⚠️)

Sin CAPTCHA, sin XSRF, sin sesión. Compatible httpx puro.

Schema de la respuesta HTML (columnas tabla):
    1. Clave de Registro
    2. Denominación Social
    3. Nombre Corto o comercial
    4. Estatus (En operación / Cancelado / Suspendido / etc.)
    5. Sector (Instituciones de banca múltiple, SOFOM ENR, etc.)
    6. Estado (entidad federativa del domicilio)
    7. Última Sección Actualizada
    8. No Localizable (flag)

Link al detalle:
    onclick="window.open('../../jsp/home_publico.jsp?idins=16316', ...)"
    El `idins` es el ID interno de la institución.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Optional


PORTAL_URL = "https://webapps.condusef.gob.mx/SIPRES/jsp/pub/index.jsp"
ENDPOINT_BUSQUEDA = "https://webapps.condusef.gob.mx/SIPRES/jsp/pub/resulbusq.jsp"
ENDPOINT_DETALLE = "https://webapps.condusef.gob.mx/SIPRES/jsp/home_publico.jsp"
RESPONSE_ENCODING = "iso-8859-1"  # SIPRES retorna latin-1, NO UTF-8

# Tipos de búsqueda según el handler JS cargaDatos():
#   tipo=1 → instituciones (formBusins)
#   tipo=2 → funcionarios (formBusfun, no implementado en v1)
TIPO_INSTITUCIONES = 1
TIPO_FUNCIONARIOS = 2

# Estatus comunes (se usan en filtro y resultado)
ESTATUS_OPERACION = "En operación"
ESTATUS_SUSPENDIDO = "Suspendido"
ESTATUS_CANCELADO = "Cancelado"
ESTATUS_REVOCADO = "Revocado"

# Sectores principales (SIPRES tiene ~30 sectores)
SECTORES_COMUNES = [
    "Instituciones de banca múltiple",
    "SOFOM E.N.R.",
    "SOFOM E.R.",
    "Aseguradoras",
    "AFORES",
    "Casas de Cambio",
    "Casas de Bolsa",
    "Instituciones de Fondos de Pago Electrónico (IFPE)",
    "Instituciones de Financiamiento Colectivo (IFC)",
]


@dataclass
class EntidadSIPRES:
    """Resultado normalizado de la tabla SIPRES."""
    clave_registro: str        # "40165"
    denominacion: str          # "Banco Bineo, S.A., Institución de Banca Múltiple..."
    nombre_corto: str          # "BANCO BINEO"
    estatus: str               # "En operación"
    sector: str                # "Instituciones de banca múltiple"
    estado: str                # "Ciudad de México"
    ultima_actualizacion: str  # fecha o vacío
    no_localizable: str        # flag
    idins: Optional[str] = None  # ID interno para consulta detalle (de onclick)
    estatus_tooltip: str = ""  # info adicional del title="..."

    def to_dict(self) -> dict[str, str]:
        return {
            "clave_registro": self.clave_registro,
            "denominacion": self.denominacion,
            "nombre_corto": self.nombre_corto,
            "estatus": self.estatus,
            "sector": self.sector,
            "estado": self.estado,
            "ultima_actualizacion": self.ultima_actualizacion,
            "no_localizable": self.no_localizable,
            "idins": self.idins or "",
            "estatus_tooltip": self.estatus_tooltip,
        }

    @property
    def autorizada_operacion(self) -> bool:
        """True si está vigente. Tolera variantes con/sin acentos (ISO-8859-1)."""
        norm = self.estatus.lower().replace("ó", "o").replace("á", "a")
        return "en operacion" in norm


# ============================================================
# Parsing HTML → EntidadSIPRES[]
# ============================================================

# El HTML del SIPRES es HTML4 plano sin doctype moderno. Usamos regex
# cuidadosa en lugar de BeautifulSoup para evitar dependencia externa.
# Estructura esperada por row:
#   <tr>
#     <td align='center'>40165</td>                          ← clave
#     <td><a onclick="...idins=16316...">Banco Bineo...</a></td>  ← denominación + idins
#     <td>BANCO BINEO</td>                                   ← nombre corto
#     <td title='...'><b style=color:#45B600;>En operación</b></td>  ← estatus + tooltip
#     <td>Instituciones de banca múltiple</td>               ← sector
#     <td>Ciudad de México</td>                              ← estado
#     <td>...</td>                                           ← última actualización
#     <td>...</td>                                           ← no localizable
#   </tr>

_RE_TOTAL = re.compile(
    r"<span\s+class=['\"]rojo['\"]>(\d+)</span>\s*resultados",
    re.IGNORECASE,
)
_RE_TBODY = re.compile(r"<tbody[^>]*>([\s\S]*?)</tbody>", re.IGNORECASE)
_RE_TR_BLOCK = re.compile(r"<tr[^>]*>([\s\S]*?)</tr>", re.IGNORECASE)
# Capturamos (atributos_td, contenido_td) — luego extraemos title del primer grupo
_RE_TD_BLOCK = re.compile(r"<td([^>]*)>([\s\S]*?)</td>", re.IGNORECASE)
_RE_TITLE_ATTR = re.compile(r"""\stitle\s*=\s*['"]([^'"]*)['"]""", re.IGNORECASE)
_RE_IDINS = re.compile(r"idins=(\d+)", re.IGNORECASE)
_RE_TAGS = re.compile(r"<[^>]+>")
_RE_WHITESPACE = re.compile(r"\s+")


def _limpiar_td(html_fragment: str) -> str:
    """Quita tags HTML y normaliza whitespace + entidades."""
    text = _RE_TAGS.sub(" ", html_fragment)
    text = html.unescape(text)
    return _RE_WHITESPACE.sub(" ", text).strip()


def extraer_total_resultados(body: str) -> int:
    """Lee el contador `<span class='rojo'>NN</span> resultados`."""
    m = _RE_TOTAL.search(body)
    return int(m.group(1)) if m else 0


def parsear_resultados_html(body: str) -> list[EntidadSIPRES]:
    """Parsea el HTML de respuesta y devuelve EntidadSIPRES tipadas.

    Ignora rows del header (<thead>) — solo procesa los <tr> dentro de <tbody>.
    """
    entidades: list[EntidadSIPRES] = []
    tbody_match = _RE_TBODY.search(body)
    if not tbody_match:
        return entidades

    tbody = tbody_match.group(1)
    for tr_match in _RE_TR_BLOCK.finditer(tbody):
        row_html = tr_match.group(1)
        td_matches = _RE_TD_BLOCK.findall(row_html)
        if len(td_matches) < 6:
            continue  # row con menos de 6 columnas no es resultado válido

        # Cada entry es (attrs_str, inner_html). Extraer title si está.
        cells: list[tuple[str, str]] = []
        for attrs, html_frag in td_matches:
            title_match = _RE_TITLE_ATTR.search(attrs)
            title = title_match.group(1) if title_match else ""
            cells.append((title, _limpiar_td(html_frag)))

        # idins viene del onclick de la segunda celda (link denominación)
        idins_match = _RE_IDINS.search(row_html)

        ent = EntidadSIPRES(
            clave_registro=cells[0][1],
            denominacion=cells[1][1],
            nombre_corto=cells[2][1],
            estatus=cells[3][1],
            sector=cells[4][1] if len(cells) > 4 else "",
            estado=cells[5][1] if len(cells) > 5 else "",
            ultima_actualizacion=cells[6][1] if len(cells) > 6 else "",
            no_localizable=cells[7][1] if len(cells) > 7 else "",
            idins=idins_match.group(1) if idins_match else None,
            estatus_tooltip=cells[3][0],
        )
        entidades.append(ent)
    return entidades


def validar_query(query: str) -> str:
    """Normaliza query SIPRES."""
    query = (query or "").strip()
    if len(query) < 2:
        raise ValueError("Query muy corta — mínimo 2 caracteres.")
    if len(query) > 200:
        raise ValueError("Query muy larga — máximo 200 caracteres.")
    return query


def construir_body_busqueda(
    pnom: str = "",
    pedo: str = "",
    psec: str = "",
    psta: str = "",
    tipo: int = TIPO_INSTITUCIONES,
) -> dict[str, str]:
    """Construye el body urlencoded para POST /resulbusq.jsp."""
    return {
        "tipo": str(tipo),
        "pnom": pnom,
        "pedo": pedo,
        "psec": psec,
        "psta": psta,
    }


__all__ = [
    "PORTAL_URL",
    "ENDPOINT_BUSQUEDA",
    "ENDPOINT_DETALLE",
    "RESPONSE_ENCODING",
    "TIPO_INSTITUCIONES",
    "TIPO_FUNCIONARIOS",
    "ESTATUS_OPERACION",
    "SECTORES_COMUNES",
    "EntidadSIPRES",
    "extraer_total_resultados",
    "parsear_resultados_html",
    "validar_query",
    "construir_body_busqueda",
]
