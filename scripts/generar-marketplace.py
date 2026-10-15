#!/usr/bin/env python3
"""Genera .claude-plugin/marketplace.json con todos los plugins del repo (lee cada plugin.json).

Uso: python3 scripts/generar-marketplace.py [--check]
Instalación: /plugin marketplace add elimorals/Skills_MX
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / ".claude-plugin" / "marketplace.json"


def construir() -> dict:
    plugins = []
    for pj in sorted(RAIZ.glob("*/.claude-plugin/plugin.json")):
        p = json.loads(pj.read_text())
        entrada = {
            "name": p["name"],
            "source": f"./{pj.parent.parent.name}",
            "description": p.get("description", ""),
            "version": p.get("version", "0.1.0"),
        }
        if p.get("keywords"):
            entrada["keywords"] = p["keywords"]
        plugins.append(entrada)
    # core-mexico primero: es la base de todos los verticales.
    plugins.sort(key=lambda e: (e["name"] != "core-mexico", e["name"]))
    return {
        "name": "plugins-mx",
        "owner": {"name": "Elías Rashid Morales Mendoza", "email": "elimoralsmendox@gmail.com"},
        "metadata": {
            "description": "Plugins de Claude Code, skills y MCP servers para operar una PyME o profesión en México.",
            "version": "0.3.0",
        },
        "plugins": plugins,
    }


def main() -> int:
    nuevo = json.dumps(construir(), ensure_ascii=False, indent=2) + "\n"
    if "--check" in sys.argv:
        if not DESTINO.exists() or DESTINO.read_text() != nuevo:
            print(f"{DESTINO.relative_to(RAIZ)} desactualizado: corre scripts/generar-marketplace.py")
            return 1
        return 0
    DESTINO.parent.mkdir(exist_ok=True)
    DESTINO.write_text(nuevo)
    print(f"{len(construir()['plugins'])} plugins en {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
