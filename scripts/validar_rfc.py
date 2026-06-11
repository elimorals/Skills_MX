#!/usr/bin/env python3
"""
Validador estructural de RFC mexicano.

Uso:
    python validar_rfc.py MAJG800101XYZ
    python validar_rfc.py MAJG800101XYZ IBM970131DRA XAXX010101000
    cat rfcs.txt | python validar_rfc.py --stdin
    python validar_rfc.py --json MAJG800101XYZ

Valida:
- Formato (regex)
- Longitud correcta (12 PM, 13 PF)
- Fecha embebida válida
- RFCs genéricos
- Palabras inconvenientes

NO valida:
- Existencia en padrón SAT (requiere API SAT)
- 69-B EFOS (requiere descarga de listado)
- Homoclave matemáticamente (requiere algoritmo SAT)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import date
from typing import Optional

# Palabras inconvenientes según SAT (lista vigente al training)
PALABRAS_INCONVENIENTES = {
    "BACA", "BAKA", "BUEI", "BUEY", "CACA", "CACO", "CAGA", "CAGO", "CAKA", "CAKO",
    "COGE", "COGI", "COJA", "COJE", "COJI", "COJO", "COLA", "CULO", "FALO", "FETO",
    "GETA", "GUEI", "GUEY", "JETA", "JOTO", "KACA", "KACO", "KAGA", "KAGO", "KAKA",
    "KAKO", "KOGE", "KOGI", "KOJA", "KOJE", "KOJI", "KOJO", "KOLA", "KULO", "LILO",
    "LOCA", "LOCO", "LOKA", "LOKO", "MAME", "MAMO", "MEAR", "MEAS", "MEON", "MIAR",
    "MION", "MOCO", "MOKO", "MULA", "MULO", "NACA", "NACO", "PEDA", "PEDO", "PENE",
    "PIPI", "PITO", "POPO", "PUTA", "PUTO", "QULO", "RATA", "ROBA", "ROBE", "ROBO",
    "RUIN", "SENO", "TETA", "VACA", "VAGA", "VAGO", "VAKA", "VUEI", "VUEY", "WUEI",
    "WUEY",
}

# RFCs genéricos válidos
RFC_GENERICOS = {
    "XAXX010101000": "publico_general_nacional",
    "XEXX010101000": "publico_general_extranjero",
}

# Regex
RE_PM = re.compile(r"^[A-ZÑ&]{3}\d{6}[A-Z0-9]{3}$")
RE_PF = re.compile(r"^[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}$")


@dataclass
class ResultadoValidacion:
    """Resultado de validar un RFC."""
    rfc_input: str
    rfc_normalizado: str = ""
    valido_estructura: bool = False
    tipo: Optional[str] = None  # "PF" | "PM" | None
    fecha_embebida: Optional[str] = None  # ISO date string
    es_generico: bool = False
    subtipo_generico: Optional[str] = None
    alertas: list = field(default_factory=list)
    errores: list = field(default_factory=list)


def normalizar(rfc: str) -> str:
    """Quita separadores y pasa a mayúsculas."""
    return rfc.upper().replace("-", "").replace(" ", "").strip()


def validar_fecha_embebida(seis_digitos: str) -> tuple[bool, Optional[str], Optional[str]]:
    """Valida los 6 dígitos centrales como fecha.

    Returns:
        (es_valida, fecha_iso o None, error o None)
    """
    if not seis_digitos.isdigit() or len(seis_digitos) != 6:
        return False, None, "Los 6 dígitos centrales no son numéricos"

    año = int(seis_digitos[0:2])
    mes = int(seis_digitos[2:4])
    dia = int(seis_digitos[4:6])

    # Determinar siglo (1900s o 2000s)
    año_actual = date.today().year % 100
    siglo = 2000 if año <= año_actual + 5 else 1900
    año_completo = siglo + año

    if mes < 1 or mes > 12:
        return False, None, f"Mes inválido: {mes}"

    if dia < 1 or dia > 31:
        return False, None, f"Día inválido: {dia}"

    try:
        fecha = date(año_completo, mes, dia)
        # Validar no futuro
        if fecha > date.today():
            return False, None, f"Fecha futura: {fecha.isoformat()}"
        # Validar no muy antigua
        if año_completo < 1900:
            return False, None, f"Año muy antiguo: {año_completo}"
        return True, fecha.isoformat(), None
    except ValueError as e:
        return False, None, f"Fecha inválida: {e}"


def validar_rfc(rfc_input: str) -> ResultadoValidacion:
    """Valida un RFC mexicano estructuralmente."""
    resultado = ResultadoValidacion(rfc_input=rfc_input)

    rfc = normalizar(rfc_input)
    resultado.rfc_normalizado = rfc

    # Genérico?
    if rfc in RFC_GENERICOS:
        resultado.es_generico = True
        resultado.subtipo_generico = RFC_GENERICOS[rfc]
        resultado.valido_estructura = True
        resultado.tipo = "PF"  # ambos genéricos son tratados como PF
        # Fecha embebida ficticia 010101
        es_valida, fecha, _ = validar_fecha_embebida(rfc[4:10] if len(rfc) == 13 else rfc[3:9])
        if es_valida:
            resultado.fecha_embebida = fecha
        resultado.alertas.append(
            "RFC genérico válido solo como receptor con UsoCFDI = S01 "
            "en factura global de público en general."
        )
        return resultado

    # Determinar tipo por longitud
    if len(rfc) == 13:
        resultado.tipo = "PF"
        regex = RE_PF
        letras_iniciales = rfc[0:4]
        fecha_str = rfc[4:10]
    elif len(rfc) == 12:
        resultado.tipo = "PM"
        regex = RE_PM
        letras_iniciales = rfc[0:3]
        fecha_str = rfc[3:9]
    else:
        resultado.errores.append(
            f"Longitud incorrecta: {len(rfc)} caracteres "
            f"(PF debe ser 13, PM debe ser 12)"
        )
        return resultado

    # Validar regex
    if not regex.match(rfc):
        resultado.errores.append(
            "Formato no cumple regex estructural para "
            f"{resultado.tipo}"
        )
        return resultado

    # Validar fecha embebida
    fecha_valida, fecha_iso, error_fecha = validar_fecha_embebida(fecha_str)
    if not fecha_valida:
        resultado.errores.append(f"Fecha embebida inválida: {error_fecha}")
        return resultado
    resultado.fecha_embebida = fecha_iso

    # Validar palabras inconvenientes (solo PF, 4 letras iniciales)
    if resultado.tipo == "PF":
        if letras_iniciales in PALABRAS_INCONVENIENTES:
            resultado.alertas.append(
                f"RFC sospechoso: las 4 primeras letras ({letras_iniciales}) "
                "forman una palabra que el SAT habría sustituido automáticamente. "
                "Verificar que sea el RFC real del contribuyente."
            )

    resultado.valido_estructura = True
    return resultado


def formato_humano(resultado: ResultadoValidacion) -> str:
    """Formatea resultado para lectura humana."""
    lines = []
    estado = "✓ Válido" if resultado.valido_estructura else "✗ Inválido"
    lines.append(f"RFC: {resultado.rfc_input}")
    if resultado.rfc_normalizado != resultado.rfc_input:
        lines.append(f"Normalizado: {resultado.rfc_normalizado}")
    lines.append(f"Estado: {estado}")
    if resultado.tipo:
        lines.append(f"Tipo: {resultado.tipo}")
    if resultado.fecha_embebida:
        lines.append(f"Fecha embebida: {resultado.fecha_embebida}")
    if resultado.es_generico:
        lines.append(f"Genérico: {resultado.subtipo_generico}")
    if resultado.alertas:
        lines.append("Alertas:")
        for a in resultado.alertas:
            lines.append(f"  ⚠ {a}")
    if resultado.errores:
        lines.append("Errores:")
        for e in resultado.errores:
            lines.append(f"  ✗ {e}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validador estructural de RFC mexicano")
    parser.add_argument("rfcs", nargs="*", help="RFCs a validar")
    parser.add_argument("--stdin", action="store_true", help="Leer RFCs de stdin")
    parser.add_argument("--json", action="store_true", help="Output en JSON")
    args = parser.parse_args()

    rfcs = []
    if args.stdin:
        rfcs = [line.strip() for line in sys.stdin if line.strip()]
    else:
        rfcs = args.rfcs

    if not rfcs:
        parser.print_help()
        sys.exit(1)

    resultados = [validar_rfc(rfc) for rfc in rfcs]

    if args.json:
        print(json.dumps([asdict(r) for r in resultados], indent=2, ensure_ascii=False))
    else:
        for i, r in enumerate(resultados):
            if i > 0:
                print("─" * 40)
            print(formato_humano(r))

    # Exit code
    exit_code = 0 if all(r.valido_estructura for r in resultados) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
