"""Parseo de la lista pública 69-B (EFOS) y 69 (incumplidos) del SAT.

El SAT publica ambas listas como archivos descargables. La URL exacta cambia
con frecuencia (al menos una vez al año), por lo que aquí mantenemos solo el
parser y la lógica de búsqueda — el endpoint actual se resuelve en `client.py`.

Formato típico de 69-B (CSV):
    No,RFC,Nombre del Contribuyente,Situación del Contribuyente,Número y Fecha del Oficio Global de Presunción,...

Formato típico de 69 (CSV):
    RFC,Nombre,Supuesto,Entidad Federativa,...

Esta capa NO descarga — solo parsea el contenido bruto que `client.py` le pasa.
Esto permite testear el parseo sin red.
"""

from __future__ import annotations

import csv
import io
from typing import Any


def _normalize_row(row: dict[str | None, Any]) -> dict[str, str]:
    """Normaliza un row del csv.DictReader.

    Casos a manejar:
    - Keys con espacios extra o mayúsculas — strip + lower
    - Keys None (cuando hay más columnas que headers) — se ignoran
    - Values list (cuando hay columnas extra) — se ignoran o joinean
    - Values None — se convierten a ""
    """
    out: dict[str, str] = {}
    for k, v in row.items():
        if k is None:
            continue  # columnas extra sin header
        key = k.strip().lower()
        if v is None:
            out[key] = ""
        elif isinstance(v, list):
            # Cuando DictReader recibe valores extra los pone como list bajo None
            # (no debería pasar aquí porque k is None lo filtra arriba, pero por seguridad)
            out[key] = ", ".join(str(x) for x in v).strip()
        else:
            out[key] = str(v).strip()
    return out


def parsear_csv_69b(contenido_csv: str) -> list[dict[str, Any]]:
    """Parsea un CSV de la lista 69-B EFOS.

    Tolera distintos formatos del SAT (headers en español con/sin acentos,
    columnas opcionales) y retorna registros normalizados.

    Cada registro tiene shape:
        {
          "rfc": "ABC010101001",
          "nombre": "Razón social",
          "estado_69b": "PRESUNTO" | "DEFINITIVO" | "DESVIRTUADO" | "SENTENCIA_FAVORABLE",
          "oficio_presuncion": str | None,
          "fecha_publicacion_presuncion": str | None,
          "oficio_definitivo": str | None,
          "fecha_publicacion_definitivo": str | None,
          "raw": dict,  # registro original del CSV
        }
    """
    if not contenido_csv.strip():
        return []

    # Detectar delimitador (SAT usa coma; algunos exports tabuladores)
    sample = contenido_csv[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel  # default

    reader = csv.DictReader(io.StringIO(contenido_csv), dialect=dialect)
    out: list[dict[str, Any]] = []

    for row in reader:
        normalized = _normalize_row(row)

        rfc = (
            normalized.get("rfc")
            or normalized.get("rfc del contribuyente")
            or ""
        ).upper()
        if not rfc or len(rfc) < 12:
            continue

        nombre = (
            normalized.get("nombre del contribuyente")
            or normalized.get("nombre")
            or normalized.get("razón social")
            or normalized.get("razon social")
            or ""
        )

        situacion = (
            normalized.get("situación del contribuyente")
            or normalized.get("situacion del contribuyente")
            or normalized.get("situación")
            or normalized.get("situacion")
            or ""
        ).lower()

        estado = _clasificar_estado_69b(situacion)

        out.append(
            {
                "rfc": rfc,
                "nombre": nombre,
                "estado_69b": estado,
                "oficio_presuncion": normalized.get("número y fecha del oficio global de presunción")
                or normalized.get("numero y fecha del oficio global de presuncion")
                or None,
                "fecha_publicacion_presuncion": normalized.get("publicación pagina sat presuntos")
                or normalized.get("publicacion pagina sat presuntos")
                or None,
                "oficio_definitivo": normalized.get("número y fecha del oficio global de contribuyentes que desvirtuaron")
                or normalized.get("numero y fecha del oficio global definitivos")
                or None,
                "fecha_publicacion_definitivo": normalized.get("publicación dof definitivos")
                or normalized.get("publicacion dof definitivos")
                or None,
                "raw": dict(row),
            }
        )

    return out


def _clasificar_estado_69b(situacion: str) -> str:
    """Mapea la descripción libre del SAT al catálogo estandarizado."""
    s = situacion.lower()
    if "definitivo" in s:
        return "DEFINITIVO"
    if "presunto" in s:
        return "PRESUNTO"
    if "desvirtu" in s:
        return "DESVIRTUADO"
    if "sentencia" in s and "favorable" in s:
        return "SENTENCIA_FAVORABLE"
    return "PRESUNTO"  # fallback conservador — peor caso para deducibilidad


def buscar_rfc_en_lista(
    rfc: str, registros: list[dict[str, Any]]
) -> dict[str, Any] | None:
    """Busca un RFC en la lista parseada (case-insensitive).

    Retorna el primer registro encontrado o None si no aparece.
    """
    rfc_norm = rfc.strip().upper()
    for reg in registros:
        if reg.get("rfc", "").upper() == rfc_norm:
            return reg
    return None


def parsear_csv_69_incumplidos(contenido_csv: str) -> list[dict[str, Any]]:
    """Parsea el CSV de la lista 69 (incumplidos del Art. 69 CFF).

    Formato típico:
        RFC, Nombre, Supuesto, Entidad Federativa, ...

    Cada registro normalizado:
        {
          "rfc": str,
          "nombre": str,
          "supuesto": str,  # motivo
          "entidad": str | None,
          "raw": dict,
        }
    """
    if not contenido_csv.strip():
        return []

    sample = contenido_csv[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
    except csv.Error:
        dialect = csv.excel

    reader = csv.DictReader(io.StringIO(contenido_csv), dialect=dialect)
    out: list[dict[str, Any]] = []

    for row in reader:
        normalized = _normalize_row(row)

        rfc = (normalized.get("rfc") or "").upper()
        if not rfc or len(rfc) < 12:
            continue

        nombre = (
            normalized.get("nombre")
            or normalized.get("nombre del contribuyente")
            or normalized.get("razón social")
            or normalized.get("razon social")
            or ""
        )

        supuesto = (
            normalized.get("supuesto")
            or normalized.get("motivo")
            or ""
        )

        entidad = (
            normalized.get("entidad federativa")
            or normalized.get("entidad")
            or None
        )

        out.append(
            {
                "rfc": rfc,
                "nombre": nombre,
                "supuesto": supuesto,
                "entidad": entidad,
                "raw": dict(row),
            }
        )

    return out
