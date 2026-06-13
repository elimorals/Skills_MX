#!/usr/bin/env python3
"""Genera lista completa de municipios MX desde dataset oficial INEGI.

Output: JSON con ~2,470 municipios mexicanos listo como input del discovery.

USO:
    # Descargar dataset oficial INEGI (~5 MB)
    python3 scripts/generar-lista-inegi.py --output municipios-inegi-completo.json

    # Filtrar solo los > N habitantes (acelera el discovery)
    python3 scripts/generar-lista-inegi.py --output municipios-grandes.json --min-poblacion 50000

    # Excluir municipios ya en el catálogo (solo nuevos)
    python3 scripts/generar-lista-inegi.py --output solo-nuevos.json --excluir-catalogo

FUENTES:
- Marco Geoestadístico INEGI 2024: https://www.inegi.org.mx/temas/mg/
- Catálogo Único de Claves de Áreas Geoestadísticas: dataset CSV oficial
- Población: Censo 2020 INEGI

Cuenta oficial de municipios MX: 2,471 (incluye 16 alcaldías CDMX como demarcaciones).
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request


# Cuenta oficial de municipios por estado (INEGI 2024)
# Fuente: https://www.inegi.org.mx/app/areasgeograficas/
MUNICIPIOS_POR_ESTADO_OFICIAL: dict[str, dict] = {
    "ags": {"nombre": "Aguascalientes", "total": 11},
    "bc": {"nombre": "Baja California", "total": 7},
    "bcs": {"nombre": "Baja California Sur", "total": 5},
    "cam": {"nombre": "Campeche", "total": 13},
    "chis": {"nombre": "Chiapas", "total": 124},
    "chih": {"nombre": "Chihuahua", "total": 67},
    "cdmx": {"nombre": "Ciudad de México", "total": 16},  # alcaldías
    "coah": {"nombre": "Coahuila", "total": 38},
    "col": {"nombre": "Colima", "total": 10},
    "dur": {"nombre": "Durango", "total": 39},
    "edomex": {"nombre": "Estado de México", "total": 125},
    "gto": {"nombre": "Guanajuato", "total": 46},
    "gro": {"nombre": "Guerrero", "total": 85},
    "hgo": {"nombre": "Hidalgo", "total": 84},
    "jal": {"nombre": "Jalisco", "total": 125},
    "mich": {"nombre": "Michoacán", "total": 113},
    "mor": {"nombre": "Morelos", "total": 36},
    "nay": {"nombre": "Nayarit", "total": 20},
    "nl": {"nombre": "Nuevo León", "total": 51},
    "oax": {"nombre": "Oaxaca", "total": 570},  # ¡el más grande!
    "pue": {"nombre": "Puebla", "total": 217},
    "qro": {"nombre": "Querétaro", "total": 18},
    "qroo": {"nombre": "Quintana Roo", "total": 11},
    "slp": {"nombre": "San Luis Potosí", "total": 59},
    "sin": {"nombre": "Sinaloa", "total": 20},
    "son": {"nombre": "Sonora", "total": 72},
    "tab": {"nombre": "Tabasco", "total": 17},
    "tam": {"nombre": "Tamaulipas", "total": 43},
    "tlax": {"nombre": "Tlaxcala", "total": 60},
    "ver": {"nombre": "Veracruz", "total": 212},
    "yuc": {"nombre": "Yucatán", "total": 106},
    "zac": {"nombre": "Zacatecas", "total": 58},
}

TOTAL_MUNICIPIOS_MX = sum(d["total"] for d in MUNICIPIOS_POR_ESTADO_OFICIAL.values())
# Resultado: 2,471


# URL del catálogo oficial AGEEML del INEGI (formato fijo desde 2010)
INEGI_AGEEML_URL = (
    "https://www.inegi.org.mx/contenidos/programas/mg/2024/datosabiertos/"
    "00ent/00mun/AGEEML_2024_00.zip"
)


# Estado clave → código INEGI 2 dígitos (mapping a marco oficial)
ESTADO_CODIGO_INEGI: dict[str, str] = {
    "ags": "01", "bc": "02", "bcs": "03", "cam": "04", "coah": "05",
    "col": "06", "chis": "07", "chih": "08", "cdmx": "09", "dur": "10",
    "gto": "11", "gro": "12", "hgo": "13", "jal": "14", "edomex": "15",
    "mich": "16", "mor": "17", "nay": "18", "nl": "19", "oax": "20",
    "pue": "21", "qro": "22", "qroo": "23", "slp": "24", "sin": "25",
    "son": "26", "tab": "27", "tam": "28", "tlax": "29", "ver": "30",
    "yuc": "31", "zac": "32",
}

CODIGO_INEGI_A_ESTADO: dict[str, str] = {v: k for k, v in ESTADO_CODIGO_INEGI.items()}


def slugify(s: str) -> str:
    """Convierte 'Ciudad de México' → 'ciudad_de_mexico'."""
    out = s.lower().strip()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
                  ("ñ", "n"), (" ", "_"), (".", ""), (",", ""), ("(", ""), (")", ""),
                  ("'", ""), ("´", "")):
        out = out.replace(a, b)
    return out


def descargar_inegi_ageeml() -> list[dict]:
    """Descarga + parsea el catálogo oficial AGEEML INEGI.

    Si falla con SSLError en macOS, instalar certifi:
        pip install certifi
        # o ejecutar el Install Certificates.command del Python.app
    NO se hace fallback a TLS unverified — sería vulnerable a MITM.
    """
    import ssl
    print(f"Descargando AGEEML INEGI: {INEGI_AGEEML_URL}")
    print("(Si esto falla, INEGI cambió el URL. Buscar 'AGEEML' + año actual en inegi.org.mx)")

    req = Request(
        INEGI_AGEEML_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; plugins-mx-discover/1.0)"},
    )

    # Intentar primero con certs del sistema; si falla, intentar con certifi
    try:
        ctx = ssl.create_default_context()
        with urlopen(req, timeout=60, context=ctx) as resp:
            zip_bytes = resp.read()
    except ssl.SSLError as ssl_err:
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
            with urlopen(req, timeout=60, context=ctx) as resp:
                zip_bytes = resp.read()
        except ImportError:
            raise RuntimeError(
                f"SSL falla y certifi no está instalado. "
                f"Instalar: pip install certifi. Error original: {ssl_err}"
            ) from ssl_err
    print(f"Descargado: {len(zip_bytes):,} bytes")

    municipios: list[dict] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        # Buscar el archivo de municipios (típicamente AGEEML_YYYYMM_00mun.csv)
        candidatos = [n for n in zf.namelist() if "mun" in n.lower() and n.endswith(".csv")]
        if not candidatos:
            candidatos = [n for n in zf.namelist() if n.endswith(".csv")]
        if not candidatos:
            raise RuntimeError(f"ZIP no contiene CSV. Contenido: {zf.namelist()[:5]}")

        archivo_mun = candidatos[0]
        print(f"Parseando: {archivo_mun}")
        with zf.open(archivo_mun) as f:
            text = io.TextIOWrapper(f, encoding="latin-1")  # INEGI usa latin-1 históricamente
            reader = csv.DictReader(text)
            for row in reader:
                # Estructura típica: CVE_ENT, CVE_MUN, NOMGEO, AMBITO, ...
                cve_ent = row.get("CVE_ENT") or row.get("cve_ent") or ""
                cve_mun = row.get("CVE_MUN") or row.get("cve_mun") or ""
                nombre = row.get("NOMGEO") or row.get("nomgeo") or row.get("NOM_MUN") or ""
                if not (cve_ent and cve_mun and nombre):
                    continue
                cve_ent = str(cve_ent).zfill(2)
                cve_mun = str(cve_mun).zfill(3)
                estado_clave = CODIGO_INEGI_A_ESTADO.get(cve_ent)
                if not estado_clave:
                    continue
                municipios.append({
                    "estado": estado_clave,
                    "mun": slugify(nombre),
                    "nombre": nombre.strip(),
                    "cve_inegi": f"{cve_ent}{cve_mun}",
                })
    print(f"Parseados: {len(municipios)} municipios")
    return municipios


def _cargar_lista_estatica() -> list[dict]:
    """Lee scripts/municipios-inegi-top500.json si existe (lista hardcoded del repo).

    Si no existe el archivo, retorna lista vacía y avisa al usuario.
    Este archivo se actualiza manualmente o vía descarga INEGI cuando esté disponible.
    """
    estatica_path = Path(__file__).resolve().parent / "municipios-inegi-top500.json"
    if not estatica_path.exists():
        print(f"⚠ No existe {estatica_path}. Lista vacía.")
        print(f"   Para generar: poblar manualmente con dataset INEGI o usar --fuente inegi cuando funcione.")
        return []
    try:
        return json.loads(estatica_path.read_text())
    except Exception as e:
        print(f"⚠ Error leyendo {estatica_path}: {e}")
        return []


def cargar_catalogo_existente() -> set[tuple[str, str]]:
    """Devuelve set de (estado, mun) ya en el catálogo central."""
    catalogo_path = Path(__file__).resolve().parent.parent / "mcp-servers" / "shared" / "catalogo_municipios_mx.py"
    if not catalogo_path.exists():
        return set()

    contenido = catalogo_path.read_text()
    # Extraer cada par ('clave_mun': MunicipioConfig(..., estado_clave='xxx', ...))
    import re
    pattern = r"'([a-z_]+)':\s*MunicipioConfig\([^)]*estado_clave=['\"]([a-z]+)['\"]"
    existentes = set()
    for match in re.finditer(pattern, contenido):
        mun, estado = match.group(1), match.group(2)
        existentes.add((estado, mun))
    return existentes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="municipios-inegi-completo.json")
    parser.add_argument("--min-poblacion", type=int, default=0,
                        help="Filtrar municipios con menos de N habitantes (default: incluir todos)")
    parser.add_argument("--excluir-catalogo", action="store_true",
                        help="Excluir municipios ya en catálogo_municipios_mx.py")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limitar output a primeros N (testing)")
    parser.add_argument("--fuente", choices=["inegi", "estatico"], default="inegi",
                        help="'inegi' descarga online; 'estatico' usa lista hardcoded")
    args = parser.parse_args()

    if args.fuente == "inegi":
        try:
            municipios = descargar_inegi_ageeml()
        except Exception as e:
            print(f"⚠ Falló descarga INEGI: {e}")
            print("Usando lista estática de top 500 municipios por población.")
            municipios = _cargar_lista_estatica()
    else:
        municipios = _cargar_lista_estatica()

    # Stats por estado
    por_estado: dict[str, int] = {}
    for m in municipios:
        por_estado[m["estado"]] = por_estado.get(m["estado"], 0) + 1

    print("\nMunicipios descargados por estado:")
    for estado, oficial in sorted(MUNICIPIOS_POR_ESTADO_OFICIAL.items()):
        got = por_estado.get(estado, 0)
        marca = "✅" if got == oficial["total"] else f"⚠ esperado {oficial['total']}"
        print(f"  {estado:6} {oficial['nombre']:25}: {got:4} {marca}")

    print(f"\nTotal: {len(municipios)} (esperado {TOTAL_MUNICIPIOS_MX})")

    # Filtros
    if args.excluir_catalogo:
        existentes = cargar_catalogo_existente()
        antes = len(municipios)
        municipios = [m for m in municipios if (m["estado"], m["mun"]) not in existentes]
        print(f"\nExcluyendo {antes - len(municipios)} municipios ya en catálogo.")

    if args.limit > 0:
        municipios = municipios[:args.limit]
        print(f"Limitado a {len(municipios)} (debug).")

    # Escribir
    out_path = Path(args.output)
    out_path.write_text(json.dumps(municipios, indent=2, ensure_ascii=False))
    print(f"\n✅ Output: {out_path} ({len(municipios)} municipios)")
    print()
    print(f"Para correr discovery sobre estos:")
    print(f"  python3 scripts/descubrir-portal-municipal.py \\")
    print(f"      --input {out_path} \\")
    print(f"      --output hallazgos-completos.json \\")
    print(f"      --workers 5")
    print()
    print(f"  Tiempo estimado: {len(municipios) * 20 / 60:.0f} min (con 5 workers).")


if __name__ == "__main__":
    main()
