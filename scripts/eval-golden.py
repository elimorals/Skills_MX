#!/usr/bin/env python3
"""Evals de salida deterministas: casos golden (evals/golden/*.golden.json) contra
los scripts de cálculo. No requiere API key ni red.

Cada caso corre `python3 <script> --json <args>` y compara:
  expect          {ruta: valor}   igualdad (floats con tolerancia 0.005)
  expect_contains {ruta: texto}   subcadena
  expect_len      {ruta: n}       longitud de lista
Ruta = claves/índices separados por punto: "impuestos_retenidos.1.importe".

Uso:
    python3 scripts/eval-golden.py                 # todos
    python3 scripts/eval-golden.py rfc-validacion  # un skill
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_MISSING = object()


def get(obj, ruta):
    for k in ruta.split("."):
        try:
            obj = obj[int(k)] if isinstance(obj, list) else obj[k]
        except (KeyError, IndexError, ValueError, TypeError):
            return _MISSING
    return obj


def iguales(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) < 0.005
    return a == b


def correr_caso(script, caso):
    proc = subprocess.run([sys.executable, str(ROOT / script), "--json", *caso["args"]],
                          capture_output=True, text=True, cwd=ROOT)
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return [f"salida no es JSON (rc={proc.returncode}): {proc.stderr.strip()[:200]}"]
    fallas = []
    for ruta, esperado in caso.get("expect", {}).items():
        real = get(out, ruta)
        if not iguales(real, esperado):
            fallas.append(f"{ruta}: esperado {esperado!r}, obtuvo {'<falta>' if real is _MISSING else repr(real)}")
    for ruta, texto in caso.get("expect_contains", {}).items():
        real = get(out, ruta)
        if not isinstance(real, str) or texto not in real:
            fallas.append(f"{ruta}: debía contener {texto!r}, obtuvo {'<falta>' if real is _MISSING else repr(real)}")
    for ruta, n in caso.get("expect_len", {}).items():
        real = get(out, ruta)
        if not isinstance(real, list) or len(real) != n:
            fallas.append(f"{ruta}: longitud esperada {n}, obtuvo {real!r}")
    return fallas


def main():
    filtro = sys.argv[1] if len(sys.argv) > 1 else None
    total = fallidos = 0
    for archivo in sorted((ROOT / "evals" / "golden").glob("*.golden.json")):
        suite = json.loads(archivo.read_text())
        if filtro and suite["skill"] != filtro:
            continue
        print(f"{suite['skill']}:")
        for caso in suite["cases"]:
            total += 1
            fallas = correr_caso(suite["script"], caso)
            if fallas:
                fallidos += 1
                print(f"  ✗ {caso['id']}  [{caso.get('fuente', '')}]")
                for f in fallas:
                    print(f"      {f}")
            else:
                print(f"  ✓ {caso['id']}")
    print(f"\n{total - fallidos}/{total} casos golden OK")
    sys.exit(1 if fallidos or total == 0 else 0)


if __name__ == "__main__":
    main()
