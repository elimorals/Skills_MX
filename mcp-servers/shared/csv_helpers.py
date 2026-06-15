"""CSV helpers reusables — preamble skip + key normalize.

Patrones extraídos de mp_sat_portal/rfc69b.py después de descubrir que MUCHOS
archivos CSV gov.mx comparten 2 quirks que rompen el csv.DictReader:

1. **Preámbulo de N líneas antes del header**: SAT pone hasta 2-3 líneas
   descriptivas/legales antes del CSV real (ej. archivos AGAFF y AGR de
   datos abiertos). El csv.DictReader asume línea 1 = header.

2. **Headers con acentos + encoding mal-decodificado**: las keys del CSV
   tienen tildes y, si el archivo viene en latin-1 leído como UTF-8 strict,
   aparecen como U+FFFD (`�`). Eso rompe los lookups por key conocida.

Reusable en futuros parsers: CSVs de CONDUSEF, COFEPRIS, RNT, donatarias, etc.
"""
from __future__ import annotations

from typing import Any


# Mapeo de caracteres comunes a normalizar
_ACENTOS_TABLE = str.maketrans({
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
    "ñ": "n", "ü": "u",
    "Á": "a", "É": "e", "Í": "i", "Ó": "o", "Ú": "u",
    "Ñ": "n",
    "�": "",  # U+FFFD replacement char (encoding broken)
})


def normalize_csv_key(key: str) -> str:
    """Normaliza una key de header CSV para matching robusto cross-encoding.

    Pipeline:
        1. strip + lowercase
        2. quita acentos (á→a, ñ→n) — para que "situación" matche "situacion"
        3. quita U+FFFD (replacement char) — viene de latin-1 leído como UTF-8
    """
    if not key:
        return ""
    return key.strip().lower().translate(_ACENTOS_TABLE)


def skip_csv_preamble_until_header(
    contenido_csv: str,
    header_marker: str = "RFC",
    max_skip_lines: int = 5,
) -> str:
    """Localiza la línea de header real saltando preámbulo legal.

    Útil para CSVs del SAT (Datos Abiertos Azure Blob) que ponen 2 líneas
    descriptivas antes del header real.

    Args:
        contenido_csv: contenido del archivo CSV completo.
        header_marker: string que identifica el header real cuando aparece
            como columna independiente. Default "RFC".
        max_skip_lines: máximo de líneas a inspeccionar antes de rendirse.
    """
    if not contenido_csv:
        return contenido_csv
    lines = contenido_csv.splitlines()
    marker_upper = header_marker.strip().upper()
    for i, line in enumerate(lines[:max_skip_lines]):
        cells = [c.strip().upper() for c in line.split(",")]
        if marker_upper in cells:
            if i == 0:
                return contenido_csv
            return "\n".join(lines[i:])
    return contenido_csv


def normalize_row(row: dict) -> dict[str, str]:
    """Normaliza un row del csv.DictReader.

    Pipeline:
        - Keys se pasan por normalize_csv_key.
        - Keys None se ignoran.
        - Values list se joinean con ", ".
        - Values None se convierten a "".
    """
    out: dict[str, str] = {}
    for k, v in row.items():
        if k is None:
            continue
        key = normalize_csv_key(k)
        if v is None:
            out[key] = ""
        elif isinstance(v, list):
            out[key] = ", ".join(str(x) for x in v).strip()
        else:
            out[key] = str(v).strip()
    return out


__all__ = [
    "normalize_csv_key",
    "skip_csv_preamble_until_header",
    "normalize_row",
]
