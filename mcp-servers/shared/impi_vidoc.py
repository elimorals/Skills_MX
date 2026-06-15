"""Utilidades para IMPI ViDoc (Visualización electrónica de Documentos PI).

Reemplaza al MARCANET descontinuado. Portal actual:
    https://vidoc.impi.gob.mx/busc

Endpoint backend (descubierto con Playwright MCP 2026-06-15):
    POST /api/BusquedaDocumentos/getBusquedaSimpleNdjson
    Body: {"busqueda": "TELMEX", "recaptcha": "<v3 token>"}
    Headers: X-XSRF-TOKEN: <ASP.NET Core DataProtection token>
    Response: application/x-ndjson (864 docs típicos sin paginación server-side)

Áreas posibles (idArea):
    114 = MARCAS
    115 = PATENTES (DEEPL: pendiente confirmar)
    116 = DISEÑOS INDUSTRIALES (pendiente)
    117 = ASUNTOS CONTENCIOSOS (pendiente)

Schema de cada línea NDJSON:
    {
      "event": "processing" | "complete",
      "data": {
        "expedienteODocumento": "MA/M/1985/3502080",
        "idArea": 114,
        "area": "MARCAS",
        "anio": 2025,
        "isExpediente": "expediente",
        "expediente": "3502080",
        "tipoExpediente": "MARCA",
        "fichaDatos": [{"descripcion": "...", "valor": "..."}]
      }
    }
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional


PORTAL_URL = "https://vidoc.impi.gob.mx/busc"
API_ENDPOINT = "/api/BusquedaDocumentos/getBusquedaSimpleNdjson"
API_URL_PATTERN = r"/api/BusquedaDocumentos/getBusquedaSimpleNdjson"
SEARCH_INPUT_SELECTOR = 'input[type="search"]'
SEARCH_BUTTON_SELECTOR = 'button[aria-label="Search"]'

# Áreas conocidas del IMPI ViDoc
AREA_MARCAS = 114

# Mapping ficha descripcion → key normalizada (snake_case)
# Las keys exactas vienen del front-end IMPI; este mapping las traduce a algo
# usable por agentes de IA sin parsear strings con espacios y acentos.
_FICHA_KEYS = {
    "Num. Expediente": "num_expediente",
    "Expediente": "expediente",
    "Expediente Interno": "expediente_interno",
    "Título o Denominación": "denominacion",
    "Titulo o Denominacion": "denominacion",  # variantes sin acentos
    "Fecha": "fecha",
    "Titular": "titular",
    "Nacionalidad (Titular.)": "titular_nacionalidad",
    "Estado (Titular.)": "titular_estado",
    "Tipo Descripción": "tipo_descripcion",
    "Tipo Descripcion": "tipo_descripcion",
    "Clase": "clase_niza",
    "Inventor": "inventor",
    "Causahabiente": "causahabiente",
    "Apoderado": "apoderado",
    "Vigencia": "vigencia",
    "Status": "status",
    "Estado del Expediente": "estado_expediente",
    "Fecha de Solicitud": "fecha_solicitud",
    "Fecha de Concesión": "fecha_concesion",
    "Fecha de Concesion": "fecha_concesion",
}


@dataclass
class MarcaIMPI:
    """Resultado normalizado de un documento del IMPI ViDoc."""
    expediente: str               # "MA/M/1985/3502080" (id global)
    numero_expediente: str        # "3502080"
    area: str                     # "MARCAS"
    anio: int
    tipo_expediente: str          # "MARCA", "PATENTE", "DISEÑO"
    denominacion: str = ""        # "RELLAMADO TELMEX"
    titular: str = ""             # "TELEFONOS DE MEXICO, S.A.B. DE C.V."
    titular_nacionalidad: str = ""
    titular_estado: str = ""      # ubicación del titular
    clase_niza: str = ""          # "38" (clasificación internacional)
    tipo_descripcion: str = ""    # "DENOMINACION" / "MIXTA" / "INNOMINADA"
    fecha: str = ""               # ISO timestamp
    raw_ficha_datos: list[dict[str, str]] = field(default_factory=list)
    raw_ficha_normalizada: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "expediente": self.expediente,
            "numero_expediente": self.numero_expediente,
            "area": self.area,
            "anio": self.anio,
            "tipo_expediente": self.tipo_expediente,
            "denominacion": self.denominacion,
            "titular": self.titular,
            "titular_nacionalidad": self.titular_nacionalidad,
            "titular_estado": self.titular_estado,
            "clase_niza": self.clase_niza,
            "tipo_descripcion": self.tipo_descripcion,
            "fecha": self.fecha,
            "raw_ficha_normalizada": self.raw_ficha_normalizada,
        }


def normalizar_ficha_datos(ficha: list[dict[str, str]]) -> dict[str, str]:
    """Convierte [{descripcion, valor}] a {key_snake_case: valor}."""
    out: dict[str, str] = {}
    for item in ficha:
        descripcion = (item.get("descripcion") or "").strip()
        valor = (item.get("valor") or "").strip()
        if not descripcion or not valor:
            continue
        key = _FICHA_KEYS.get(descripcion)
        if key is None:
            # Fallback: snake_case del descripcion
            key = _to_snake_case(descripcion)
        # No sobrescribir si el key ya está presente (primer match gana)
        if key not in out:
            out[key] = valor
    return out


def _to_snake_case(s: str) -> str:
    """Convierte 'Título o Denominación' → 'titulo_o_denominacion'."""
    s = s.lower()
    # Quita acentos básicos
    for src, dst in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                     ("ñ", "n"), ("ü", "u")]:
        s = s.replace(src, dst)
    # Quita paréntesis y puntos
    s = re.sub(r"[()\\.]+", "", s)
    # Espacios → guiones bajos
    s = re.sub(r"\s+", "_", s.strip())
    # Caracteres no-alfanum → guion bajo
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def parsear_ndjson_response(body: str) -> Iterator[MarcaIMPI]:
    """Itera sobre líneas NDJSON y yield un MarcaIMPI por documento.

    Filtra eventos no-data (event != "processing"). Tolera líneas malformadas.
    """
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("event") not in ("processing", "complete", None):
            # Evento administrativo (heartbeat, total, etc.) — skip
            continue
        data = payload.get("data")
        if not isinstance(data, dict):
            continue
        marca = _payload_to_marca(data)
        if marca:
            yield marca


def _payload_to_marca(data: dict[str, Any]) -> Optional[MarcaIMPI]:
    """Convierte un payload `data` del NDJSON a MarcaIMPI tipada."""
    expediente = data.get("expedienteODocumento") or data.get("expediente") or ""
    if not expediente:
        return None

    ficha_raw = data.get("fichaDatos") or []
    ficha_norm = normalizar_ficha_datos(ficha_raw)

    return MarcaIMPI(
        expediente=expediente,
        numero_expediente=str(data.get("expediente") or ""),
        area=data.get("area") or "",
        anio=int(data.get("anio") or 0),
        tipo_expediente=data.get("tipoExpediente") or "",
        denominacion=ficha_norm.get("denominacion", ""),
        titular=ficha_norm.get("titular", ""),
        titular_nacionalidad=ficha_norm.get("titular_nacionalidad", ""),
        titular_estado=ficha_norm.get("titular_estado", ""),
        clase_niza=ficha_norm.get("clase_niza", ""),
        tipo_descripcion=ficha_norm.get("tipo_descripcion", ""),
        fecha=ficha_norm.get("fecha", ""),
        raw_ficha_datos=ficha_raw,
        raw_ficha_normalizada=ficha_norm,
    )


def validar_query(query: str) -> str:
    """Normaliza y valida un término de búsqueda IMPI.

    - Strip + upper para coincidir con cómo el portal lo trata.
    - Length mínima 2 (el portal acepta queries muy cortas pero devuelve ruido).
    - Length máxima 200.
    """
    query = (query or "").strip()
    if len(query) < 2:
        raise ValueError("Query muy corta — mínimo 2 caracteres.")
    if len(query) > 200:
        raise ValueError("Query muy larga — máximo 200 caracteres.")
    return query.upper()


__all__ = [
    "PORTAL_URL",
    "API_ENDPOINT",
    "API_URL_PATTERN",
    "SEARCH_INPUT_SELECTOR",
    "SEARCH_BUTTON_SELECTOR",
    "AREA_MARCAS",
    "MarcaIMPI",
    "normalizar_ficha_datos",
    "parsear_ndjson_response",
    "validar_query",
]
