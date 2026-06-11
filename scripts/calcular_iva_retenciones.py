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
    """Redondeo bancario a N decimales."""
    return float(Decimal(str(valor)).quantize(Decimal(f"0.{'0' * decimales}"), rounding=ROUND_HALF_UP))


def calcular_pfae_a_pm(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """Servicios profesionales PFAE (612) → PM (601). Caso más común."""
    tasa_iva = 0.08 if frontera else 0.16
    iva = redondear(monto * tasa_iva)
    ret_isr = redondear(monto * 0.10)
    ret_iva = redondear(monto * 0.106667)

    return ResultadoCalculo(
        escenario="Servicios profesionales PFAE (612) → PM (601)",
        subtotal=monto,
        impuestos_trasladados=[
            Impuesto("IVA", "Tasa", tasa_iva, iva,
                     f"IVA {int(tasa_iva*100)}% {'frontera norte' if frontera else 'general'}")
        ],
        impuestos_retenidos=[
            Impuesto("ISR", "Tasa", 0.10, ret_isr,
                     "Retención ISR 10% servicios profesionales (Art. 106 LISR)"),
            Impuesto("IVA", "Tasa", 0.106667, ret_iva,
                     "Retención IVA 2/3 partes (10.6667%) Art. 1-A LIVA"),
        ],
        total_comprobante=redondear(monto + iva),
        neto_a_pagar_emisor=redondear(monto + iva - ret_isr - ret_iva),
        alertas=[],
    )


def calcular_resico_pf_a_pm(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """Servicios profesionales RESICO PF (626) → PM (601). Retención reducida."""
    tasa_iva = 0.08 if frontera else 0.16
    iva = redondear(monto * tasa_iva)
    ret_isr = redondear(monto * 0.0125)
    # RESICO PF NO genera retención IVA

    return ResultadoCalculo(
        escenario="Servicios profesionales RESICO PF (626) → PM (601)",
        subtotal=monto,
        impuestos_trasladados=[
            Impuesto("IVA", "Tasa", tasa_iva, iva,
                     f"IVA {int(tasa_iva*100)}% {'frontera norte' if frontera else 'general'}")
        ],
        impuestos_retenidos=[
            Impuesto("ISR", "Tasa", 0.0125, ret_isr,
                     "Retención ISR 1.25% específica de RESICO PF"),
        ],
        total_comprobante=redondear(monto + iva),
        neto_a_pagar_emisor=redondear(monto + iva - ret_isr),
        alertas=[
            "RESICO PF NO causa retención de IVA, solo ISR reducido."
        ],
    )


def calcular_pf_a_pf(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """PF a PF sin retenciones."""
    tasa_iva = 0.08 if frontera else 0.16
    iva = redondear(monto * tasa_iva)

    return ResultadoCalculo(
        escenario="Servicios entre Personas Físicas",
        subtotal=monto,
        impuestos_trasladados=[
            Impuesto("IVA", "Tasa", tasa_iva, iva,
                     f"IVA {int(tasa_iva*100)}%"),
        ],
        impuestos_retenidos=[],
        total_comprobante=redondear(monto + iva),
        neto_a_pagar_emisor=redondear(monto + iva),
        alertas=["Personas físicas no retienen entre sí."],
    )


def calcular_pm_a_pm(monto: float, frontera: bool = False) -> ResultadoCalculo:
    """PM a PM sin retenciones por servicios estándar."""
    tasa_iva = 0.08 if frontera else 0.16
    iva = redondear(monto * tasa_iva)

    return ResultadoCalculo(
        escenario="Servicios entre Personas Morales",
        subtotal=monto,
        impuestos_trasladados=[
            Impuesto("IVA", "Tasa", tasa_iva, iva,
                     f"IVA {int(tasa_iva*100)}%"),
        ],
        impuestos_retenidos=[],
        total_comprobante=redondear(monto + iva),
        neto_a_pagar_emisor=redondear(monto + iva),
        alertas=[],
    )


def calcular_exportacion(monto: float, moneda: str = "USD", tipo_cambio: float = 1.0) -> ResultadoCalculo:
    """Exportación de servicios — tasa 0%."""
    monto_mxn = redondear(monto * tipo_cambio) if moneda != "MXN" else monto

    return ResultadoCalculo(
        escenario=f"Exportación de servicios (Art. 29 LIVA), moneda {moneda}",
        subtotal=monto,
        impuestos_trasladados=[
            Impuesto("IVA", "Tasa", 0.0, 0.00,
                     "Tasa 0% por exportación. Nodo SÍ existe con importe 0.00 (no es exento)"),
        ],
        impuestos_retenidos=[],
        total_comprobante=monto,
        neto_a_pagar_emisor=monto,
        alertas=[
            f"Moneda {moneda}. Equivalente: ${monto_mxn:,.2f} MXN al TC {tipo_cambio}.",
            "Diferencia con exento: tasa 0% SÍ acumula IVA acreditable de gastos.",
            "Verificar que el servicio realmente se aprovecha en el extranjero.",
        ],
    )


def calcular_autotransporte_pf_a_pm(monto: float) -> ResultadoCalculo:
    """Autotransporte de carga PF → PM."""
    iva = redondear(monto * 0.16)
    ret_isr = redondear(monto * 0.04)
    ret_iva = redondear(monto * 0.04)

    return ResultadoCalculo(
        escenario="Autotransporte terrestre de carga PF → PM",
        subtotal=monto,
        impuestos_trasladados=[
            Impuesto("IVA", "Tasa", 0.16, iva, "IVA 16%"),
        ],
        impuestos_retenidos=[
            Impuesto("ISR", "Tasa", 0.04, ret_isr,
                     "Retención ISR 4% autotransporte"),
            Impuesto("IVA", "Tasa", 0.04, ret_iva,
                     "Retención IVA 4% (4/16 partes)"),
        ],
        total_comprobante=redondear(monto + iva),
        neto_a_pagar_emisor=redondear(monto + iva - ret_isr - ret_iva),
        alertas=[],
    )


def calcular_arrendamiento_pf_a_pm(monto: float) -> ResultadoCalculo:
    """Arrendamiento PF (régimen 606) → PM."""
    iva = redondear(monto * 0.16)
    ret_isr = redondear(monto * 0.10)
    ret_iva = redondear(monto * 0.106667)

    return ResultadoCalculo(
        escenario="Arrendamiento PF (606) → PM",
        subtotal=monto,
        impuestos_trasladados=[
            Impuesto("IVA", "Tasa", 0.16, iva, "IVA 16% arrendamiento comercial"),
        ],
        impuestos_retenidos=[
            Impuesto("ISR", "Tasa", 0.10, ret_isr, "Retención ISR 10% arrendamiento"),
            Impuesto("IVA", "Tasa", 0.106667, ret_iva, "Retención IVA 2/3 partes"),
        ],
        total_comprobante=redondear(monto + iva),
        neto_a_pagar_emisor=redondear(monto + iva - ret_isr - ret_iva),
        alertas=[
            "Si el arrendamiento es casa habitación a PF, IVA exento (no se traslada).",
        ],
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
