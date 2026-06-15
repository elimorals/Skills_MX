#!/usr/bin/env python3
"""Discovery automatizado mensual de portales predial municipales MX.

Objetivo: descubrir municipios nuevos con portal predial online y producir
un parche al catálogo shared/catalogo_municipios_mx.py.

Estrategia:
  1. Lee el catálogo INEGI completo (2,469 municipios).
  2. Filtra los que NO están en el catálogo actual de mp_predial_mx.
  3. Por cada municipio candidato, prueba URLs canónicas típicas:
        - https://www.{slug}.gob.mx/predial
        - https://www.{slug}.gob.mx/predial-en-linea
        - https://pago.{slug}.gob.mx
        - https://recaudacion.{slug}.gob.mx
        - https://pagoenlinea.{slug}.gob.mx/predial
  4. Marca como "candidato_validable" si HTTP 200 + content-type text/html.
  5. Genera reporte markdown + parche JSON del catálogo.

Uso:
    python3 scripts/discovery_predial_mensual.py [--state STATE] [--limit N]

Output:
    docs/discovery-predial-YYYY-MM-DD.md   (reporte)
    /tmp/predial_discovery_patch.json      (catálogo a fusionar)

Cobertura actual: 163 muns consultables / 2,469 totales = 6.6%.
Objetivo: 400 muns para 2026-Q4 = 16% de cobertura.
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from typing import Iterable

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
sys.path.insert(0, str(_REPO_ROOT / "mcp-servers"))


# ============================================================
# Configuración
# ============================================================

TIMEOUT_S = 8
MAX_WORKERS = 12
USER_AGENT = "plugins-mx/discovery_predial (compliance B2B)"


def _ssl_context() -> ssl.SSLContext:
    """SSL context con truststore o certifi."""
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except ImportError:
        try:
            import certifi
            return ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            return ssl.create_default_context()


SSL_CTX = _ssl_context()


# ============================================================
# Generación de URLs candidatas
# ============================================================

def slugify_municipio(nombre: str) -> str:
    """Convierte 'Ciudad de México' → 'ciudaddemexico' style."""
    import re
    s = nombre.lower()
    replacements = [
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
        ("ñ", "n"), ("ü", "u"),
    ]
    for src, dst in replacements:
        s = s.replace(src, dst)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def slug_municipio_dash(nombre: str) -> str:
    """Variante con guiones: 'San Pedro Garza García' → 'san-pedro-garza-garcia'."""
    import re
    s = slugify_municipio(nombre)
    # No tiene dashes porque ya quitamos non-alphanum
    # Hacer una segunda versión con dashes entre palabras
    s2 = nombre.lower()
    for src, dst in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"), ("ü", "u")]:
        s2 = s2.replace(src, dst)
    s2 = re.sub(r"[^a-z0-9]+", "-", s2).strip("-")
    return s2


def candidatas_urls(municipio: str) -> list[str]:
    """Genera URLs candidatas para un municipio (8-10 patrones comunes)."""
    nodash = slugify_municipio(municipio)
    dash = slug_municipio_dash(municipio)
    base_slugs = {nodash, dash}
    out: list[str] = []
    for slug in base_slugs:
        out.extend([
            f"https://www.{slug}.gob.mx/predial",
            f"https://{slug}.gob.mx/predial",
            f"https://www.{slug}.gob.mx/predial-en-linea",
            f"https://pago.{slug}.gob.mx/predial",
            f"https://pagoenlinea.{slug}.gob.mx/impuestopredial/",
            f"https://recaudacion.{slug}.gob.mx/predial",
            f"https://predial.{slug}.gob.mx",
            f"https://pagos.{slug}.gob.mx/predial",
        ])
    # Dedup preservando orden
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


# ============================================================
# Probe HTTP
# ============================================================

def probe_url(url: str) -> dict:
    """Probe una URL con HEAD (fallback GET) y devuelve metadata."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
        r = urllib.request.urlopen(req, timeout=TIMEOUT_S, context=SSL_CTX)
        return {
            "url": url, "status": r.status, "content_type": r.headers.get("Content-Type", ""),
            "ok": r.status == 200,
        }
    except urllib.error.HTTPError as e:
        if e.code == 405:  # Method Not Allowed → try GET
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                r = urllib.request.urlopen(req, timeout=TIMEOUT_S, context=SSL_CTX)
                return {"url": url, "status": r.status, "content_type": r.headers.get("Content-Type", ""), "ok": r.status == 200}
            except Exception:
                return {"url": url, "status": e.code, "content_type": "", "ok": False}
        return {"url": url, "status": e.code, "content_type": "", "ok": False}
    except Exception:
        return {"url": url, "status": 0, "content_type": "", "ok": False}


def probe_municipio(estado: str, municipio: str) -> dict:
    """Prueba un municipio completo: candidatas + retorna mejor match."""
    urls = candidatas_urls(municipio)
    candidate = None
    for u in urls:
        r = probe_url(u)
        if r["ok"] and "text/html" in r["content_type"].lower():
            candidate = u
            break
    return {
        "estado": estado,
        "municipio": municipio,
        "urls_probadas": len(urls),
        "candidato_url": candidate,
        "validable": candidate is not None,
    }


# ============================================================
# Main
# ============================================================

def cargar_catalogo_existente() -> set[tuple[str, str]]:
    """Lee el catálogo actual de mp_predial_mx para evitar duplicados."""
    try:
        from shared.catalogo_municipios_mx import CATALOGO_MUNICIPIOS  # type: ignore
        return {(m.get("estado", "").upper(), m.get("municipio", "").upper()) for m in CATALOGO_MUNICIPIOS}
    except Exception:
        return set()


# Lista parcial INEGI (top muns por población) — placeholder hasta tener
# el catálogo INEGI completo cargado. Para v1 usamos esta lista curada.
TOP_MUNICIPIOS_INEGI: list[tuple[str, str]] = [
    ("CDMX", "Iztapalapa"),
    ("CDMX", "Gustavo A. Madero"),
    ("CDMX", "Álvaro Obregón"),
    ("CDMX", "Coyoacán"),
    ("CDMX", "Tlalpan"),
    ("EDOMEX", "Ecatepec"),
    ("EDOMEX", "Naucalpan"),
    ("EDOMEX", "Cuautitlán Izcalli"),
    ("EDOMEX", "Atizapán"),
    ("EDOMEX", "Tultitlán"),
    ("EDOMEX", "Ixtapaluca"),
    ("EDOMEX", "Chimalhuacán"),
    ("EDOMEX", "Coacalco"),
    ("EDOMEX", "Nicolás Romero"),
    ("EDOMEX", "Texcoco"),
    ("EDOMEX", "Valle de Chalco"),
    ("EDOMEX", "Metepec"),
    ("JAL", "Tonalá"),
    ("JAL", "Tlaquepaque"),
    ("JAL", "Tlajomulco"),
    ("JAL", "El Salto"),
    ("JAL", "Puerto Vallarta"),
    ("NL", "Santa Catarina"),
    ("NL", "Cadereyta"),
    ("NL", "García"),
    ("BC", "Ensenada"),
    ("BC", "Mexicali"),
    ("BC", "Tecate"),
    ("BC", "Rosarito"),
    ("CHIH", "Delicias"),
    ("CHIH", "Cuauhtémoc"),
    ("CHIH", "Parral"),
    ("COAH", "Torreón"),
    ("COAH", "Saltillo"),
    ("COAH", "Monclova"),
    ("COAH", "Piedras Negras"),
    ("SIN", "Mazatlán"),
    ("SIN", "Los Mochis"),
    ("SIN", "Guasave"),
    ("SON", "Ciudad Obregón"),
    ("SON", "Nogales"),
    ("SON", "Navojoa"),
    ("VER", "Veracruz"),
    ("VER", "Xalapa"),
    ("VER", "Córdoba"),
    ("VER", "Coatzacoalcos"),
    ("VER", "Poza Rica"),
    ("VER", "Orizaba"),
    ("TAM", "Reynosa"),
    ("TAM", "Matamoros"),
    ("TAM", "Tampico"),
    ("TAM", "Nuevo Laredo"),
    ("TAM", "Ciudad Victoria"),
    ("YUC", "Valladolid"),
    ("YUC", "Progreso"),
    ("YUC", "Tizimín"),
    ("QROO", "Playa del Carmen"),
    ("QROO", "Chetumal"),
    ("QROO", "Cozumel"),
    ("QROO", "Tulum"),
    ("MICH", "Uruapan"),
    ("MICH", "Zamora"),
    ("MICH", "Apatzingán"),
    ("MICH", "Lázaro Cárdenas"),
    ("GTO", "Salamanca"),
    ("GTO", "Irapuato"),
    ("GTO", "Pénjamo"),
    ("GTO", "Silao"),
    ("PUE", "Tehuacán"),
    ("PUE", "Atlixco"),
    ("PUE", "Cholula"),
    ("PUE", "Huauchinango"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Discovery predial municipal MX")
    parser.add_argument("--state", default=None, help="Filtrar por estado (ej. JAL)")
    parser.add_argument("--limit", type=int, default=None, help="Máx muns a probar")
    parser.add_argument("--output-dir", default=str(_REPO_ROOT / "docs"))
    args = parser.parse_args()

    catalogo_actual = cargar_catalogo_existente()

    candidatos = TOP_MUNICIPIOS_INEGI
    if args.state:
        candidatos = [(e, m) for e, m in candidatos if e.upper() == args.state.upper()]

    # Filtrar los que ya están en catálogo
    candidatos_nuevos = [(e, m) for e, m in candidatos if (e.upper(), m.upper()) not in catalogo_actual]
    if args.limit:
        candidatos_nuevos = candidatos_nuevos[:args.limit]

    print(f"[discovery] Probando {len(candidatos_nuevos)} municipios candidatos…")

    resultados: list[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(probe_municipio, e, m): (e, m) for e, m in candidatos_nuevos}
        for f in as_completed(futures):
            r = f.result()
            estado, mun = r["estado"], r["municipio"]
            mark = "✓" if r["validable"] else "✗"
            print(f"  {mark}  {estado:6s} {mun:30s}  {r['candidato_url'] or '-'}")
            resultados.append(r)

    validables = [r for r in resultados if r["validable"]]
    print(f"\n[discovery] {len(validables)}/{len(resultados)} municipios con portal accesible.")

    # Generar reporte markdown
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date(2026, 6, 15)  # determinístico para evitar drift
    report_path = out_dir / f"discovery-predial-{today.isoformat()}.md"
    with report_path.open("w") as f:
        f.write(f"# Discovery predial municipal — {today.isoformat()}\n\n")
        f.write(f"**Probados**: {len(resultados)} municipios\n")
        f.write(f"**Con portal accesible**: {len(validables)}\n")
        f.write(f"**Catálogo actual**: {len(catalogo_actual)} muns\n\n")
        f.write("## Municipios candidatos para agregar al catálogo\n\n")
        f.write("| Estado | Municipio | URL candidata |\n|---|---|---|\n")
        for r in sorted(validables, key=lambda x: (x["estado"], x["municipio"])):
            f.write(f"| {r['estado']} | {r['municipio']} | {r['candidato_url']} |\n")
        f.write("\n## No validables (404 / unreachable)\n\n")
        for r in sorted([x for x in resultados if not x["validable"]], key=lambda x: (x["estado"], x["municipio"])):
            f.write(f"- {r['estado']} {r['municipio']}\n")

    # Generar parche JSON
    patch_path = Path("/tmp/predial_discovery_patch.json")
    with patch_path.open("w") as f:
        json.dump({
            "fecha": today.isoformat(),
            "candidatos": [
                {
                    "estado": r["estado"],
                    "municipio": r["municipio"],
                    "url": r["candidato_url"],
                    "consultable": False,  # requiere validación Playwright manual
                    "metodo": "directo",
                }
                for r in validables
            ],
        }, f, indent=2, ensure_ascii=False)

    print(f"\n[discovery] Reporte: {report_path}")
    print(f"[discovery] Parche JSON: {patch_path}")
    print(f"[discovery] Siguiente paso: validar con Playwright los {len(validables)} candidatos,")
    print(f"[discovery]   luego mergear al catálogo shared/catalogo_municipios_mx.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
