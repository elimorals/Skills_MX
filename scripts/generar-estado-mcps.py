#!/usr/bin/env python3
"""Genera el estado real de los MCPs para website/ y los .md del repo.

Fuente de verdad: la sección "## Estado real" de cada mcp-servers/mp_*/README.md
(oleada 1, 2026-10-14). La categoría de cada MCP está transcrita a mano en
ESTADO (leer el README no se puede automatizar sin inventar); el script falla si
un MCP con sección "Estado real" no está clasificado o si uno sin sección lo está.
Las tools se leen de server.py (funciones decoradas con @mcp.tool).

Escribe:
  website/data/mcp-estado.json  (+ copia en website/api/)
  website/data/skills-catalog.json  (+ copia en website/api/)
  website/mcp-manifest.json  (servers + stats)
  website/data/isn-tasas.json  (+ copia en website/api/), desde shared/catalogo_isn_estatal.py
  website/data/municipios.json (+ copia en website/api/), desde shared/catalogo_municipios_mx.py
  website/data/portales-coverage.json (+ copia): 'validado' = estado real de los MCPs de cada dependencia
  bloques entre marcadores <!-- <nombre>:inicio --> / <!-- <nombre>:fin --> en
  mcp-servers/CATALOGO.md, README.md, website/index.html y las páginas de ISN

Uso:  python3 scripts/generar-estado-mcps.py           (escribe)
      python3 scripts/generar-estado-mcps.py --check   (falla si algo está desactualizado)
"""
from __future__ import annotations

import ast
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_DIR = ROOT / "mcp-servers"
WEB = ROOT / "website"
FECHA = "2026-10-14"

CATEGORIAS = {
    "real_validado": "Real, validado en vivo",
    "real_sin_validar": "Real sin validar (requiere credenciales)",
    "handoff": "Entrega a humano (CAPTCHA o login)",
    "sin_api": "Sin API pública",
    "calculo_normativo": "Cálculo normativo verificado",
    "bloqueado": "Bloqueado",
    "sin_verificar": "Sin verificar",
}

# Transcripción de "## Estado real" de cada README. Nota = resumen literal, sin adornos.
ESTADO: dict[str, tuple[str, str]] = {
    "mp_agua_mx": ("real_validado", "Parcial: JMAS Juárez real; SIAPA con reCAPTCHA; CESPT da 404; OOAPAS sin parser validado."),
    "mp_amazon_mx_seller": ("real_sin_validar", "Rutas SP-API verificadas (Orders, Listings, Fees); falta una app SP-API autorizada."),
    "mp_banxico_cep": ("real_validado", "Consulta de estado y 'no encontrado' validadas; descarga de un SPEI existente sin validar. Handoff si vuelve el CAPTCHA."),
    "mp_cabify_business": ("real_sin_validar", "Reescrito contra la API oficial v4 (estimates, journey, sales); falta sandbox. Sin listado de viajes ni CFDI."),
    "mp_catastro_estatal_mx": ("handoff", "IGECEM: handoff; IRCEP sin DNS; IRCNL y OVICA exigen login."),
    "mp_cdmx_municipal": ("handoff", "Predial (ALTCHA) y tenencia/multas (CAPTCHA de imagen): handoff. Hoy No Circula: cálculo local."),
    "mp_cfe_interconexion_solar": ("calculo_normativo", "Umbrales de la LSE (DOF 18-03-2025); sin tarifas ni folios inventados."),
    "mp_citas_monitor": ("handoff", "SAT exige sesión, SRE tiene Radware Captcha, IMSS sin DNS, INE informativo. No reserva citas."),
    "mp_clabe_validador_oficial": ("real_validado", "Catálogo SPEI de Banxico validado en vivo."),
    "mp_clip_terminal": ("real_sin_validar", "Reescrito contra developer.clip.mx (payments, refunds, devices, settlements); falta credencial de pruebas."),
    "mp_cnbv_fintech": ("real_validado", "Padrón PES de la CNBV validado; no publica RFC; sin fuente para modelos novedosos."),
    "mp_cofepris_aviso_funcionamiento": ("calculo_normativo", "Constantes de la LGS (reforma DOF 15-01-2026); giros por Acuerdo SSA sin cotejar."),
    "mp_conagua_repda": ("real_validado", "Consulta REPDA (ASP.NET, sin CAPTCHA) validada en vivo."),
    "mp_concilianet_profeco": ("real_validado", "PDFs de Concilianet y Buró Comercial validados en vivo."),
    "mp_condusef_sipres": ("real_validado", "SIPRES validado en vivo (requiere extra truststore por TLS incompleto)."),
    "mp_cre_hidrocarburos": ("real_validado", "XML público de precios/permisos (15,046 estaciones) validado en vivo."),
    "mp_curp_renapo": ("handoff", "gob.mx/curp con challenge Akamai y reCAPTCHA Enterprise; validación local de la CURP."),
    "mp_desconexion_digital": ("calculo_normativo", "LFT vigente: desconexión solo en teletrabajo (Art. 330-E); no existe la 'reforma Art. 132 marzo 2026'."),
    "mp_didi_food_partners": ("sin_api", "DiDi Food no publica API de comercios; con credenciales devuelve ConfigError."),
    "mp_didi_partners": ("sin_api", "DiDi no publica API para conductores; con credenciales devuelve ConfigError."),
    "mp_dof_api": ("real_validado", "API JSON de SIDOF validada; búsqueda por título recorriendo sumarios diarios."),
    "mp_donatarias_sat": ("real_validado", "Directorio XLSX del SAT validado (10,017 RFC); no incluye revocaciones posteriores al corte."),
    "mp_edomex_municipal": ("real_validado", "Parcial: predial Toluca real; tenencia y multas handoff; Ecatepec, Naucalpan e Izcalli fallan."),
    "mp_expediente_clinico_nom024": ("calculo_normativo", "NOM-024, NOM-004 y LGS verificadas; Reglamento de Insumos sin cotejar."),
    "mp_facturama_extendido": ("real_sin_validar", "Rutas verificadas contra el cliente de satcfdi; falta cuenta sandbox."),
    "mp_form_filler_public": ("handoff", "Ya no abre navegador ni envía formularios: devuelve URL, pasos y campos prellenados."),
    "mp_gas_natural_mx": ("real_validado", "Parcial: tarifas Ecogas (PDF) validadas; otros distribuidores sin fuente → upstream_error."),
    "mp_guadalajara_municipal": ("handoff", "Predial y adeudos vehiculares con reCAPTCHA."),
    "mp_impi_marcanet": ("real_validado", "MARCia (IMPI) validado en vivo, sin CAPTCHA ni login."),
    "mp_ine_verificacion": ("handoff", "Lista nominal con Cloudflare y reCAPTCHA v2; no se evade."),
    "mp_ish_mx": ("calculo_normativo", "Cálculo local; tasas 2026 contra fuentes secundarias (confianza media, varias en conflicto)."),
    "mp_isn_mx": ("calculo_normativo", "Cálculo local; tasas 2026 contra fuente secundaria."),
    "mp_klap": ("sin_api", "Sin documentación pública de API; con credenciales devuelve ConfigError."),
    "mp_kueski": ("sin_api", "API solo para comercios afiliados; con credenciales devuelve ConfigError."),
    "mp_ley_silla_nom037": ("calculo_normativo", "LFT (Ley Silla DOF 19-12-2024), NOM-035, NOM-037 y UMA 2026 verificadas."),
    "mp_llave_mx": ("real_sin_validar", "Login con CAPTCHA; el canje de token requiere convenio con la ATDT. Estadísticas de adopción leídas de datos.gob.mx."),
    "mp_llave_mx_tracker": ("real_validado", "Revisión de portadas de 20 portales validada en vivo; solo mira la portada."),
    "mp_lnetb_auditor": ("calculo_normativo", "Plazos de los transitorios de la LNETB (DOF 16-07-2025); se retiraron scores por estado sin fuente."),
    "mp_merida_municipal": ("handoff", "Predial detrás de Radware Bot Manager con hCaptcha."),
    "mp_monterrey_municipal": ("real_validado", "Predial (ASP.NET, sin CAPTCHA) validado con expediente inexistente; tabla de adeudo sin ver con caso real."),
    "mp_multas_mx": ("handoff", "CDMX, EdoMex, Jalisco y San Pedro con CAPTCHA; NL solo refrendo."),
    "mp_multas_vehiculares_mx": ("handoff", "CDMX, EdoMex, Jalisco y San Pedro con CAPTCHA; NL consulta manual."),
    "mp_no_antecedentes_penales_mx": ("handoff", "Sin verificador público consultable (CDMX); EdoMex sin DNS."),
    "mp_paypal_mx": ("real_sin_validar", "Cliente contra el OpenAPI oficial (transactions, balances); falta app REST con credenciales."),
    "mp_portales_monitor": ("real_validado", "Chequeo HTTP de 25 portales validado en vivo; los detrás de Akamai necesitan navegador con ventana."),
    "mp_predial_mx": ("real_validado", "Parcial: Toluca real; CDMX handoff (ALTCHA); resto del catálogo no revalidado en esta oleada."),
    "mp_puebla_municipal": ("handoff", "Predial con CAPTCHA."),
    "mp_queretaro_municipal": ("real_validado", "Endpoints JSON del portal validados con clave ficticia, sin CAPTCHA."),
    "mp_rappi_partners": ("real_sin_validar", "Cliente contra el dev-portal; credenciales solo para aliados aprobados. Ranking y comisiones: sin endpoint."),
    "mp_repep_profeco": ("handoff", "El portal tiene controles anti-automatización deliberados; no se emulan."),
    "mp_repse_stps": ("real_validado", "Búsqueda y padrón REPSE validados en vivo."),
    "mp_repuve": ("handoff", "reCAPTCHA v3 y body cifrado en el navegador; robo devuelve null (desconocido), nunca false."),
    "mp_resico_sat": ("calculo_normativo", "Cálculo local sobre tablas LISR; la tasa de retención de plataformas y el criterio 'SCJN 2026' están sin verificar."),
    "mp_retys_catalogo": ("real_validado", "Validado solo con Chromium con ventana (Akamai bloquea headless y httpx)."),
    "mp_sacpi_michoacan": ("bloqueado", "Host sacpi.michoacan.gob.mx sin DNS (NXDOMAIN); selectores de 2026-06 sin revalidar."),
    "mp_sat_opinion_32d": ("real_validado", "Consulta pública 32-D validada; descarga propia con e.firma sin validar."),
    "mp_sat_portal": ("real_validado", "Parcial: listas 69 y 69-B validadas; login e.firma (CSF, padrón, vigencia) sin validar con e.firma real; buzón y acuses no implementados."),
    "mp_sat_ws": ("real_sin_validar", "Firma y autenticación validadas con e.firma de prueba; solicitud/descarga con e.firma real sin validar."),
    "mp_sedatu_uso_suelo": ("handoff", "Sin consulta pública nacional de uso de suelo; devuelve pasos con permitido: null."),
    "mp_sep_profesional": ("handoff", "Cédula profesional exige token reCAPTCHA; resultado null (desconocido) con handoff."),
    "mp_simplifica_ciudadano": ("bloqueado", "No hay fuente pública del avance por estado; fuera de mock devuelve ConfigError."),
    "mp_tenencia_mx": ("calculo_normativo", "Cálculo local; montos 2026 de notas de prensa (confianza media o baja); se retiraron estados sin fuente."),
    "mp_tijuana_municipal": ("real_validado", "Consulta de vivienda asegurada validada en vivo, sin CAPTCHA."),
    "mp_trustly_mx": ("sin_api", "Trustly no opera en México; con credenciales devuelve ConfigError."),
    "mp_uber_eats_partners": ("sin_api", "La doc de la Marketplace API no es pública; con credenciales devuelve ConfigError."),
    "mp_verificacion_vehicular_mx": ("handoff", "Estatus CDMX con CAPTCHA; calendario y costos 2026 de notas de prensa."),
}

MARK_INI, MARK_FIN = "<!-- estado-mcps:inicio -->", "<!-- estado-mcps:fin -->"


def tiene_estado_real(mcp: str) -> bool:
    readme = MCP_DIR / mcp / "README.md"
    return readme.exists() and re.search(r"^## Estado real", readme.read_text(), re.M) is not None


def tools(mcp: str) -> list[str]:
    """Nombres de las funciones decoradas con @mcp.tool en server.py (respeta name=)."""
    tree = ast.parse((MCP_DIR / mcp / "server.py").read_text())
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            fn = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(fn, ast.Attribute) and fn.attr == "tool" and getattr(fn.value, "id", "") == "mcp":
                name = node.name
                if isinstance(dec, ast.Call):
                    for kw in dec.keywords:
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                            name = kw.value.value
                out.append(name)
    return out


def construir() -> list[dict]:
    mcps = sorted(p.name for p in MCP_DIR.glob("mp_*") if p.is_dir())
    filas = []
    errores = []
    for m in mcps:
        con_seccion = tiene_estado_real(m)
        if con_seccion and m not in ESTADO:
            errores.append(f"{m}: tiene 'Estado real' pero no está en ESTADO")
        if not con_seccion and m in ESTADO:
            errores.append(f"{m}: está en ESTADO pero su README no tiene 'Estado real'")
        cat, nota = ESTADO.get(m, ("sin_verificar", "El README no tiene sección 'Estado real' de la oleada 1."))
        filas.append({"id": m, "estado": cat, "estado_label": CATEGORIAS[cat], "nota": nota, "tools": tools(m)})
    extra = set(ESTADO) - set(mcps)
    errores += [f"{m}: en ESTADO pero no existe el directorio" for m in sorted(extra)]
    if errores:
        sys.exit("\n".join(errores))
    return filas


def conteos(filas):
    c = Counter(f["estado"] for f in filas)
    return {k: c.get(k, 0) for k in CATEGORIAS}


def bloque_md(filas, con_tabla: bool) -> str:
    c = conteos(filas)
    lineas = [MARK_INI, f"## Estado a {FECHA} (oleada 1: mock → real)", "",
              f"Generado por `scripts/generar-estado-mcps.py` desde la sección \"Estado real\" de cada README. "
              f"{len(filas)} MCPs, {sum(len(f['tools']) for f in filas)} tools.", "",
              "| Categoría | MCPs |", "|---|---|"]
    lineas += [f"| {CATEGORIAS[k]} | {v} |" for k, v in c.items()]
    if con_tabla:
        lineas += ["", "| MCP | Estado | Nota | Tools |", "|---|---|---|---|"]
        for f in filas:
            t = ", ".join(f"`{x}`" for x in f["tools"])
            lineas.append(f"| `{f['id']}` | {f['estado_label']} | {f['nota']} | {t} |")
    lineas.append(MARK_FIN)
    return "\n".join(lineas)


def bloque_lista(filas) -> str:
    """Lista compacta por estado (para llms.txt)."""
    lineas = [MARK_INI]
    for k, label in CATEGORIAS.items():
        ids = [f["id"] for f in filas if f["estado"] == k]
        if ids:
            lineas.append(f"- **{label} ({len(ids)}):** " + ", ".join(ids))
    lineas.append(MARK_FIN)
    return "\n".join(lineas)


def bloque_html(filas, catalogo) -> str:
    por_id = {f["id"]: f for f in filas}
    resumen = " · ".join(f"{html.escape(CATEGORIAS[k])}: {v}" for k, v in conteos(filas).items())
    h = [MARK_INI, f'<p class="cat-note">Estado al {FECHA}: {resumen}. Detalle por MCP en '
                   '<a href="/data/mcp-estado.json">/data/mcp-estado.json</a>.</p>']
    for n, cat in enumerate(catalogo["categorias"]):
        h += ['<div class="mcp-cat">', '  <div class="mcp-cat-head">',
              f'    <span class="cat-no">{chr(65 + n)}.</span>', f'    <h3>{html.escape(cat["label"])}</h3>',
              f'    <span class="cat-count">{len(cat["skills"])}</span>', '  </div>', '  <div class="mcp-list">']
        for s in cat["skills"]:
            f = por_id[s["id"]]
            h.append(f'    <span class="mcp-item" title="{html.escape(f["nota"])}">'
                     f'{f["id"]} · {html.escape(f["estado_label"])}</span>')
        h += ['  </div>', '</div>']
    h.append(MARK_FIN)
    return "\n".join(h)


def reemplazar_bloque(texto: str, bloque: str, nombre: str = "estado-mcps", path: Path | None = None) -> str:
    """Sustituye lo que hay entre <!-- nombre:inicio --> y <!-- nombre:fin --> (marcadores incluidos)."""
    ini, fin = f"<!-- {nombre}:inicio -->", f"<!-- {nombre}:fin -->"
    patron = re.compile(re.escape(ini) + r".*?" + re.escape(fin), re.S)
    if not patron.search(texto):
        sys.exit(f"{path}: faltan los marcadores {ini} / {fin}")
    return patron.sub(lambda _: bloque.replace(MARK_INI, ini).replace(MARK_FIN, fin), texto)


def bloque_stats(filas) -> str:
    c = conteos(filas)
    cajas = [
        (len(filas), "MCP servers", "Python + FastMCP. Estado de cada uno en su README."),
        (c["real_validado"], CATEGORIAS["real_validado"], f"Consultados contra la fuente oficial el {FECHA}; varios son parciales."),
        (c["real_sin_validar"], CATEGORIAS["real_sin_validar"], "Cliente escrito contra la API documentada; falta una cuenta o sandbox para probarlo."),
        (c["handoff"], CATEGORIAS["handoff"], "El portal exige CAPTCHA, login o tiene controles anti-bot: el MCP devuelve URL, pasos y datos prellenados."),
        (c["calculo_normativo"], "Cálculos normativos locales", "Constantes contra ley o NOM; algunos solo contra fuentes secundarias (lo dice su nota)."),
        (c["sin_api"] + c["bloqueado"] + c["sin_verificar"], "Sin API, bloqueados o sin verificar",
         f"{c['sin_api']} sin API pública, {c['bloqueado']} bloqueados, {c['sin_verificar']} sin sección \"Estado real\"."),
    ]
    h = [MARK_INI]
    for n, l, d in cajas:
        h += ['    <div class="bs">', f'      <span class="bs-n" data-target="{n}">{n}</span>',
              f'      <span class="bs-l">{html.escape(l)}</span>', f'      <span class="bs-d">{html.escape(d)}</span>', '    </div>']
    h.append(MARK_FIN)
    return "\n".join(h)


def isn_estados() -> list[dict]:
    sys.path.insert(0, str(MCP_DIR))
    from shared import catalogo_isn_estatal as isn  # noqa: E402
    return isn.listar_estados()


def fmt_tasa(e) -> str:
    r = e.get("tasa_rango")
    return f"{r[0]}%–{r[1]}% (no calculable)" if r else f"{e['tasa_pct']}%"


def bloques_isn(estados):
    orden = sorted(estados, key=lambda e: (-e["tasa_pct"], e["nombre"]))
    filas_tabla = [MARK_INI] + [
        f'      <tr><td>{html.escape(e["nombre"])}</td><td>{fmt_tasa(e)}</td><td>{e["dia_vencimiento"]}</td></tr>'
        for e in orden] + [MARK_FIN]
    distintos = [e for e in orden if e["tasa_pct"] != 3.0 or e.get("tasa_rango")]
    resto = len(estados) - len(distintos)
    hero = [MARK_INI] + [
        f'        <tr><td>{html.escape(e["nombre"])}</td><td>{fmt_tasa(e)}</td><td>día {e["dia_vencimiento"]}</td></tr>'
        for e in distintos] + [f'        <tr><td>Resto ({resto} estados)</td><td>3.0%</td><td>varía</td></tr>', MARK_FIN]
    grid = [MARK_INI] + [
        f'    <div class="cat-state"><span class="cat-state-n">{html.escape(e["nombre"])}</span>'
        f'<span class="cat-state-r">{fmt_tasa(e).replace(" (no calculable)", "*")}</span></div>'
        for e in orden] + [MARK_FIN]
    ejemplo = [MARK_INI]
    for clave in ("CDMX", "JAL", "BC", "SIN"):
        e = next(x for x in estados if x["clave"] == clave)
        monto = "no calculable (tramos 2026 sin verificar)" if e.get("tasa_rango") else f"$ {500_000 * e['tasa_pct'] / 100:,.2f}"
        ejemplo.append(f'<span class="c-cm"># {e["nombre"]:<22} {fmt_tasa(e).replace(" (no calculable)", ""):>9} → {monto}</span>')
    ejemplo.append(MARK_FIN)
    return {"isn-tabla": "\n".join(filas_tabla), "isn-hero": "\n".join(hero),
            "isn-grid": "\n".join(grid), "isn-ejemplo": "\n".join(ejemplo)}


def isn_json(estados, previo) -> dict:
    tasas = [e["tasa_pct"] for e in estados] + [x for e in estados if e.get("tasa_rango") for x in e["tasa_rango"]]
    return {
        "$schema": previo.get("$schema"), "version": FECHA, "vigencia": "2026", "license": previo.get("license"),
        "source": "mcp-servers/shared/catalogo_isn_estatal.py. Fuente base: BHR 'Contribuciones locales, cambios "
                  "relevantes 2026' (fuente secundaria, confianza media); algunas entidades citan su ley local.",
        "documentation": previo.get("documentation"), "glossary": previo.get("glossary"),
        "totalEstados": len(estados), "tasaMinima": min(tasas), "tasaMaxima": max(tasas),
        "estados": [{"codigo": e["clave"], "estado": e["nombre"], "tasa_pct": e["tasa_pct"],
                     "tasa_rango": e.get("tasa_rango"), "calculable": not e.get("tasa_rango"),
                     "vence_dia": e["dia_vencimiento"], "portal": e["portal_url"], "fuente": e["fuente_tasa"]}
                    for e in sorted(estados, key=lambda e: e["clave"])],
        "notas": ["Tasas con rango (Sinaloa, Tabasco): el MCP no calcula el monto porque los tramos o el criterio 2026 no están verificados.",
                  "El MCP solo calcula; no genera línea de captura ni descarga declaraciones (requieren la sesión del contribuyente)."],
    }


def main():
    check = "--check" in sys.argv
    filas = construir()
    por_id = {f["id"]: f for f in filas}
    c = conteos(filas)
    dump = lambda d: json.dumps(d, ensure_ascii=False, indent=2) + "\n"

    salidas: dict[Path, str] = {}
    estado = {"fecha": FECHA, "fuente": "Sección 'Estado real' de mcp-servers/mp_*/README.md",
              "categorias": CATEGORIAS, "conteos": c, "total_mcps": len(filas), "mcps": filas}
    salidas[WEB / "data/mcp-estado.json"] = salidas[WEB / "api/mcp-estado.json"] = dump(estado)

    cat_path = WEB / "data/skills-catalog.json"
    catalogo = json.loads(cat_path.read_text())
    nuevo_cat = {"version": "2.0.0", "generated_at": FECHA, "total_skills": len(filas),
                 "fuente_estado": estado["fuente"], "conteos_estado": c,
                 "categorias": [], "filtros": {"estado": list(CATEGORIAS)}, "agents": catalogo["agents"]}
    for cat in catalogo["categorias"]:
        cc = {k: cat[k] for k in ("id", "label", "icon", "color", "descripcion")}
        cc["skills"] = [{"id": s["id"], "estado": por_id[s["id"]]["estado"],
                         "estado_label": por_id[s["id"]]["estado_label"],
                         "desc": por_id[s["id"]]["nota"], "tools": por_id[s["id"]]["tools"]}
                        for s in cat["skills"]]
        nuevo_cat["categorias"].append(cc)
    salidas[cat_path] = salidas[WEB / "api/skills-catalog.json"] = dump(nuevo_cat)

    man_path = WEB / "mcp-manifest.json"
    man = json.loads(man_path.read_text())
    man["description"] = (f"{len(filas)} MCP servers para trámites y cumplimiento en México. Estado al {FECHA}: "
                          f"{c['real_validado']} reales validados en vivo, {c['real_sin_validar']} reales sin validar "
                          f"(requieren credenciales), {c['handoff']} entregan a humano por CAPTCHA o login, "
                          f"{c['calculo_normativo']} cálculos normativos, {c['sin_api']} sin API pública, "
                          f"{c['bloqueado']} bloqueados y {c['sin_verificar']} sin verificar. "
                          "Detalle por MCP en /data/mcp-estado.json.")
    man["servers"] = [{"id": f["id"], "estado": f["estado"], "tools": f["tools"]} for f in filas]
    man["stats"] = {"totalServers": len(filas), "totalTools": sum(len(f["tools"]) for f in filas),
                    "estadoFecha": FECHA, "porEstado": c}
    salidas[man_path] = dump(man)

    def con_bloques(path: Path, bloques: dict[str, str]) -> None:
        texto = salidas.get(path) or path.read_text()
        for nombre, bloque in bloques.items():
            texto = reemplazar_bloque(texto, bloque, nombre, path)
        salidas[path] = texto

    con_bloques(MCP_DIR / "CATALOGO.md", {"estado-mcps": bloque_md(filas, True)})
    con_bloques(ROOT / "README.md", {"estado-mcps": bloque_md(filas, False)})
    con_bloques(WEB / "index.html", {"estado-mcps": bloque_html(filas, nuevo_cat), "estado-stats": bloque_stats(filas)})
    con_bloques(WEB / "llms.txt", {"estado-mcps": bloque_lista(filas)})
    con_bloques(WEB / "llms-full.txt", {"estado-mcps": bloque_md(filas, True)})

    por_path = WEB / "data/portales-coverage.json"
    portales = json.loads(por_path.read_text())
    portales.update(version="2.0.0", generated_at=FECHA, nota=(
        "Endpoints y cobertura vienen del discovery de junio 2026. 'validado' ahora muestra el estado real "
        f"al {FECHA} de los MCPs que usan cada dependencia (ver /data/mcp-estado.json)."))
    portales.pop("municipios_validados_playwright", None)
    for dep in [d for e in portales["estados"] for d in e["dependencias"]] + portales["dependencias_federales"]:
        dep["validado"] = "Estado 2026-10-14 · " + " · ".join(
            f"{m}: {por_id[m]['estado_label']}" for m in dep["mcps"] if m in por_id)
    for p in portales["patrones_captcha"]:
        p.pop("patron_implementacion", None)
        if p["id"] != "ninguno":
            p["manejo"] = "Entrega a humano: los MCPs no resuelven ni evaden CAPTCHAs."
    salidas[por_path] = salidas[WEB / "api/portales-coverage.json"] = dump(portales)

    sys.path.insert(0, str(MCP_DIR))
    from shared import catalogo_municipios_mx as cm  # noqa: E402
    mun_path = WEB / "data/municipios.json"
    previo = json.loads(mun_path.read_text())
    municipios = [cm.get_municipio_config(e, m) for e in cm.listar_estados() for m in cm.listar_municipios_estado(e)]
    salidas[mun_path] = salidas[WEB / "api/municipios.json"] = dump({
        "$schema": previo.get("$schema"), "version": FECHA, "license": previo.get("license"),
        "source": "mcp-servers/shared/catalogo_municipios_mx.py (discovery 2026-06)",
        "documentation": previo.get("documentation"),
        "total": len(municipios),
        "con_portal_predial": sum(1 for m in municipios if m.portal_predial_url),
        "validados_discovery_2026_06": sum(1 for m in municipios if m.validado),
        "revalidados_2026_10_14": {"toluca": "real", "cdmx": "entrega a humano (ALTCHA)"},
        "notas": ["'validado' es del discovery de junio 2026 y no se revalidó en la oleada 1, salvo Toluca y CDMX.",
                  "SACPI Michoacán (sacpi.michoacan.gob.mx) no resuelve DNS al 2026-10-14."],
        "municipios": [{"estado": m.estado_clave, "municipio": m.nombre, "portal_predial": m.portal_predial_url,
                        "validado_discovery_2026_06": m.validado} for m in municipios],
    })

    estados_isn = isn_estados()
    b = bloques_isn(estados_isn)
    con_bloques(WEB / "productos/isn.html", {k: b[k] for k in ("isn-hero", "isn-grid", "isn-ejemplo")})
    con_bloques(WEB / "glosario/isn/index.html", {k: b[k] for k in ("isn-tabla", "isn-ejemplo")})
    isn_path = WEB / "data/isn-tasas.json"
    salidas[isn_path] = salidas[WEB / "api/isn-tasas.json"] = dump(isn_json(estados_isn, json.loads(isn_path.read_text())))

    viejos = [p for p, t in salidas.items() if not p.exists() or p.read_text() != t]
    if check:
        if viejos:
            sys.exit("Desactualizados: " + ", ".join(str(p.relative_to(ROOT)) for p in viejos))
        return
    for p in viejos:
        p.write_text(salidas[p])
    print(json.dumps(c, ensure_ascii=False), f"· {len(viejos)} archivos escritos")


if __name__ == "__main__":
    main()
