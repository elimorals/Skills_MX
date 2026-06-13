#!/usr/bin/env python3
"""Auto-descubrimiento de portales municipales de pago de predial en México.

Para cada municipio en una lista de input:
1. Intenta URLs comunes (patrones convencionales)
2. Si responde, navega al home con Playwright
3. Busca enlaces con texto "predial"/"tesorería"/"pago"
4. Sigue el link más prometedor
5. Inspecciona el form de pago: inputs, buttons, stack detection
6. Persiste hallazgos a JSON
7. Idempotente: si ya hay resultado para un municipio, lo skipea

USO:
    # Crear lista de municipios (formato simple JSON)
    cat > municipios.json << 'EOF'
    [
      {"estado": "jal", "mun": "guadalajara", "nombre": "Guadalajara"},
      {"estado": "nl", "mun": "monterrey", "nombre": "Monterrey"},
      ...
    ]
    EOF

    # Setup playwright (una vez)
    pip install playwright httpx
    playwright install chromium

    # Correr (puede tomar horas para 500+ municipios)
    python3 scripts/descubrir-portal-municipal.py \\
        --input municipios.json \\
        --output hallazgos.json \\
        --workers 5 \\
        --timeout 30

    # Reanudable: si se interrumpe, vuelve a correr — skipea ya completados
    python3 scripts/descubrir-portal-municipal.py --input municipios.json --output hallazgos.json

OUTPUT:
    hallazgos.json — array con un objeto por municipio:
    {
      "estado": "jal",
      "mun": "guadalajara",
      "url_real": "https://pagoenlinea.guadalajara.gob.mx/impuestopredial/",
      "stack_detectado": "angular_material",
      "selectores": {"input": [...], "submit": [...]},
      "inputs_visibles": [...],
      "buttons_visibles": [...],
      "estado_validacion": "ok" | "404" | "dns_dead" | "no_form" | "antibot",
      "ts": "2026-06-13T..."
    }

PATRONES URL PROBADOS (en orden):
1. https://pagos.{mun}.gob.mx/predial
2. https://predial.{mun}.gob.mx/
3. https://pagoenlinea.{mun}.gob.mx/predial
4. https://www.{mun}.gob.mx/predial
5. https://{mun}.gob.mx/predial/
6. https://recaudacion.{mun}.gob.mx/predial
7. https://catastro.{mun}.gob.mx/
8. Home www.{mun}.gob.mx → buscar link "predial"

STACK FINGERPRINTING:
- ASP.NET WebForms: input name `ctl00$...`, form action `.aspx`
- Angular Material: `mat-input-N` IDs, `mat-form-field` wrappers
- PHP: action `.php`, simple form
- ASP clásico: .asp extension, IIS server
- Wix/WordPress: generator meta, page builder elements
- IP+puerto: dominio = IPv4, URL con :PORT
- Anti-bot: title "Un momento…", body "verificación de seguridad"
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse


URL_PATTERNS = [
    "https://pagos.{mun}.gob.mx/predial",
    "https://predial.{mun}.gob.mx/",
    "https://pagoenlinea.{mun}.gob.mx/predial",
    "https://www.{mun}.gob.mx/predial",
    "https://{mun}.gob.mx/predial/",
    "https://recaudacion.{mun}.gob.mx/predial",
    "https://catastro.{mun}.gob.mx/",
    "https://tesoreria.{mun}.gob.mx/",
    "https://www.{mun}.gob.mx/",  # fallback: home
    "https://{mun}.gob.mx/",       # fallback sin www
]

# Patterns para alcaldías CDMX y casos especiales — se aplican si estado_clave='cdmx'
URL_PATTERNS_CDMX_ALCALDIAS = [
    "https://www.{mun}.cdmx.gob.mx/",
    "https://{mun}.cdmx.gob.mx/",
    "https://www.{mun_normalized}.gob.mx/",  # alguna como benitojuarez.gob.mx
]


STACK_FINGERPRINTS = {
    "asp_net_webforms": {
        "url_ext": [".aspx"],
        "input_name_prefix": ["ctl00$", "Content_Main$"],
        "form_action_ext": [".aspx"],
    },
    "angular_material": {
        "input_id_prefix": ["mat-input-"],
        "tag_present": ["mat-form-field", "mat-card"],
        "class_keywords": ["mat-mdc-", "mat-form-field"],
    },
    "php": {
        "url_ext": [".php"],
        "form_action_ext": [".php"],
    },
    "asp_classic": {
        "url_ext": [".asp"],
        "form_action_ext": [".asp"],
    },
    "ip_custom_port": {
        "url_regex": [r"://\d+\.\d+\.\d+\.\d+", r":\d{4,5}/"],
    },
    "anti_bot_radware": {
        "redirect_to": ["perfdrive.com", "botmanager"],
    },
    "anti_bot_cloudflare": {
        "title_contains": ["Un momento", "Just a moment", "Verificación de seguridad"],
        "body_contains": ["challenge-platform", "cf-browser-verification"],
    },
}


def detectar_stack(url: str, html: str, inputs: list, page_title: str) -> str:
    """Heurística de detección de stack."""
    import re
    url_lower = url.lower()

    # Anti-bots
    if any(x in (page_title or "") for x in ["Un momento", "Just a moment", "Verificación de seguridad"]):
        return "anti_bot_cloudflare"
    if "perfdrive.com" in url_lower or "botmanager" in url_lower:
        return "anti_bot_radware"

    # IP custom port
    if re.search(r"://\d+\.\d+\.\d+\.\d+", url) or re.search(r":\d{4,5}/", url):
        return "ip_custom_port"

    # By URL extension
    if ".aspx" in url_lower:
        return "asp_net_webforms"
    if url_lower.endswith(".asp") or "/.asp" in url_lower:
        return "asp_classic"
    if ".php" in url_lower:
        return "php"

    # By input attributes
    for inp in inputs:
        name = (inp.get("name") or "").lower()
        iid = (inp.get("id") or "").lower()
        if name.startswith("ctl00$") or "content_main" in iid:
            return "asp_net_webforms"
        if iid.startswith("mat-input-"):
            return "angular_material"

    return "unknown"


def probar_url_con_curl(url: str, timeout: int = 10) -> dict[str, Any]:
    """HEAD + GET rápido para descartar URLs muertas antes de Playwright."""
    import subprocess
    try:
        r = subprocess.run(
            ["curl", "-sIL", "--max-time", str(timeout), "-A",
             "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/130.0.0.0",
             url, "-o", "/dev/null", "-w", "%{http_code}|%{url_effective}"],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        out = r.stdout.strip()
        if not out or "|" not in out:
            return {"alive": False, "status": 0, "final_url": None}
        status_str, final = out.split("|", 1)
        status = int(status_str) if status_str.isdigit() else 0
        return {"alive": status == 200, "status": status, "final_url": final or url}
    except Exception:
        return {"alive": False, "status": 0, "final_url": None}


def inspect_with_playwright(url: str, headless: bool = True, timeout_ms: int = 20000) -> dict[str, Any]:
    """Carga URL con Playwright, captura DOM, retorna estructura."""
    from playwright.sync_api import sync_playwright

    result: dict[str, Any] = {
        "url_final": None,
        "title": None,
        "inputs": [],
        "buttons": [],
        "links_pago_internos": [],
        "forms_count": 0,
        "error": None,
    }

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                locale="es-MX",
                viewport={"width": 1366, "height": 768},
            )
            context.set_default_timeout(timeout_ms)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(3500)  # esperar JS extra (Angular Material necesita hidratación)

            result["url_final"] = page.url
            result["title"] = page.title()

            extracted = page.evaluate("""() => {
                // Capturamos inputs con su contexto (form padre) para distinguir
                // form de búsqueda del sitio vs form de consulta predial
                const inputs = Array.from(document.querySelectorAll("input")).filter(i => ["text","search","number","tel",""].includes(i.type)).map(i => {
                    const form = i.closest("form");
                    const formAction = form ? (form.action || "") : "";
                    const formId = form ? (form.id || "") : "";
                    // Buscar label asociado: <label for=id>, mat-label, label padre
                    let labelText = "";
                    if (i.id) {
                        const lblFor = document.querySelector(`label[for='${i.id}']`);
                        if (lblFor) labelText = lblFor.textContent.trim();
                    }
                    if (!labelText) {
                        const parentLabel = i.closest("label");
                        if (parentLabel) labelText = parentLabel.textContent.trim();
                    }
                    if (!labelText) {
                        // Material: mat-form-field > mat-label
                        const matForm = i.closest("mat-form-field");
                        if (matForm) {
                            const matLabel = matForm.querySelector("mat-label, label");
                            if (matLabel) labelText = matLabel.textContent.trim();
                        }
                    }
                    return {
                        name: i.name || "", id: i.id || "", type: i.type || "text",
                        placeholder: i.placeholder || "",
                        aria: i.getAttribute("aria-label") || "",
                        label: labelText.slice(0, 60),
                        visible: !!(i.offsetWidth && i.offsetHeight),
                        form_action: formAction,
                        form_id: formId,
                    };
                }).slice(0, 15);

                // Para cada botón, capturamos también su form padre y si está
                // dentro de un <header>, <nav> o aside (descartables)
                const buttons = Array.from(document.querySelectorAll("button, input[type='submit'], input[type='button']")).map(b => {
                    const form = b.closest("form");
                    const inHeader = !!b.closest("header, nav, [role='navigation'], [role='banner']");
                    return {
                        tag: b.tagName,
                        text: (b.textContent||b.value||"").trim().slice(0,60),
                        type: b.type||"",
                        form_id: form ? (form.id || "") : "",
                        form_action: form ? (form.action || "") : "",
                        in_navigation: inHeader,
                    };
                }).filter(b => b.text.length>0).slice(0, 15);

                const links_pago = [];
                document.querySelectorAll("a").forEach(a => {
                    const txt = (a.textContent||"").trim().toLowerCase();
                    const href = a.href || "";
                    if ((txt.includes("predial")||txt.includes("tesoreria")||txt.includes("pago"))
                        && href.startsWith("http") && !href.includes("#")) {
                        links_pago.push({texto: a.textContent.trim().slice(0,80), href});
                    }
                });

                return {
                    inputs, buttons, links_pago: links_pago.slice(0, 10),
                    forms_count: document.querySelectorAll("form").length,
                };
            }""")
            result.update(extracted)

            browser.close()
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)[:200]}"

    return result


def descubrir_municipio(municipio: dict) -> dict:
    """Pipeline completo de descubrimiento para un municipio."""
    estado = municipio["estado"]
    mun = municipio["mun"]
    nombre = municipio.get("nombre", mun.replace("_", " ").title())

    hallazgo = {
        "estado": estado,
        "mun": mun,
        "nombre": nombre,
        "url_real": None,
        "stack_detectado": None,
        "selectores": None,
        "inputs_visibles": [],
        "buttons_visibles": [],
        "estado_validacion": "no_intentado",
        "urls_probadas": [],
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    # Paso 1: probar URLs comunes con curl primero (rápido)
    candidatas_vivas = []
    mun_norm = mun.replace("_", "")

    # Patterns base
    patterns = list(URL_PATTERNS)
    # Patterns extra para alcaldías CDMX
    if estado == "cdmx":
        patterns = [p.replace("{mun_normalized}", mun_norm) for p in URL_PATTERNS_CDMX_ALCALDIAS] + patterns

    for pattern in patterns:
        url = pattern.replace("{mun}", mun_norm).replace("{mun_normalized}", mun_norm)
        check = probar_url_con_curl(url, timeout=8)
        hallazgo["urls_probadas"].append({"url": url, "status": check["status"]})
        if check["alive"]:
            candidatas_vivas.append((url, check["final_url"]))
        if len(candidatas_vivas) >= 3:
            break  # tres candidatas son suficientes

    if not candidatas_vivas:
        hallazgo["estado_validacion"] = "todas_urls_muertas"
        return hallazgo

    # Paso 2: Playwright sobre la primera viva
    url_inicial, url_final_curl = candidatas_vivas[0]
    inspect = inspect_with_playwright(url_inicial)

    if inspect["error"]:
        hallazgo["estado_validacion"] = "playwright_error"
        hallazgo["error"] = inspect["error"]
        return hallazgo

    # Helper: distinguir input de búsqueda genérico vs form de predial real
    def es_input_predial(inp: dict) -> bool:
        if not inp.get("visible"):
            return False
        nombre_inp = (inp.get("name") or "").lower()
        id_inp = (inp.get("id") or "").lower()
        aria = (inp.get("aria") or "").lower()
        placeholder = (inp.get("placeholder") or "").lower()
        label_text = (inp.get("label") or "").lower()
        form_id = (inp.get("form_id") or "").lower()
        form_action = (inp.get("form_action") or "").lower()

        # Descartar buscadores del sitio
        if nombre_inp in ("s", "q", "search", "keys", "edit-keys", "buscar", "searchword", "search_word", "searchterm"):
            return False
        if "search" in form_id or "search" in form_action or "buscador" in form_id:
            return False
        if "buscar" in placeholder and "predial" not in placeholder and "cuenta" not in placeholder:
            return False
        # Descartar forms de login del CMS (WordPress wp-login, Joomla modlgn-, etc.)
        if nombre_inp in ("username", "user", "password", "pass", "passwd", "email", "login"):
            return False
        if id_inp.startswith("modlgn-") or id_inp.startswith("user_login") or id_inp.startswith("wp-"):
            return False
        if "login" in form_action or "wp-login" in form_action or "session" in form_action:
            return False
        # Descartar inputs de captcha/recaptcha (sin contenido útil)
        if nombre_inp in ("g-recaptcha-response", "h-captcha-response", "captcha", "captcha_code"):
            return False
        # Descartar newsletter/subscribe (forms del footer)
        if "subscribe" in form_id or "newsletter" in form_id or "boletin" in form_id:
            return False

        # Señales positivas de predial — incluyendo label (mat-label, etc.)
        keywords_predial = ("cuenta", "predial", "expediente", "clave", "catastr", "claveCatastral", "ctapre", "cuentapredial")
        for kw in keywords_predial:
            if kw in nombre_inp or kw in id_inp or kw in aria or kw in placeholder or kw in label_text:
                return True
        # Si está en form con action a .aspx/.php es buen indicio
        if form_action.endswith(".aspx") or form_action.endswith(".php"):
            return True
        # Angular Material con id mat-input-N + label que pide cuenta
        if id_inp.startswith("mat-input-") and ("cuenta" in label_text or "predial" in label_text or "clave" in label_text):
            return True
        return False

    def es_submit_predial(btn: dict, main_input_form_id: str = "") -> bool:
        if btn.get("in_navigation"):
            return False  # botones del header/nav descartados
        texto = btn.get("text", "").lower()
        # Texto negativo (header/footer): "gobierno", "menú", "inicio", "buscar" sin cuenta
        if texto in ("gobierno", "menú", "menu", "inicio", "home", "transparencia", "search"):
            return False
        if "cerrar" in texto or "×" == texto.strip():
            return False
        # Texto positivo
        keywords_submit = ("consultar", "aceptar", "ingresar", "iniciar", "ver adeudo", "buscar adeudo", "consultar adeudo", "pagar")
        for kw in keywords_submit:
            if kw in texto:
                return True
        # Mismo form que el input principal
        if main_input_form_id and btn.get("form_id") == main_input_form_id:
            return True
        # type=submit ambiguo: solo aceptar si NO está en navegación
        if btn.get("type") == "submit" and not btn.get("in_navigation"):
            return texto in ("aceptar", "consultar", "buscar")
        return False

    # Si hay links_pago, seguir el más prometedor (probable que sea el portal real)
    links_pago = inspect.get("links_pago", [])
    url_final = inspect["url_final"]
    inputs = inspect["inputs"]
    buttons = inspect.get("buttons", [])

    has_form_real = any(es_input_predial(i) for i in inputs)

    # Si la URL inicial NO tiene form predial, intentar seguir un link de predial
    if not has_form_real and links_pago:
        # Preferir link cuyo texto exacto contenga "predial" o "pagar predial"
        link_predial = None
        for l in links_pago:
            if "predial" in l["texto"].lower():
                link_predial = l["href"]
                break
        if link_predial and link_predial != url_final:
            inspect2 = inspect_with_playwright(link_predial)
            if not inspect2.get("error"):
                inspect = inspect2
                url_final = inspect2["url_final"]
                inputs = inspect2["inputs"]
                buttons = inspect2.get("buttons", [])
                has_form_real = any(es_input_predial(i) for i in inputs)

    # Resultado
    hallazgo["url_real"] = url_final
    hallazgo["title"] = inspect.get("title")
    hallazgo["inputs_visibles"] = [i for i in inputs if i.get("visible")]
    hallazgo["buttons_visibles"] = [b for b in buttons if b.get("text") and not b.get("in_navigation")]
    hallazgo["forms_count"] = inspect.get("forms_count", 0)

    # Detectar redirect anti-bot Radware/Cloudflare
    if "perfdrive.com" in (url_final or "") or "botmanager" in (url_final or ""):
        hallazgo["estado_validacion"] = "anti_bot_radware"
        hallazgo["stack_detectado"] = "anti_bot_radware"
        return hallazgo
    title_low = (inspect.get("title") or "").lower()
    if any(kw in title_low for kw in ["un momento", "just a moment", "verificación de seguridad", "checking your browser"]):
        hallazgo["estado_validacion"] = "anti_bot_cloudflare"
        hallazgo["stack_detectado"] = "anti_bot_cloudflare"
        return hallazgo

    if has_form_real:
        hallazgo["estado_validacion"] = "ok"
        # Buscar el input que mejor matchea predial
        main_input = next((i for i in inputs if es_input_predial(i)), None)
        if main_input:
            sel_in = []
            if main_input.get("name"):
                sel_in.append(f"input[name='{main_input['name']}']")
            if main_input.get("id") and not main_input["id"].startswith("mat-input-"):
                # mat-input-N es dinámico, no es buen selector
                sel_in.append(f"input#{main_input['id']}")
            elif main_input.get("id", "").startswith("mat-input-"):
                # Para Angular Material, usar aria-label si existe
                if main_input.get("aria"):
                    sel_in.append(f"input[aria-label='{main_input['aria']}']")
                # Fallback a mat-form-field con texto del label
                sel_in.append("mat-form-field input[id^='mat-input']")

            # Submit: descartar nav, preferir mismo form que input
            main_form_id = main_input.get("form_id") or ""
            submit_btn = next((b for b in buttons if es_submit_predial(b, main_form_id)), None)
            sel_submit = []
            if submit_btn:
                if submit_btn["text"] and len(submit_btn["text"]) < 40:
                    sel_submit.append(f"button:has-text('{submit_btn['text']}')")
                if submit_btn.get("type") == "submit":
                    sel_submit.append("input[type='submit']")
            hallazgo["selectores"] = {
                "input": sel_in,
                "submit": sel_submit,
                "result": "table, .resultado, .adeudos",
            }
            hallazgo["main_input_form_action"] = main_input.get("form_action", "")
    else:
        hallazgo["estado_validacion"] = "no_form_detectado"

    hallazgo["stack_detectado"] = detectar_stack(url_final, "", inputs, inspect.get("title", ""))

    return hallazgo


def main():
    parser = argparse.ArgumentParser(description="Auto-descubrimiento portales municipales MX")
    parser.add_argument("--input", required=True, help="JSON con lista de municipios")
    parser.add_argument("--output", default="hallazgos-portales.json", help="JSON de salida")
    parser.add_argument("--workers", type=int, default=3, help="Procesos paralelos (Playwright es pesado)")
    parser.add_argument("--limit", type=int, default=0, help="Solo procesar N municipios (0=todos)")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip municipios ya en output")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    municipios = json.loads(input_path.read_text())
    if args.limit > 0:
        municipios = municipios[:args.limit]

    # Cargar existentes para reanudar
    existentes = {}
    if output_path.exists() and args.skip_existing:
        prev = json.loads(output_path.read_text())
        existentes = {(h["estado"], h["mun"]): h for h in prev if h.get("estado_validacion") == "ok"}
        print(f"Reanudando: {len(existentes)} ya validados, skipeando...")

    pendientes = [m for m in municipios if (m["estado"], m["mun"]) not in existentes]
    print(f"Total: {len(municipios)} municipios. Pendientes: {len(pendientes)}. Workers: {args.workers}")

    todos_hallazgos = list(existentes.values())

    # Procesar en paralelo
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(descubrir_municipio, m): m for m in pendientes}
        for i, fut in enumerate(as_completed(futures), 1):
            try:
                h = fut.result(timeout=180)
                todos_hallazgos.append(h)
                status_emoji = {"ok": "✅", "no_form_detectado": "⚠️", "todas_urls_muertas": "❌", "playwright_error": "💥", "anti_bot_cloudflare": "🛡️", "anti_bot_radware": "🛡️"}.get(h["estado_validacion"], "❓")
                print(f"  [{i}/{len(pendientes)}] {status_emoji} {h['estado']}/{h['mun']:30} → {h['estado_validacion']}", flush=True)
            except Exception as e:
                m = futures[fut]
                print(f"  [{i}/{len(pendientes)}] 💥 {m['estado']}/{m['mun']}: {e}", flush=True)
                todos_hallazgos.append({**m, "estado_validacion": "exception", "error": str(e)[:200]})

            # Persistir cada 10 para no perder progreso
            if i % 10 == 0:
                output_path.write_text(json.dumps(todos_hallazgos, indent=2, ensure_ascii=False))

    # Persistir final
    output_path.write_text(json.dumps(todos_hallazgos, indent=2, ensure_ascii=False))

    # Stats
    estados_count: dict[str, int] = {}
    for h in todos_hallazgos:
        e = h["estado_validacion"]
        estados_count[e] = estados_count.get(e, 0) + 1

    print(f"\n{'='*60}")
    print("RESUMEN")
    print('='*60)
    for estado, count in sorted(estados_count.items(), key=lambda x: -x[1]):
        print(f"  {estado:30}: {count}")
    print(f"\nReporte: {output_path}")


if __name__ == "__main__":
    main()
