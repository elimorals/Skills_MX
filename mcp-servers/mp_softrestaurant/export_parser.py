"""Parser de exports CSV de Soft Restaurant."""

from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation
from typing import Any


def _to_decimal(value: str | None) -> Decimal:
    if value is None:
        return Decimal("0")
    s = str(value).strip().replace("$", "").replace(",", "").replace(" ", "")
    if not s:
        return Decimal("0")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _normalize_header(h: str) -> str:
    return h.strip().lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")


def _detect_dialect(sample: str) -> csv.Dialect | type[csv.Dialect]:
    try:
        return csv.Sniffer().sniff(sample[:2048], delimiters=",;\t|")
    except csv.Error:
        return csv.excel


def parsear_csv_corte_z(contenido: str) -> dict[str, Any]:
    """Parsea corte Z del día (totales agregados por método pago + categoría)."""
    if not contenido.strip():
        return {"total_dia_mxn": Decimal("0"), "metodos_pago": {}, "categorias": {}}

    dialect = _detect_dialect(contenido)
    reader = csv.DictReader(io.StringIO(contenido), dialect=dialect)

    total = Decimal("0")
    metodos: dict[str, Decimal] = {}
    categorias: dict[str, Decimal] = {}

    for row in reader:
        if not row:
            continue
        normalized = {_normalize_header(k or ""): (v or "").strip() for k, v in row.items() if k}

        importe = _to_decimal(
            normalized.get("importe") or normalized.get("total") or normalized.get("monto") or "0"
        )
        total += importe

        metodo = (normalized.get("metodo_pago") or normalized.get("forma_pago") or "").strip().lower()
        if metodo:
            metodos[metodo] = metodos.get(metodo, Decimal("0")) + importe

        categoria = (normalized.get("categoria") or "").strip().lower()
        if categoria:
            categorias[categoria] = categorias.get(categoria, Decimal("0")) + importe

    return {
        "total_dia_mxn": str(total),
        "metodos_pago": {k: str(v) for k, v in metodos.items()},
        "categorias": {k: str(v) for k, v in categorias.items()},
    }


def parsear_csv_ventas_periodo(contenido: str) -> list[dict[str, Any]]:
    """Parsea ventas detalladas por periodo. Cada row = una venta."""
    if not contenido.strip():
        return []

    dialect = _detect_dialect(contenido)
    reader = csv.DictReader(io.StringIO(contenido), dialect=dialect)

    out = []
    for row in reader:
        if not row:
            continue
        normalized = {_normalize_header(k or ""): (v or "").strip() for k, v in row.items() if k}

        folio = normalized.get("folio") or normalized.get("numero") or ""
        if not folio:
            continue

        out.append({
            "folio": folio,
            "fecha": normalized.get("fecha") or "",
            "mesa": normalized.get("mesa") or "",
            "mesero": normalized.get("mesero") or "",
            "total_mxn": str(_to_decimal(normalized.get("total") or "0")),
            "metodo_pago": normalized.get("metodo_pago") or normalized.get("forma_pago") or "",
            "comensales": normalized.get("comensales") or normalized.get("personas") or "1",
            "estatus": normalized.get("estatus") or "venta",
        })
    return out


def parsear_csv_platillos_vendidos(contenido: str) -> list[dict[str, Any]]:
    """Parsea ranking de platillos vendidos (para ingeniería de menú)."""
    if not contenido.strip():
        return []

    dialect = _detect_dialect(contenido)
    reader = csv.DictReader(io.StringIO(contenido), dialect=dialect)

    out = []
    for row in reader:
        if not row:
            continue
        normalized = {_normalize_header(k or ""): (v or "").strip() for k, v in row.items() if k}

        platillo = normalized.get("platillo") or normalized.get("descripcion") or ""
        if not platillo:
            continue

        out.append({
            "platillo": platillo,
            "categoria": normalized.get("categoria") or "",
            "cantidad_vendida": int(_to_decimal(normalized.get("cantidad") or "0")),
            "total_mxn": str(_to_decimal(normalized.get("total") or "0")),
            "precio_unitario_mxn": str(_to_decimal(normalized.get("precio") or "0")),
        })
    return out
