#!/usr/bin/env python3
"""Health-check de portales municipales/estatales.

CORRE ESTE SCRIPT TÚ (yo no tengo navegador local) y comparte el JSON de salida
para que iteremos sobre los selectores que fallen.

Uso:
    cd mcp-servers
    python3 ../scripts/health-check-portales.py
    python3 ../scripts/health-check-portales.py --solo cdmx,nl,jal
    python3 ../scripts/health-check-portales.py --output health-report.json
    python3 ../scripts/health-check-portales.py --visible  # navegador no-headless para ver

Setup previo (una vez):
    pip install playwright
    playwright install chromium

El script:
1. Para cada municipio en el catálogo, abre Chromium
2. Carga la URL del portal predial
3. Intenta encontrar el input principal con los selectores configurados
4. Reporta: cargó OK? input encontrado? cuál selector fue el ganador?
5. Genera reporte JSON con stats globales + detalle por portal

Output incluye:
- Portales que cargan (URL viva) vs caídos
- Cuál selector matcheó del array (para refinar prioridades)
- Sugerencias de selectores nuevos basado en HTML observado
- Tiempo de respuesta por portal

NO llena formularios ni envía requests — solo valida que la página exista y
tenga la estructura esperada. Ningún identificador real es enviado.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Agregar mcp-servers al path
_SCRIPT_DIR = Path(__file__).resolve().parent
_MCP_SERVERS = _SCRIPT_DIR.parent / "mcp-servers"
sys.path.insert(0, str(_MCP_SERVERS))

try:
    from shared.catalogo_municipios_mx import (  # type: ignore
        ESTADOS,
        MUNICIPIOS,
        estadisticas,
    )
except ImportError as e:
    print(f"ERROR: No se pudo importar catálogo. ¿Estás en el repo correcto?\n{e}")
    sys.exit(1)


def check_portal(
    page: Any,
    url: str,
    input_selectors: list[str],
    submit_selectors: list[str],
    timeout_ms: int = 15000,
) -> dict[str, Any]:
    """Verifica un portal. Reporta status detallado."""
    start = time.time()
    result: dict[str, Any] = {
        "url": url,
        "load_ok": False,
        "input_encontrado": False,
        "input_selector_ganador": None,
        "submit_encontrado": False,
        "submit_selector_ganador": None,
        "tiempo_carga_ms": None,
        "error": None,
        "title": None,
        "sugerencias": [],
    }

    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        result["load_ok"] = response.ok if response else False
        result["status_code"] = response.status if response else None
        result["title"] = page.title()
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        result["tiempo_carga_ms"] = int((time.time() - start) * 1000)
        return result

    result["tiempo_carga_ms"] = int((time.time() - start) * 1000)

    if not result["load_ok"]:
        return result

    # Probar input selectors
    for sel in input_selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                result["input_encontrado"] = True
                result["input_selector_ganador"] = sel
                break
        except Exception:
            continue

    # Probar submit selectors
    for sel in submit_selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                result["submit_encontrado"] = True
                result["submit_selector_ganador"] = sel
                break
        except Exception:
            continue

    # Si no se encontró input, sugerir desde HTML
    if not result["input_encontrado"]:
        try:
            all_inputs = page.locator("input").all()
            sugerencias = []
            for inp in all_inputs[:10]:
                name = inp.get_attribute("name") or ""
                tipo = inp.get_attribute("type") or "text"
                id_ = inp.get_attribute("id") or ""
                if tipo in ("text", "search", "number"):
                    sugerencias.append({
                        "selector": f"input[name='{name}']" if name else f"input#{id_}" if id_ else "input[type='text']",
                        "name": name,
                        "type": tipo,
                        "id": id_,
                    })
            result["sugerencias"] = sugerencias[:5]
        except Exception:
            pass

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solo", help="Filtra estados (comma-separated): --solo cdmx,nl,jal")
    parser.add_argument("--output", default="health-check-portales-report.json")
    parser.add_argument("--visible", action="store_true", help="Modo no-headless (ver browser)")
    parser.add_argument("--timeout", type=int, default=15000)
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: pip install playwright && playwright install chromium")
        sys.exit(1)

    estados_filtro = (
        set(args.solo.split(",")) if args.solo else set(ESTADOS.keys())
    )

    stats_iniciales = estadisticas()
    print(f"Health-check de portales — {stats_iniciales['estados_cubiertos']} estados, "
          f"{stats_iniciales['municipios_totales']} municipios")
    print(f"Filtro: {len(estados_filtro)} estados a verificar\n")

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "estados_evaluados": list(estados_filtro),
        "stats_iniciales": stats_iniciales,
        "resultados": {},
        "resumen": {
            "portales_evaluados": 0,
            "portales_cargan": 0,
            "portales_con_input": 0,
            "portales_con_submit": 0,
            "portales_fallidos": 0,
            "candidatos_validacion_manual": [],
        },
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=not args.visible,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            ),
            locale="es-MX",
            viewport={"width": 1366, "height": 768},
        )
        page = context.new_page()

        for estado_clave, muns in MUNICIPIOS.items():
            if estado_clave not in estados_filtro:
                continue

            report["resultados"][estado_clave] = {}

            for mun_clave, mun_cfg in muns.items():
                print(f"  [{estado_clave}/{mun_clave}] {mun_cfg.nombre}...", flush=True)
                resultado_mun = {}

                # Test PREDIAL
                predial_cfg = mun_cfg.to_predial_config()
                if predial_cfg:
                    res = check_portal(
                        page,
                        predial_cfg.url,
                        predial_cfg.input_selectors,
                        predial_cfg.submit_selectors,
                        timeout_ms=args.timeout,
                    )
                    resultado_mun["predial"] = res
                    report["resumen"]["portales_evaluados"] += 1
                    if res["load_ok"]:
                        report["resumen"]["portales_cargan"] += 1
                    else:
                        report["resumen"]["portales_fallidos"] += 1
                    if res["input_encontrado"]:
                        report["resumen"]["portales_con_input"] += 1
                    if res["submit_encontrado"]:
                        report["resumen"]["portales_con_submit"] += 1

                    if res["load_ok"] and not res["input_encontrado"]:
                        report["resumen"]["candidatos_validacion_manual"].append({
                            "estado": estado_clave,
                            "municipio": mun_clave,
                            "tipo": "predial",
                            "url": predial_cfg.url,
                            "sugerencias": res.get("sugerencias", []),
                        })

                # Test MULTAS
                multas_cfg = mun_cfg.to_multas_config()
                if multas_cfg:
                    res = check_portal(
                        page,
                        multas_cfg.url,
                        multas_cfg.input_selectors,
                        multas_cfg.submit_selectors,
                        timeout_ms=args.timeout,
                    )
                    resultado_mun["multas"] = res
                    report["resumen"]["portales_evaluados"] += 1
                    if res["load_ok"]:
                        report["resumen"]["portales_cargan"] += 1
                    else:
                        report["resumen"]["portales_fallidos"] += 1
                    if res["input_encontrado"]:
                        report["resumen"]["portales_con_input"] += 1
                    if res["submit_encontrado"]:
                        report["resumen"]["portales_con_submit"] += 1

                report["resultados"][estado_clave][mun_clave] = resultado_mun

                # Pequeña pausa para no parecer bot agresivo
                time.sleep(1)

        browser.close()

    # Escribir reporte
    out_path = Path(args.output)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Portales evaluados:       {report['resumen']['portales_evaluados']}")
    print(f"Portales que cargan:      {report['resumen']['portales_cargan']}")
    print(f"Con input encontrado:     {report['resumen']['portales_con_input']}")
    print(f"Con submit encontrado:    {report['resumen']['portales_con_submit']}")
    print(f"Fallidos (404, timeout):  {report['resumen']['portales_fallidos']}")
    print(f"Necesitan validar input:  {len(report['resumen']['candidatos_validacion_manual'])}")
    print(f"\nReporte completo en: {out_path}")
    print("\nCompártelo conmigo para iterar selectores que fallen.")


if __name__ == "__main__":
    main()
