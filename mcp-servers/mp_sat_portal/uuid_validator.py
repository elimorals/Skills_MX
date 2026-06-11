"""Validación estructural de UUID (folio fiscal) de CFDI.

Un UUID CFDI tiene formato estricto:
- 36 caracteres: 8-4-4-4-12 hex separados por guiones
- Versión 4 (random) en el bit 13 (carácter 14)
- Variant RFC4122 en bits 17-18 (carácter 19)

Esta validación es **local y determinista** — no requiere portal SAT.

La verificación contra portal SAT (status efectivo del CFDI: vigente,
cancelado, no encontrado) se hace por separado en `client.py` y solo
trabaja contra el web service público de validación de comprobantes.

⚠ El portal SAT requiere también RFC emisor, RFC receptor y total para
verificar status. Solo el UUID por sí solo no autoriza la consulta real.
"""

from __future__ import annotations

import re
from typing import Final


UUID_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}$",
    re.IGNORECASE,
)


def normalizar_uuid(uuid: str) -> str:
    """Quita espacios, pasa a mayúsculas y retorna el UUID normalizado.

    No valida el formato — solo limpia. Para validar usa `validar_uuid`.
    """
    return uuid.strip().upper().replace(" ", "")


def validar_uuid(uuid: str) -> dict[str, object]:
    """Valida la estructura de un UUID CFDI sin tocar el portal SAT.

    Returns dict con shape estable:
        {
          "valido": bool,
          "uuid_normalizado": str,
          "razon": str | None,  # solo si valido=False
          "version_uuid": int | None,
          "es_v4_random": bool,
        }
    """
    if not isinstance(uuid, str):
        return {
            "valido": False,
            "uuid_normalizado": "",
            "razon": "El UUID debe ser una cadena de texto.",
            "version_uuid": None,
            "es_v4_random": False,
        }

    normalizado = normalizar_uuid(uuid)

    if not normalizado:
        return {
            "valido": False,
            "uuid_normalizado": "",
            "razon": "UUID vacío.",
            "version_uuid": None,
            "es_v4_random": False,
        }

    if len(normalizado) != 36:
        return {
            "valido": False,
            "uuid_normalizado": normalizado,
            "razon": f"Longitud incorrecta: {len(normalizado)} (esperado 36).",
            "version_uuid": None,
            "es_v4_random": False,
        }

    if not UUID_PATTERN.match(normalizado):
        return {
            "valido": False,
            "uuid_normalizado": normalizado,
            "razon": "Formato hex 8-4-4-4-12 inválido.",
            "version_uuid": None,
            "es_v4_random": False,
        }

    # Versión está en el primer dígito del tercer grupo (carácter índice 14)
    try:
        version = int(normalizado[14], 16)
    except ValueError:
        version = None

    return {
        "valido": True,
        "uuid_normalizado": normalizado,
        "razon": None,
        "version_uuid": version,
        "es_v4_random": version == 4,
    }


def construir_url_verificacion(
    uuid: str, rfc_emisor: str, rfc_receptor: str, total: str
) -> str:
    """Construye la URL del verificador público de CFDIs del SAT.

    El endpoint público acepta GET con query params:
    - id = UUID
    - re = RFC emisor
    - rr = RFC receptor
    - tt = total (formato decimal con 6 decimales completados con ceros)

    URL base:
    https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx

    ⚠ El portal devuelve HTML (no JSON). Para parsear el resultado real se
    requiere parser HTML o Playwright (ver `playwright_runner.py`). Esta
    función solo construye la URL — la invocación HTTP es en `client.py`.
    """
    uuid_norm = normalizar_uuid(uuid)
    re_norm = rfc_emisor.strip().upper()
    rr_norm = rfc_receptor.strip().upper()
    # SAT espera el total con punto decimal y 6 dígitos exactos a la derecha
    try:
        total_norm = f"{float(total):.6f}"
    except (TypeError, ValueError):
        total_norm = str(total)

    base = "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx"
    return f"{base}?id={uuid_norm}&re={re_norm}&rr={rr_norm}&tt={total_norm}"
