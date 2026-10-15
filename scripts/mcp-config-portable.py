#!/usr/bin/env python3
"""Reescribe los .mcp.json de los plugins y los example.mcp.json de cada MCP sin rutas locales.

Los MCPs propios (mp_*) se lanzan con uv desde el repo en GitHub, así funcionan igual en un
clon o en un plugin instalado desde el marketplace:

    uv run --no-project --quiet --with "plugins-mx-mcp-servers[extras] @ git+…#subdirectory=mcp-servers" \
        python -m mp_x.server

Uso: python3 scripts/mcp-config-portable.py [--check]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
REPO = "git+https://github.com/elimorals/Skills_MX@main#subdirectory=mcp-servers"
# Extras de pyproject que necesita cada MCP para su ruta real.
EXTRAS = {
    "mp_sat_ws": ["sat-ws"],
    "mp_sat_portal": ["sat-ws", "sat-portal"],
    "mp_sat_opinion_32d": ["sat-portal"],
    "mp_condusef_sipres": ["publicos-federales"],
    "mp_concilianet_profeco": ["publicos-federales-2"],
    "mp_retys_catalogo": ["publicos-federales-2"],
    "mp_portales_monitor": ["publicos-federales-2"],
    "mp_gas_natural_mx": ["estatal-resto"],
    "mp_predial_mx": ["estatal-centro"],
    "mp_edomex_municipal": ["estatal-centro"],
}
# Servidores externos: reemplazo por el paquete oficial o None para quitar (no existen).
EXTERNOS = {
    "@stripe/mcp-server": {"command": "npx", "args": ["-y", "@stripe/mcp", "--tools=all"],
                           "env": {"STRIPE_SECRET_KEY": "${STRIPE_SECRET_KEY:-}"}},
    "@google-analytics/mcp-server": {"command": "uvx", "args": ["analytics-mcp"],
                                     "env": {"GOOGLE_APPLICATION_CREDENTIALS": "${GOOGLE_APPLICATION_CREDENTIALS:-}",
                                             "GOOGLE_PROJECT_ID": "${GOOGLE_PROJECT_ID:-}"}},
    "@gupshup/mcp-whatsapp": None,
    "./mcp-servers/meta-ads.js": None,
    "./mcp-servers/google-ads.js": None,
    "./mcp-servers/tiktok-ads.js": None,
}
MOCK = re.compile(r"[^.]*\b(mock|Mock)[^.]*\.?\s*")


def lanzador(modulo: str) -> list[str]:
    paquete = modulo.split(".")[0]
    extras = EXTRAS.get(paquete)
    spec = f"plugins-mx-mcp-servers{'[' + ','.join(extras) + ']' if extras else ''} @ {REPO}"
    return ["run", "--no-project", "--quiet", "--with", spec, "python", "-m", modulo]


def limpiar_comentario(c: str) -> str:
    c = MOCK.sub(" ", c)
    c = re.sub(r"\s+", " ", re.sub(r"\.(?=[A-ZÁÉÍÓÚ¿])", ". ", c)).strip()
    return c or "Ver la sección 'Estado real' del README del MCP."


def a_formato_estandar(cfg: dict) -> dict:
    """Algunos example.mcp.json traían el servidor en la raíz y mcpServers vacío."""
    if cfg.get("mcpServers") or "command" not in cfg:
        return cfg
    nombre = cfg["name"].removeprefix("mp_")
    env = {k: v for k, v in (cfg.get("env") or {}).items() if k != "PLUGINS_MX_MOCK"}
    env["PLUGINS_MX_MOCK"] = "${PLUGINS_MX_MOCK:-}"
    return {"mcpServers": {nombre: {
        "_comment": f"{cfg.get('displayName', nombre)}. Estado y cobertura: README del MCP, sección 'Estado real'.",
        "command": cfg["command"], "args": cfg["args"], "env": env,
    }}}


def portar(cfg: dict) -> dict:
    cfg = a_formato_estandar(cfg)
    nuevos = {}
    for nombre, s in cfg.get("mcpServers", {}).items():
        args = s.get("args", [])
        if "-m" in args and args[args.index("-m") + 1].startswith("mp_"):
            modulo = args[args.index("-m") + 1]
            s = {k: v for k, v in s.items() if k not in ("cwd",)}
            s["command"], s["args"] = "uv", lanzador(modulo)
        else:
            clave = next((a for a in args if a in EXTERNOS), None)
            if clave is not None:
                if EXTERNOS[clave] is None:
                    continue
                s = {**{k: v for k, v in s.items() if k not in ("env",)}, **EXTERNOS[clave]}
        if "PLUGINS_MX_MOCK" in (s.get("env") or {}):
            # Nunca forzar mock desde la config: lo decide el usuario.
            s["env"] = {**s["env"], "PLUGINS_MX_MOCK": "${PLUGINS_MX_MOCK:-}"}
        if "_comment" in s:
            s["_comment"] = limpiar_comentario(s["_comment"])
        nuevos[nombre] = s
    out = {k: v for k, v in cfg.items() if k != "mcpServers"}
    if "_comment" in out:
        out["_comment"] = limpiar_comentario(out["_comment"])
    out["mcpServers"] = nuevos
    return out


def main() -> int:
    check = "--check" in sys.argv
    archivos = sorted(RAIZ.glob("*/.mcp.json")) + sorted(RAIZ.glob("mcp-servers/mp_*/example.mcp.json"))
    pendientes = []
    for f in archivos:
        actual = f.read_text()
        nuevo = json.dumps(portar(json.loads(actual)), ensure_ascii=False, indent=2) + "\n"
        if nuevo != actual:
            pendientes.append(str(f.relative_to(RAIZ)))
            if not check:
                f.write_text(nuevo)
    if check and pendientes:
        print("Configs MCP sin portar:", ", ".join(pendientes))
        return 1
    print(f"{len(archivos)} configs revisados, {len(pendientes)} {'pendientes' if check else 'actualizados'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
