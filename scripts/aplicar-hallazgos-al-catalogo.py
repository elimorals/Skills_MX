#!/usr/bin/env python3
"""Aplica hallazgos del discovery al catalogo_municipios_mx.py.

Toma el JSON output de scripts/descubrir-portal-municipal.py, filtra los OK
(con form pago real detectado) y actualiza las entries correspondientes en
shared/catalogo_municipios_mx.py.

Detecta y descarta falsos positivos automáticamente:
- Forms de login (username, password, wp-login, modlgn-)
- Buscadores del sitio (s, q, search, searchword)
- Newsletter (subscribe, boletin)
- Captcha responses (g-recaptcha-response)

USO:
    # Desde scripts/discovery
    python3 scripts/aplicar-hallazgos-al-catalogo.py hallazgos-144-2026-06-13.json

    # Solo dry-run (no modifica catálogo, solo reporta qué cambiaría)
    python3 scripts/aplicar-hallazgos-al-catalogo.py hallazgos.json --dry-run

    # Aplicar y commitear automáticamente
    python3 scripts/aplicar-hallazgos-al-catalogo.py hallazgos.json --commit
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOGO = REPO_ROOT / "mcp-servers" / "shared" / "catalogo_municipios_mx.py"


# Patrones que indican falso positivo
FALSOS_POSITIVOS_NAMES = {
    "username", "user", "password", "pass", "passwd", "email", "login",
    "s", "q", "search", "keys", "edit-keys", "buscar",
    "searchword", "search_word", "searchterm",
    "g-recaptcha-response", "h-captcha-response", "captcha", "captcha_code",
}

FALSOS_POSITIVOS_ID_PREFIX = ("modlgn-", "user_login", "wp-", "mod-search-")
FALSOS_POSITIVOS_FORM_ACTION = ("login", "wp-login", "session", "search")


def es_falso_positivo(hallazgo: dict) -> tuple[bool, str | None]:
    """Detecta si un hallazgo OK es realmente un falso positivo.

    Returns:
        (es_falso, razon_si_lo_es)
    """
    selectores = hallazgo.get("selectores") or {}
    inputs_lista = selectores.get("input", [])

    for sel in inputs_lista:
        sel_low = sel.lower()
        # input[name='X']
        m = re.search(r"input\[name=['\"]([^'\"]+)['\"]", sel_low)
        if m and m.group(1) in FALSOS_POSITIVOS_NAMES:
            return True, f"form de login/search detectado: name='{m.group(1)}'"
        # input#X
        m = re.search(r"input#([a-z0-9_-]+)", sel_low)
        if m:
            id_val = m.group(1)
            for prefix in FALSOS_POSITIVOS_ID_PREFIX:
                if id_val.startswith(prefix):
                    return True, f"id sugiere CMS/login: '{id_val}'"

    # También revisar inputs_visibles para más contexto
    for inp in hallazgo.get("inputs_visibles", []):
        name = (inp.get("name") or "").lower()
        if name in FALSOS_POSITIVOS_NAMES:
            return True, f"input visible es buscador/login: name='{name}'"
        form_action = (inp.get("form_action") or "").lower()
        for fp in FALSOS_POSITIVOS_FORM_ACTION:
            if fp in form_action and "predial" not in form_action:
                return True, f"form action='{form_action}' no es portal pago"

    return False, None


def construir_entry_python(hallazgo: dict, nombre_real: str, poblacion: int) -> str:
    """Genera bloque Python MunicipioConfig para insertar en catálogo."""
    estado = hallazgo["estado"]
    mun = hallazgo["mun"]
    url = hallazgo["url_real"]
    selectores = hallazgo.get("selectores") or {}
    stack = hallazgo.get("stack_detectado", "unknown")
    fecha = datetime.now().strftime("%Y-%m-%d")

    if selectores.get("input"):
        sel_repr = repr(selectores)
        nota = f"✅ Auto-discovery {fecha}: stack={stack}. Selectores derivados, validar manualmente antes de producción."
        return (
            f"        {mun!r}: MunicipioConfig(\n"
            f"            nombre={nombre_real!r}, estado_clave={estado!r},\n"
            f"            portal_predial_url={url!r},\n"
            f"            selectores_predial={sel_repr},\n"
            f"            poblacion_aprox={poblacion}, validado=True,\n"
            f"            notas={nota!r},\n"
            f"        ),"
        )
    nota = f"✅ Auto-discovery {fecha}: stack={stack}, sin selectores configurados."
    return (
        f"        {mun!r}: MunicipioConfig("
        f"nombre={nombre_real!r}, estado_clave={estado!r}, "
        f"portal_predial_url={url!r}, "
        f"poblacion_aprox={poblacion}, validado=True, "
        f"notas={nota!r}),"
    )


def aplicar(hallazgos_path: Path, dry_run: bool = False) -> dict[str, Any]:
    """Aplica los hallazgos OK al catálogo. Devuelve stats."""
    hallazgos = json.loads(hallazgos_path.read_text())
    contenido = CATALOGO.read_text()

    aplicados = []
    falsos_positivos = []
    no_encontrados = []

    oks = [h for h in hallazgos if h.get("estado_validacion") == "ok"]
    print(f"Hallazgos OK en JSON: {len(oks)}")

    for h in oks:
        # Filtrar falsos positivos
        es_fp, razon = es_falso_positivo(h)
        if es_fp:
            falsos_positivos.append({"hallazgo": f"{h['estado']}/{h['mun']}", "razon": razon})
            continue

        estado, mun = h["estado"], h["mun"]

        # Buscar entry actual en catálogo
        pattern = rf"(\s*{re.escape(repr(mun))}: MunicipioConfig\([^)]*\),)"
        match = re.search(pattern, contenido)
        if not match:
            no_encontrados.append(f"{estado}/{mun}")
            continue

        actual = match.group(1)
        nombre_match = re.search(r"nombre=['\"]([^'\"]+)['\"]", actual)
        pob_match = re.search(r"poblacion_aprox=(\d+)", actual)
        if not (nombre_match and pob_match):
            no_encontrados.append(f"{estado}/{mun} (no se pudo parsear nombre/pob)")
            continue

        nombre = nombre_match.group(1)
        pob = int(pob_match.group(1))

        nueva = construir_entry_python(h, nombre, pob)
        contenido = contenido.replace(actual, "\n" + nueva)
        aplicados.append({"estado": estado, "mun": mun, "url": h["url_real"]})

    if not dry_run and aplicados:
        CATALOGO.write_text(contenido)

    return {
        "total_hallazgos_ok": len(oks),
        "aplicados": aplicados,
        "falsos_positivos": falsos_positivos,
        "no_encontrados_en_catalogo": no_encontrados,
        "dry_run": dry_run,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hallazgos_json", type=Path,
                        help="Path al JSON de hallazgos del discovery")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo reporta cambios, no modifica catálogo")
    parser.add_argument("--commit", action="store_true",
                        help="Auto-commitear cambios al git (requiere repo limpio)")
    args = parser.parse_args()

    if not args.hallazgos_json.exists():
        print(f"ERROR: {args.hallazgos_json} no existe")
        sys.exit(1)

    print(f"Aplicando hallazgos: {args.hallazgos_json}")
    print(f"Catálogo: {CATALOGO}")
    print(f"Modo: {'DRY-RUN' if args.dry_run else 'APLICAR'}")
    print()

    stats = aplicar(args.hallazgos_json, dry_run=args.dry_run)

    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Total hallazgos OK del JSON:         {stats['total_hallazgos_ok']}")
    print(f"Aplicados al catálogo:               {len(stats['aplicados'])}")
    print(f"Falsos positivos descartados:        {len(stats['falsos_positivos'])}")
    print(f"No encontrados en catálogo:          {len(stats['no_encontrados_en_catalogo'])}")
    print()

    if stats["aplicados"]:
        print("✓ Aplicados:")
        for a in stats["aplicados"]:
            print(f"  {a['estado']}/{a['mun']:30} → {a['url'][:60]}")
        print()

    if stats["falsos_positivos"]:
        print("✗ Falsos positivos:")
        for fp in stats["falsos_positivos"]:
            print(f"  {fp['hallazgo']:35} {fp['razon']}")
        print()

    if stats["no_encontrados_en_catalogo"]:
        print("⚠ No encontrados en catálogo (¿agregar manualmente?):")
        for n in stats["no_encontrados_en_catalogo"]:
            print(f"  {n}")
        print()

    if args.dry_run:
        print("(dry-run: catálogo NO modificado)")
        return

    if args.commit and stats["aplicados"]:
        print("Commiteando cambios...")
        result = subprocess.run(
            ["git", "add", str(CATALOGO)],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        if result.returncode == 0:
            msg = f"chore(catalogo): aplicar {len(stats['aplicados'])} hallazgos discovery {datetime.now().strftime('%Y-%m-%d')}"
            commit_result = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=REPO_ROOT, capture_output=True, text=True,
            )
            if commit_result.returncode == 0:
                print(f"✓ Commit OK: {msg}")
            else:
                print(f"⚠ git commit falló: {commit_result.stderr}")
        else:
            print(f"⚠ git add falló: {result.stderr}")


if __name__ == "__main__":
    main()
