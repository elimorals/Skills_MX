#!/usr/bin/env python3
"""
Formateador y normalizador de moneda MXN.

Uso:
    python format_mxn.py 1234.56
    python format_mxn.py "1,234.56" --letras
    python format_mxn.py 1500000 --moneda USD
    python format_mxn.py --json 1234.56
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class ResultadoFormato:
    monto_input: str
    monto_normalizado: float = 0.0
    formato_corto: str = ""
    formato_largo: str = ""
    letra: str = ""
    moneda: str = "MXN"
    alertas: list = field(default_factory=list)


# Tablas para conversión a letra
UNIDADES = [
    "", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE",
    "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISÉIS",
    "DIECISIETE", "DIECIOCHO", "DIECINUEVE", "VEINTE", "VEINTIUNO", "VEINTIDÓS",
    "VEINTITRÉS", "VEINTICUATRO", "VEINTICINCO", "VEINTISÉIS", "VEINTISIETE",
    "VEINTIOCHO", "VEINTINUEVE",
]

DECENAS = [
    "", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA",
    "SETENTA", "OCHENTA", "NOVENTA",
]

CENTENAS = [
    "", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS",
    "QUINIENTOS", "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS",
]


def numero_a_letras_hasta_999(n: int) -> str:
    """Convierte 0-999 a letras."""
    if n == 0:
        return ""
    if n < 30:
        return UNIDADES[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DECENAS[d] + (" Y " + UNIDADES[u] if u else "")
    if n == 100:
        return "CIEN"
    c, resto = divmod(n, 100)
    return CENTENAS[c] + (" " + numero_a_letras_hasta_999(resto) if resto else "")


def numero_a_letras(n: int) -> str:
    """Convierte cualquier entero a letras, formato CFDI MX."""
    if n == 0:
        return "CERO"
    if n < 0:
        return "MENOS " + numero_a_letras(-n)

    partes = []
    # Millones
    millones, resto = divmod(n, 1_000_000)
    if millones:
        if millones == 1:
            partes.append("UN MILLÓN")
        else:
            partes.append(numero_a_letras_hasta_999(millones // 1000 or 1) if millones >= 1000 else "")
            if millones >= 1000:
                miles_m, m = divmod(millones, 1000)
                partes_m = []
                if miles_m == 1:
                    partes_m.append("MIL")
                elif miles_m > 0:
                    partes_m.append(numero_a_letras_hasta_999(miles_m) + " MIL")
                if m:
                    partes_m.append(numero_a_letras_hasta_999(m))
                partes.append(" ".join(partes_m) + " MILLONES")
            else:
                partes.append(numero_a_letras_hasta_999(millones) + " MILLONES")

    # Miles
    miles, resto_final = divmod(resto, 1000)
    if miles == 1:
        partes.append("UN MIL")  # Convención CFDI
    elif miles > 0:
        partes.append(numero_a_letras_hasta_999(miles) + " MIL")

    # Resto
    if resto_final > 0:
        partes.append(numero_a_letras_hasta_999(resto_final))

    return " ".join(p for p in partes if p).strip()


def monto_a_letra(monto: float, moneda: str = "MXN") -> str:
    """Genera representación canónica CFDI: 'UN MIL PESOS 56/100 M.N.'"""
    dec = Decimal(str(monto)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    enteros = int(dec)
    centavos = int((dec - enteros) * 100)

    if moneda == "MXN":
        unidad = "PESO" if enteros == 1 else "PESOS"
        sufijo = "M.N."
    elif moneda == "USD":
        unidad = "DÓLAR AMERICANO" if enteros == 1 else "DÓLARES AMERICANOS"
        sufijo = "USD"
    elif moneda == "EUR":
        unidad = "EURO" if enteros == 1 else "EUROS"
        sufijo = "EUR"
    else:
        unidad = moneda
        sufijo = moneda

    letras_enteros = numero_a_letras(enteros)
    return f"{letras_enteros} {unidad} {centavos:02d}/100 {sufijo}"


def normalizar_monto(input_str: str) -> tuple[float, list]:
    """Normaliza diferentes formatos de entrada a float.

    Returns:
        (monto_float, alertas)
    """
    alertas = []
    s = input_str.strip().replace("$", "").replace("MXN", "").replace("USD", "").strip()

    # Detectar formato europeo (decimal con coma)
    # Heurística: si hay un . y una ,, el formato europeo tiene . como miles y , como decimal
    # Si solo hay , y está al final con 2 dígitos: probable decimal europeo
    if "." in s and "," in s:
        if s.rindex(",") > s.rindex("."):
            # Formato europeo: 1.234,56
            s = s.replace(".", "").replace(",", ".")
            alertas.append("Detectado formato europeo (decimal con coma). Normalizado a punto.")
    elif "," in s and "." not in s:
        # Podría ser solo separador de miles o decimal europeo
        partes = s.split(",")
        if len(partes) == 2 and len(partes[1]) == 2:
            # 2 decimales después de coma → probable decimal europeo
            s = s.replace(",", ".")
            alertas.append("Asumido como decimal europeo. Verificar si era separador de miles.")
        else:
            # Asumir separador de miles
            s = s.replace(",", "")

    s = s.replace(",", "")  # Quitar comas restantes (separadores de miles)

    # Manejar "1.5k", "2 millones"
    s_lower = input_str.lower()
    if "k" in s_lower and re.match(r"^\d+\.?\d*k$", s_lower.strip().replace("$", "").strip()):
        n = float(s_lower.replace("k", "").replace("$", "").strip())
        return n * 1000, alertas
    if "millon" in s_lower or "millón" in s_lower:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:millon|millón)", s_lower)
        if match:
            n = float(match.group(1))
            return n * 1_000_000, alertas + ["Detectada palabra 'millón'."]

    try:
        valor = float(s)
        # Verificar precision (más de 2 decimales)
        if "." in s:
            decimales = len(s.split(".")[1])
            if decimales > 2:
                alertas.append(f"Input tenía {decimales} decimales. Redondeado a 2.")
        return valor, alertas
    except ValueError:
        raise ValueError(f"No se pudo interpretar el monto: '{input_str}'")


def formatear(monto_input: str, moneda: str = "MXN", incluir_letra: bool = True) -> ResultadoFormato:
    """Formatea un monto a salida canónica."""
    resultado = ResultadoFormato(monto_input=monto_input, moneda=moneda)

    try:
        valor, alertas = normalizar_monto(monto_input)
    except ValueError as e:
        resultado.alertas.append(str(e))
        return resultado

    resultado.alertas.extend(alertas)

    # Redondear a 2 decimales
    valor_dec = Decimal(str(valor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    resultado.monto_normalizado = float(valor_dec)

    # Formato corto
    if valor < 0:
        resultado.formato_corto = f"-${abs(valor_dec):,.2f}"
    else:
        resultado.formato_corto = f"${valor_dec:,.2f}"

    # Formato largo
    resultado.formato_largo = f"{resultado.formato_corto} {moneda}"

    # Letra
    if incluir_letra:
        resultado.letra = monto_a_letra(float(valor_dec), moneda)

    return resultado


def main():
    parser = argparse.ArgumentParser(description="Formateador de moneda MXN")
    parser.add_argument("monto", help="Monto a formatear (acepta varios formatos)")
    parser.add_argument("--moneda", default="MXN", choices=["MXN", "USD", "EUR", "CAD"])
    parser.add_argument("--sin-letra", action="store_true", help="No incluir conversión a letra")
    parser.add_argument("--json", action="store_true", help="Output en JSON")
    args = parser.parse_args()

    resultado = formatear(args.monto, args.moneda, not args.sin_letra)

    if args.json:
        print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
    else:
        print(f"Input: {resultado.monto_input}")
        print(f"Normalizado: {resultado.monto_normalizado}")
        print(f"Formato corto: {resultado.formato_corto}")
        print(f"Formato largo: {resultado.formato_largo}")
        if resultado.letra:
            print(f"En letra: {resultado.letra}")
        if resultado.alertas:
            print("Alertas:")
            for a in resultado.alertas:
                print(f"  ⚠ {a}")


if __name__ == "__main__":
    main()
