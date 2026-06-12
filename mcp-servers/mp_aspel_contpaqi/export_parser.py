"""Parser de archivos de exportación contable (Aspel COI / ContPAQi).

Soporta los formatos CSV más comunes de ambos ERPs. Sin red — todo local.

Formatos soportados:
- Pólizas CSV: número, fecha, tipo, concepto, líneas (cuenta, debe, haber)
- Balanza CSV: cuenta, nombre, saldo_inicial, cargos, abonos, saldo_final
- Catálogo de Cuentas CSV: codigo, nombre, codigo_sat, naturaleza

⚠ Aspel y ContPAQi tienen variantes de delimitador (coma vs punto y coma)
y de orden de columnas. El parser intenta auto-detectar.
"""

from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation
from typing import Any


def _to_decimal(value: str | None) -> Decimal:
    """Convierte string monetario a Decimal. Tolera comas, signos, símbolos."""
    if value is None:
        return Decimal("0")
    s = str(value).strip().replace("$", "").replace(" ", "")
    # Si tiene tanto coma como punto, la coma es separador de miles
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s and "." not in s:
        # Coma como separador decimal estilo europeo — depende del export
        # En MX típicamente es punto decimal; tratar coma como decimal solo si <= 2 digits
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            s = ".".join(parts)
        else:
            s = s.replace(",", "")
    if not s:
        return Decimal("0")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _normalize_header(header: str) -> str:
    """Normaliza header: strip, lower, sin acentos básicos."""
    h = header.strip().lower()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ñ": "n",
    }
    for k, v in replacements.items():
        h = h.replace(k, v)
    return h


def _detect_dialect(sample: str) -> csv.Dialect | type[csv.Dialect]:
    try:
        return csv.Sniffer().sniff(sample[:2048], delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def parsear_csv_polizas(contenido_csv: str) -> list[dict[str, Any]]:
    """Parsea CSV de pólizas.

    Esquema esperado (alguna variante de):
        Numero, Fecha, Tipo, Concepto, Cuenta, Debe, Haber

    Cada póliza puede tener múltiples líneas (filas) con mismo Numero.
    El parser agrupa por Numero/Fecha y devuelve estructura jerárquica.

    Returns:
        Lista de pólizas:
        [
          {
            "numero": str,
            "fecha": str,
            "tipo": str,
            "concepto": str,
            "lineas": [{"cuenta": str, "debe": Decimal, "haber": Decimal}, ...],
            "total_cargos": Decimal,
            "total_abonos": Decimal,
            "balanceada": bool,
          },
          ...
        ]
    """
    if not contenido_csv.strip():
        return []

    dialect = _detect_dialect(contenido_csv)
    reader = csv.DictReader(io.StringIO(contenido_csv), dialect=dialect)

    polizas_dict: dict[tuple[str, str], dict[str, Any]] = {}
    orden_aparicion: list[tuple[str, str]] = []

    for row in reader:
        if not row:
            continue
        normalized = {_normalize_header(k): v for k, v in row.items() if k}

        numero = (
            normalized.get("numero")
            or normalized.get("no")
            or normalized.get("no_poliza")
            or normalized.get("numero_poliza")
            or ""
        ).strip()
        fecha = (
            normalized.get("fecha")
            or normalized.get("fecha_poliza")
            or ""
        ).strip()
        tipo = (
            normalized.get("tipo")
            or normalized.get("tipo_poliza")
            or "DIARIO"
        ).strip().upper()
        concepto = (
            normalized.get("concepto")
            or normalized.get("descripcion")
            or normalized.get("glosa")
            or ""
        ).strip()
        cuenta = (
            normalized.get("cuenta")
            or normalized.get("codigo_cuenta")
            or normalized.get("codigo")
            or ""
        ).strip()
        debe = _to_decimal(normalized.get("debe") or normalized.get("cargo") or "0")
        haber = _to_decimal(normalized.get("haber") or normalized.get("abono") or "0")

        if not numero and not fecha and not cuenta:
            continue  # row vacía o header espurio

        key = (numero, fecha)
        if key not in polizas_dict:
            polizas_dict[key] = {
                "numero": numero,
                "fecha": fecha,
                "tipo": tipo,
                "concepto": concepto,
                "lineas": [],
                "total_cargos": Decimal("0"),
                "total_abonos": Decimal("0"),
            }
            orden_aparicion.append(key)
        if not polizas_dict[key]["concepto"] and concepto:
            polizas_dict[key]["concepto"] = concepto
        if cuenta:
            polizas_dict[key]["lineas"].append(
                {"cuenta": cuenta, "debe": debe, "haber": haber}
            )
            polizas_dict[key]["total_cargos"] += debe
            polizas_dict[key]["total_abonos"] += haber

    out: list[dict[str, Any]] = []
    for key in orden_aparicion:
        p = polizas_dict[key]
        p["balanceada"] = p["total_cargos"] == p["total_abonos"]
        # Convertir Decimal a string para serialización JSON estable
        p["total_cargos"] = str(p["total_cargos"])
        p["total_abonos"] = str(p["total_abonos"])
        p["lineas"] = [
            {"cuenta": l["cuenta"], "debe": str(l["debe"]), "haber": str(l["haber"])}
            for l in p["lineas"]
        ]
        out.append(p)
    return out


def parsear_csv_balanza(contenido_csv: str) -> list[dict[str, Any]]:
    """Parsea CSV de balanza de comprobación.

    Esquema esperado:
        Cuenta, Nombre, Saldo Inicial, Cargos, Abonos, Saldo Final

    Returns lista de cuentas con sus saldos.
    """
    if not contenido_csv.strip():
        return []

    dialect = _detect_dialect(contenido_csv)
    reader = csv.DictReader(io.StringIO(contenido_csv), dialect=dialect)

    out: list[dict[str, Any]] = []
    for row in reader:
        if not row:
            continue
        normalized = {_normalize_header(k): v for k, v in row.items() if k}

        cuenta = (
            normalized.get("cuenta")
            or normalized.get("codigo")
            or normalized.get("codigo_cuenta")
            or ""
        ).strip()
        if not cuenta:
            continue

        nombre = (
            normalized.get("nombre")
            or normalized.get("descripcion")
            or normalized.get("nombre_cuenta")
            or ""
        ).strip()
        saldo_inicial = _to_decimal(
            normalized.get("saldo_inicial")
            or normalized.get("saldo inicial")
            or normalized.get("inicial")
            or "0"
        )
        cargos = _to_decimal(
            normalized.get("cargos") or normalized.get("debe") or "0"
        )
        abonos = _to_decimal(
            normalized.get("abonos") or normalized.get("haber") or "0"
        )
        saldo_final = _to_decimal(
            normalized.get("saldo_final")
            or normalized.get("saldo final")
            or normalized.get("final")
            or "0"
        )

        out.append(
            {
                "cuenta": cuenta,
                "nombre": nombre,
                "saldo_inicial": str(saldo_inicial),
                "cargos": str(cargos),
                "abonos": str(abonos),
                "saldo_final": str(saldo_final),
            }
        )
    return out


def parsear_csv_catalogo_cuentas(contenido_csv: str) -> list[dict[str, Any]]:
    """Parsea CSV de catálogo de cuentas.

    Esquema esperado:
        Cuenta, Nombre, Codigo SAT, Naturaleza, Nivel

    Returns lista de cuentas del catálogo.
    """
    if not contenido_csv.strip():
        return []

    dialect = _detect_dialect(contenido_csv)
    reader = csv.DictReader(io.StringIO(contenido_csv), dialect=dialect)

    out: list[dict[str, Any]] = []
    for row in reader:
        if not row:
            continue
        normalized = {_normalize_header(k): v for k, v in row.items() if k}

        cuenta = (normalized.get("cuenta") or normalized.get("codigo") or "").strip()
        if not cuenta:
            continue

        out.append(
            {
                "cuenta": cuenta,
                "nombre": (
                    normalized.get("nombre")
                    or normalized.get("descripcion")
                    or ""
                ).strip(),
                "codigo_sat": (
                    normalized.get("codigo_sat")
                    or normalized.get("codigo sat")
                    or normalized.get("codigo agrupador")
                    or normalized.get("agrupador")
                    or ""
                ).strip(),
                "naturaleza": (
                    normalized.get("naturaleza") or ""
                ).strip().upper(),
                "nivel": (
                    normalized.get("nivel") or ""
                ).strip(),
            }
        )
    return out
