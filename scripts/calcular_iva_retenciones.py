#!/usr/bin/env python3
"""
Calculadora de IVA y retenciones para operaciones mexicanas.

Cubre los casos más comunes documentados en _shared/iva-retenciones-mx/.

⚠ Las tasas y reglas se actualizan periódicamente. Validar contra fuente
oficial vigente antes de uso productivo.

Uso:
    python calcular_iva_retenciones.py --emisor 612 --receptor 601 --monto 10000
    python calcular_iva_retenciones.py --emisor 626 --receptor 601 --monto 10000 --tipo-persona-emisor PF
    python calcular_iva_retenciones.py --exportacion --monto 10000 --moneda USD --tc 18.5
    python calcular_iva_retenciones.py --json --emisor 612 --receptor 601 --monto 50000
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class Impuesto:
    tipo: str  # "IVA" | "ISR"
    tasa_factor: str = "Tasa"  # "Tasa" | "Exento" | "Cuota"
    tasa: float = 0.0
    importe: float = 0.0
    razon: str = ""


@dataclass
class ResultadoCalculo:
    escenario: str
    subtotal: float
    impuestos_trasladados: list = field(default_factory=list)
    impuestos_retenidos: list = field(default_factory=list)
    total_comprobante: float = 0.0
    neto_a_pagar_emisor: float = 0.0
    alertas: list = field(default_factory=list)
    fuente_vigencia_pendiente: bool = True


def redondear(valor: float, decimales: int = 2) -> float:
    """Redondeo aritmético (ROUND_HALF_UP) a N decimales."""
    return float(Decimal(str(valor)).quantize(Decimal(f"0.{'0' * decimales}"), rounding=ROUND_HALF_UP))


def tasa_ret_iva_dos_tercios(tasa_iva: float) -> float:
    """2/3 del IVA como TasaOCuota de 6 decimales (Art. 1-A LIVA, Art. 3 fr. I RLIVA).

    16% -> 0.106667 · 8% (frontera) -> 0.053333.
    """
    return redondear(tasa_iva * 2 / 3, 6)


_C = Decimal("0.01")


def _importe(base: float, tasa: float, preferido: Decimal = None) -> float:
    """Importe = Base × TasaOCuota a 2 decimales, en Decimal (sin error binario).

    Anexo 20 acepta cualquier Importe entre
      inferior = trunc((Base − 0.005) × Tasa) y superior = ceil((Base + 0.005) × Tasa).
    Si `preferido` (p.ej. 2/3 exactos del IVA) cae en ese rango se usa; si no
    (bases grandes: 1,000,000 → 106,666.67 queda fuera), se usa Base × Tasa.
    """
    b, t = Decimal(str(base)), Decimal(str(tasa))
    if preferido is not None:
        inferior = ((b - Decimal("0.005")) * t).quantize(_C, rounding="ROUND_DOWN")
        superior = ((b + Decimal("0.005")) * t).quantize(_C, rounding="ROUND_UP")
        if inferior <= preferido <= superior:
            return float(preferido)
    return float((b * t).quantize(_C, rounding=ROUND_HALF_UP))


def _resultado(escenario: str, monto: float, tasa_iva: float, razon_iva: str,
               retenciones: list, alertas: list) -> ResultadoCalculo:
    """Total = SubTotal + Trasladados - Retenidos (Anexo 20 CFDI 4.0, atributo Total)."""
    iva = _importe(monto, tasa_iva)
    dos_tercios = (Decimal(str(iva)) * 2 / 3).quantize(_C, rounding=ROUND_HALF_UP)
    retenidos = [Impuesto(tipo, "Tasa", tasa,
                          _importe(monto, tasa, dos_tercios if tipo == "IVA" and tasa == tasa_ret_iva_dos_tercios(tasa_iva) else None),
                          razon)
                 for tipo, tasa, razon in retenciones]
    total = redondear(monto + iva - sum(r.importe for r in retenidos))
    return ResultadoCalculo(
        escenario=escenario,
        subtotal=monto,
        impuestos_trasladados=[Impuesto("IVA", "Tasa", tasa_iva, iva, razon_iva)],
        impuestos_retenidos=retenidos,
        total_comprobante=total,
        neto_a_pagar_emisor=total,
        alertas=alertas,
    )


def _iva(frontera: bool) -> tuple:
    tasa = 0.08 if frontera else 0.16
    return tasa, f"IVA {int(tasa * 100)}% {'región fronteriza (decreto vigente)' if frontera else 'general'}"


def calcular_pfae_a_pm(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """Servicios profesionales PFAE (612) -> PM (601). Caso más común."""
    tasa_iva, razon = _iva(frontera)
    ret_iva = tasa_ret_iva_dos_tercios(tasa_iva)
    return _resultado(
        "Servicios profesionales PFAE (612) → PM (601)", monto, tasa_iva, razon,
        [("ISR", 0.10, "Retención ISR 10% servicios profesionales (Art. 106 LISR)"),
         ("IVA", ret_iva, f"Retención IVA 2/3 partes ({ret_iva * 100:.4f}%) Art. 1-A fr. II a) LIVA")],
        [],
    )


def calcular_resico_pf_a_pm(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """Servicios profesionales RESICO PF (626) -> PM (601)."""
    tasa_iva, razon = _iva(frontera)
    ret_iva = tasa_ret_iva_dos_tercios(tasa_iva)
    return _resultado(
        "Servicios profesionales RESICO PF (626) → PM (601)", monto, tasa_iva, razon,
        [("ISR", 0.0125, "Retención ISR 1.25% RESICO PF (Art. 113-J LISR)"),
         ("IVA", ret_iva, f"Retención IVA 2/3 partes ({ret_iva * 100:.4f}%) Art. 1-A fr. II a) LIVA; RESICO no la elimina")],
        ["RESICO PF: la PM retiene ISR 1.25% (no 10%) y también 2/3 del IVA."],
    )


def calcular_pf_a_pf(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """PF a PF sin retenciones."""
    tasa_iva, razon = _iva(frontera)
    return _resultado("Servicios entre Personas Físicas", monto, tasa_iva, razon, [],
                      ["Personas físicas no retienen entre sí."])


def calcular_pm_a_pm(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """PM a PM sin retenciones por servicios estándar."""
    tasa_iva, razon = _iva(frontera)
    return _resultado("Servicios entre Personas Morales", monto, tasa_iva, razon, [], [])


def calcular_exportacion(monto: float, moneda: str = "USD", tipo_cambio: float = 1.0) -> ResultadoCalculo:
    """Exportación de servicios: tasa 0%."""
    monto_mxn = redondear(monto * tipo_cambio) if moneda != "MXN" else monto
    return _resultado(
        f"Exportación de servicios (Art. 29 LIVA), moneda {moneda}", monto, 0.0,
        "Tasa 0% por exportación. Nodo SÍ existe con importe 0.00 (no es exento)", [],
        [
            f"Moneda {moneda}. Equivalente: ${monto_mxn:,.2f} MXN al TC {tipo_cambio}.",
            "Diferencia con exento: tasa 0% SÍ acumula IVA acreditable de gastos.",
            "Verificar que el servicio realmente se aprovecha en el extranjero.",
        ],
    )


def calcular_autotransporte_pf_a_pm(monto: float) -> ResultadoCalculo:
    """Autotransporte terrestre de bienes PF (612) -> PM.

    IVA: retención 4% del valor (Art. 1-A fr. II c) LIVA, Art. 3 fr. II RLIVA).
    ISR: la LISR no prevé retención para este servicio con emisor 612
    (si el transportista es RESICO PF, la PM retiene 1.25%, Art. 113-J LISR).
    """
    return _resultado(
        "Autotransporte terrestre de bienes PF → PM", monto, 0.16, "IVA 16%",
        [("IVA", 0.04, "Retención IVA 4% autotransporte de bienes (Art. 1-A fr. II c) LIVA)")],
        ["La retención de IVA 4% aplica aunque el transportista sea PM.",
         "Sin retención de ISR para PF 612; si es RESICO PF agregar ISR 1.25%."],
    )


def calcular_arrendamiento_pf_a_pm(monto: float) -> ResultadoCalculo:
    """Arrendamiento PF (régimen 606) -> PM."""
    return _resultado(
        "Arrendamiento PF (606) → PM", monto, 0.16, "IVA 16% arrendamiento comercial",
        [("ISR", 0.10, "Retención ISR 10% arrendamiento (Art. 116 LISR)"),
         ("IVA", tasa_ret_iva_dos_tercios(0.16), "Retención IVA 2/3 partes Art. 1-A fr. II a) LIVA")],
        ["Si el arrendamiento es casa habitación, IVA exento (Art. 20 fr. II LIVA)."],
    )


def calcular(args) -> ResultadoCalculo:
    """Despacha al cálculo apropiado según parámetros."""
    if args.exportacion:
        return calcular_exportacion(args.monto, args.moneda, args.tc)

    if args.autotransporte:
        return calcular_autotransporte_pf_a_pm(args.monto)

    if args.arrendamiento:
        return calcular_arrendamiento_pf_a_pm(args.monto)

    # Combinaciones régimen
    emisor = args.emisor
    receptor = args.receptor
    tipo_emisor = (args.tipo_persona_emisor or "").upper()
    tipo_receptor = (args.tipo_persona_receptor or "").upper()

    # Inferir tipo persona si no fue dado
    if not tipo_emisor:
        if emisor in {"601", "603", "620", "622", "623", "624"}:
            tipo_emisor = "PM"
        elif emisor in {"605", "606", "607", "608", "611", "612", "614", "615", "621", "625"}:
            tipo_emisor = "PF"
        elif emisor == "626":
            tipo_emisor = "PF"  # default; sería ideal especificar
        else:
            tipo_emisor = "PF"

    if not tipo_receptor:
        if receptor in {"601", "603", "620", "622", "623", "624"}:
            tipo_receptor = "PM"
        elif receptor == "626":
            tipo_receptor = "PM"  # típico
        else:
            tipo_receptor = "PF"

    # Decisiones
    if emisor == "612" and tipo_receptor == "PM":
        return calcular_pfae_a_pm(args.monto, args.frontera)

    if emisor == "626" and tipo_emisor == "PF" and tipo_receptor == "PM":
        return calcular_resico_pf_a_pm(args.monto, args.frontera)

    if tipo_emisor == "PF" and tipo_receptor == "PF":
        return calcular_pf_a_pf(args.monto, args.frontera)

    if tipo_emisor == "PM" and tipo_receptor == "PM":
        return calcular_pm_a_pm(args.monto, args.frontera)

    # Fallback
    resultado = calcular_pm_a_pm(args.monto, args.frontera)
    resultado.alertas.append(
        f"Caso no específico (emisor {emisor} {tipo_emisor} → receptor {receptor} {tipo_receptor}). "
        "Validar manualmente."
    )
    return resultado


def main():
    parser = argparse.ArgumentParser(description="Calculadora de IVA y retenciones MX")
    parser.add_argument("--monto", type=float, required=True, help="Monto base (sin IVA)")
    parser.add_argument("--emisor", help="Régimen del emisor (601, 612, 626, etc.)")
    parser.add_argument("--receptor", help="Régimen del receptor")
    parser.add_argument("--tipo-persona-emisor", help="PF o PM")
    parser.add_argument("--tipo-persona-receptor", help="PF o PM")
    parser.add_argument("--frontera", action="store_true", help="Emisor en región fronteriza (IVA 8%)")
    parser.add_argument("--exportacion", action="store_true", help="Caso exportación (tasa 0%)")
    parser.add_argument("--moneda", default="MXN", help="Moneda (MXN, USD, EUR)")
    parser.add_argument("--tc", type=float, default=1.0, help="Tipo de cambio")
    parser.add_argument("--autotransporte", action="store_true", help="Caso autotransporte de carga PF→PM")
    parser.add_argument("--arrendamiento", action="store_true", help="Caso arrendamiento PF→PM")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    resultado = calcular(args)

    # Convertir dataclasses para serialización
    out = {
        "escenario": resultado.escenario,
        "subtotal": resultado.subtotal,
        "impuestos_trasladados": [asdict(i) for i in resultado.impuestos_trasladados],
        "impuestos_retenidos": [asdict(i) for i in resultado.impuestos_retenidos],
        "total_comprobante": resultado.total_comprobante,
        "neto_a_pagar_emisor": resultado.neto_a_pagar_emisor,
        "alertas": resultado.alertas,
        "fuente_vigencia_pendiente": resultado.fuente_vigencia_pendiente,
    }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"Escenario: {resultado.escenario}")
        print(f"Subtotal: ${resultado.subtotal:,.2f} {args.moneda}")
        print(f"\nImpuestos trasladados:")
        for i in resultado.impuestos_trasladados:
            print(f"  {i.tipo} {i.tasa*100:.4f}%: ${i.importe:,.2f}  ({i.razon})")
        if resultado.impuestos_retenidos:
            print(f"\nImpuestos retenidos:")
            for i in resultado.impuestos_retenidos:
                print(f"  {i.tipo} {i.tasa*100:.4f}%: -${i.importe:,.2f}  ({i.razon})")
        print(f"\nTotal del CFDI: ${resultado.total_comprobante:,.2f} {args.moneda}")
        print(f"Neto a pagar al emisor: ${resultado.neto_a_pagar_emisor:,.2f} {args.moneda}")
        if resultado.alertas:
            print(f"\nAlertas:")
            for a in resultado.alertas:
                print(f"  ⚠ {a}")
        if resultado.fuente_vigencia_pendiente:
            print(f"\n⚠ ATENCIÓN: tasas y reglas pueden estar desactualizadas.")
            print(f"  Validar contra fuente oficial vigente antes de uso productivo.")


if __name__ == "__main__":
    main()
