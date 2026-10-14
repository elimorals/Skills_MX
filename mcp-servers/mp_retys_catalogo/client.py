"""Cliente mp_retys_catalogo — Catálogo Nacional de Regulaciones (CONAMER).

Verificado 2026-10-14 en https://www.catalogonacional.gob.mx/:
- El buscador público ya solo expone **Inspecciones, Inspectores y Regulaciones**; los
  trámites no aparecen en sus resultados.
- Está detrás de Akamai: httpx y Chromium headless reciben 403; Chromium con ventana
  (MP_PLAYWRIGHT_HEADLESS=0) pasa. Por eso la búsqueda en vivo usa Playwright.
- Los resultados salen de `GET /Buscador/SearchRegulacionResult` y
  `/Buscador/SearchInspeccionResult` (fragmentos HTML). Algunos términos hacen fallar la
  consulta de regulaciones del lado del servidor (Postgres 42601) → se reporta como error
  de esa sección, no se oculta.
- Los 27 "Temas de interés" de la portada coinciden con SECTORES_CONAMER.

El catálogo curado de trámites (homoclaves no verificadas) solo se sirve con
PLUGINS_MX_MOCK=1.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.bitacora import Bitacora  # noqa: E402
from shared.errors import ConfigError, UpstreamError, ValidationError  # noqa: E402
from shared.mock import is_mock_mode, mark_simulated  # noqa: E402

import html as html_lib  # noqa: E402
import re  # noqa: E402
from urllib.parse import quote  # noqa: E402


NAMESPACE = "retys_catalogo"
URL_CONAMER = "https://www.catalogonacional.gob.mx/"
URL_DATOS_GOBMX = "https://www.datos.gob.mx/"

# 27 "Temas de interés" de la portada del Catálogo Nacional (verificados 2026-10-14)
SECTORES_CONAMER: dict[str, str] = {
    "hacienda_finanzas": "Hacienda y Finanzas Públicas",
    "comunicaciones_transporte": "Comunicaciones, Transporte y Movilidad",
    "energia": "Energía",
    "salud_deporte": "Salud y Deporte",
    "medio_ambiente": "Medio Ambiente, Recursos Naturales y Pesca",
    "desarrollo_economico": "Desarrollo económico",
    "no_sectorizado": "No sectorizado",
    "agricultura": "Agricultura, Ganadería y Desarrollo rural",
    "ciencia_educacion": "Ciencia y Educación",
    "gobernacion": "Gobernación",
    "relaciones_exteriores": "Relaciones Exteriores",
    "marina": "Marina",
    "cultura_recreacion": "Cultura y Recreación",
    "desarrollo_social": "Desarrollo Social",
    "sedatu": "Desarrollo Agrario, Territorial y Urbano",
    "trabajo_prevision": "Trabajo y Previsión Social",
    "turismo": "Turismo",
    "funcion_publica": "Función Pública y Contraloría",
    "seguridad_justicia": "Seguridad, Legalidad y Justicia",
    "proteccion_civil": "Protección Civil",
    "igualdad_sustantiva": "Igualdad Sustantiva",
    "ayuntamiento": "Ayuntamiento",
    "agua": "Agua",
    "desarrollo_sustentable": "Desarrollo Sustentable",
    "construccion": "Construcción",
    "sector_electoral": "Sector Electoral",
    "transformacion_digital": "Transformación Digital",
}

# Catálogo curado SOLO para PLUGINS_MX_MOCK=1: varias homoclaves no son oficiales
# (p. ej. "RENAPO-CURP", "INE-CV") y no se verificaron contra CONAMER.
TRAMITES_DEMANDA_ALTA: list[dict[str, Any]] = [
    {"homoclave": "SAT-04-022", "nombre": "Constancia de Situación Fiscal",
     "dependencia": "SAT", "sector": "hacienda_finanzas",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.sat.gob.mx/portal/public/tramites/constancia-de-situacion-fiscal",
     "fundamento_legal": "Art. 27 CFF"},
    {"homoclave": "SAT-08-001", "nombre": "Inscripción al RFC",
     "dependencia": "SAT", "sector": "hacienda_finanzas",
     "modalidad": "Mixto", "costo_mxn": 0,
     "url_tramite": "https://www.sat.gob.mx/tramites/operacion/15433/inscribete-en-el-rfc-como-persona-fisica-con-curp",
     "fundamento_legal": "Art. 27 CFF + RCFF Art. 22"},
    {"homoclave": "IMSS-02-025-A", "nombre": "Semanas cotizadas IMSS",
     "dependencia": "IMSS", "sector": "trabajo_prevision",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.imss.gob.mx/tramites/imss02025a",
     "fundamento_legal": "Art. 295 LSS"},
    {"homoclave": "RENAPO-CURP", "nombre": "Consulta CURP",
     "dependencia": "RENAPO", "sector": "gobernacion",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.gob.mx/curp/",
     "fundamento_legal": "Reglamento Ley General Población"},
    {"homoclave": "INE-CV", "nombre": "Credencial para votar",
     "dependencia": "INE", "sector": "sector_electoral",
     "modalidad": "Mixto", "costo_mxn": 0,
     "url_tramite": "https://www.ine.mx/credencial/",
     "fundamento_legal": "LGIPE Art. 130"},
    {"homoclave": "SRE-PASAPORTE", "nombre": "Pasaporte mexicano",
     "dependencia": "SRE", "sector": "relaciones_exteriores",
     "modalidad": "Presencial", "costo_mxn": 1830,
     "url_tramite": "https://www.gob.mx/tramites/ficha/pasaporte-ordinario-en-territorio-nacional/SRE227",
     "fundamento_legal": "Ley de Migración Art. 11"},
    {"homoclave": "COFEPRIS-AVISO-FUNC", "nombre": "Aviso de Funcionamiento COFEPRIS",
     "dependencia": "COFEPRIS", "sector": "salud_deporte",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://www.gob.mx/cofepris",
     "fundamento_legal": "Ley General Salud Art. 200 bis"},
    {"homoclave": "STPS-REPSE", "nombre": "Registro REPSE",
     "dependencia": "STPS", "sector": "trabajo_prevision",
     "modalidad": "Digital", "costo_mxn": 0,
     "url_tramite": "https://repse.stps.gob.mx/",
     "fundamento_legal": "LFT Art. 15"},
    {"homoclave": "IMPI-MARCA", "nombre": "Registro de marca IMPI",
     "dependencia": "IMPI", "sector": "desarrollo_economico",
     "modalidad": "Mixto", "costo_mxn": 3231,
     "url_tramite": "https://www.gob.mx/impi",
     "fundamento_legal": "Ley Federal Protección Propiedad Industrial"},
    {"homoclave": "CRE-20-001-I", "nombre": "Permiso comercialización hidrocarburos",
     "dependencia": "CRE", "sector": "energia",
     "modalidad": "Mixto", "costo_mxn": 47000,
     "url_tramite": "https://catalogonacional.gob.mx/FichaTramite?traHomoclave=CRE-20-001-I",
     "fundamento_legal": "Ley Hidrocarburos"},
    {"homoclave": "CONAGUA-REPDA", "nombre": "Inscripción REPDA",
     "dependencia": "CONAGUA", "sector": "agua",
     "modalidad": "Presencial", "costo_mxn": 0,
     "url_tramite": "https://www.gob.mx/conagua",
     "fundamento_legal": "Ley Aguas Nacionales Art. 30"},
    {"homoclave": "SEP-CEDULA", "nombre": "Cédula profesional SEP",
     "dependencia": "SEP", "sector": "ciencia_educacion",
     "modalidad": "Digital", "costo_mxn": 1670,
     "url_tramite": "https://www.cedulaprofesional.sep.gob.mx/",
     "fundamento_legal": "Ley Reglamentaria Art. 5 Constitucional"},
]


class RetysCatalogoClient:
    def __init__(self, bitacora: Bitacora | None = None) -> None:
        self._bitacora = bitacora or Bitacora(NAMESPACE)

    def _log(self, op: str, params: dict[str, Any]) -> None:
        self._bitacora.log(op, success=True, params_summary=params)

    def listar_sectores(self) -> dict[str, Any]:
        """Los 27 temas de interés de la portada del Catálogo Nacional (verificados 2026-10-14)."""
        self._log("listar_sectores", {})
        return {
            "total_sectores": len(SECTORES_CONAMER),
            "sectores": [{"clave": k, "nombre": v} for k, v in SECTORES_CONAMER.items()],
            "fuente": URL_CONAMER,
        }

    def _solo_mock(self, tool: str) -> None:
        if not is_mock_mode([], default_when_no_creds=False):
            raise ConfigError(
                f"{tool} usa un catálogo curado no verificado; solo disponible con PLUGINS_MX_MOCK=1. "
                "Para datos oficiales usa retys_buscar_en_vivo."
            )

    def buscar_tramite(
        self, q: str, sector: str | None = None
    ) -> dict[str, Any]:
        """Fuera de mock delega en la búsqueda en vivo (regulaciones + inspecciones)."""
        if not q or len(q) < 2:
            raise ValidationError("Query debe tener al menos 2 caracteres")
        if sector and sector.lower().strip() not in SECTORES_CONAMER:
            raise ValidationError(f"sector inválido: {sector!r}")
        if not is_mock_mode([], default_when_no_creds=False):
            out = self.buscar_en_vivo(q)
            out["nota_tramites"] = ("El Catálogo Nacional ya no publica trámites en su buscador; "
                                    "se devuelven regulaciones e inspecciones. Filtro de sector no aplicado.")
            return out
        return self._buscar_curado(q, sector)

    def _buscar_curado(
        self, q: str, sector: str | None = None
    ) -> dict[str, Any]:
        """Búsqueda de trámites por texto + filtro de sector."""
        self._log("buscar_tramite", {"q": q, "sector": sector})
        if not q or len(q) < 2:
            raise ValidationError("Query debe tener al menos 2 caracteres")
        q_norm = q.lower().strip()
        candidatos = TRAMITES_DEMANDA_ALTA
        if sector:
            sector_norm = sector.lower().strip()
            if sector_norm not in SECTORES_CONAMER:
                raise ValidationError(f"sector inválido: {sector!r}")
            candidatos = [t for t in candidatos if t["sector"] == sector_norm]
        matches = [
            t for t in candidatos
            if q_norm in t["nombre"].lower()
            or q_norm in t["homoclave"].lower()
            or q_norm in t["dependencia"].lower()
        ]
        return mark_simulated(
            {
                "query": q,
                "sector_filtro": sector,
                "total_resultados": len(matches),
                "resultados": matches,
                "fuente": URL_CONAMER,
                "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            },
            note="PLUGINS_MX_MOCK=1 — catálogo curado no verificado.",
        )

    def detalle_tramite(self, homoclave: str) -> dict[str, Any]:
        """Detalle por homoclave. Fuera de mock: URL oficial de la ficha (R-/I-)."""
        self._log("detalle_tramite", {"homoclave": homoclave})
        hc = (homoclave or "").upper().strip()
        if not is_mock_mode([], default_when_no_creds=False):
            if hc.startswith("I-"):
                url = f"{URL_CONAMER}FichaInspeccion?homoClave={quote(hc)}"
            elif hc.startswith("R-"):
                url = f"{URL_CONAMER}FichaRegulacion?Homoclave={quote(hc)}"
            else:
                raise ValidationError("Homoclave CONAMER esperada con prefijo R- (regulación) o I- (inspección)")
            return {"homoclave": hc, "url_ficha": url, "simulated": False,
                    "nota": "La ficha está detrás de Akamai; ábrela en navegador o con retys_buscar_en_vivo."}
        for t in TRAMITES_DEMANDA_ALTA:
            if t["homoclave"].upper() == hc:
                return mark_simulated(
                    {**t, "fecha_corte": datetime.now(timezone.utc).strftime("%Y-%m-%d")},
                    note="Catálogo curado — para detalle oficial: portal CONAMER.",
                )
        raise ValidationError(f"Homoclave no en catálogo curado: {homoclave!r}")

    def exportar_dcat(self) -> dict[str, Any]:
        """Exporta a formato DCAT (Data Catalog Vocabulary) compatible datos.gob.mx."""
        self._log("exportar_dcat", {})
        self._solo_mock("retys_exportar_dcat")
        return {
            "@context": "https://www.w3.org/ns/dcat",
            "@type": "Catalog",
            "title": "Catálogo de Trámites Federales MX — Plugins MX",
            "description": (
                "Catálogo curado de trámites federales de alta demanda, "
                "normalizado para datos.gob.mx (Sistema Ajolote)."
            ),
            "publisher": "Plugins MX (elimoralsmendox@gmail.com)",
            "issued": "2026-06-15",
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "dataset": [
                {
                    "@type": "Dataset",
                    "identifier": t["homoclave"],
                    "title": t["nombre"],
                    "publisher": t["dependencia"],
                    "theme": SECTORES_CONAMER.get(t["sector"], t["sector"]),
                    "accessURL": t["url_tramite"],
                    "fundamentoLegal": t["fundamento_legal"],
                    "costoMXN": t["costo_mxn"],
                    "modalidad": t["modalidad"],
                }
                for t in TRAMITES_DEMANDA_ALTA
            ],
        }

    def buscar_en_vivo(self, q: str) -> dict[str, Any]:
        """Regulaciones + inspecciones del Catálogo Nacional con Chromium real. Sin fallback."""
        self._log("buscar_en_vivo", {"q": q})
        if not q or len(q.strip()) < 2:
            raise ValidationError("Query debe tener al menos 2 caracteres")
        if is_mock_mode([], default_when_no_creds=False):
            return mark_simulated(self._buscar_curado(q, None), note="PLUGINS_MX_MOCK=1")

        from shared.playwright_real import playwright_session

        qs = (f"?search={quote(q.strip())}&txtTipo=Todos&nivelId=-1&estadoId=-1"
              "&municipioId=-1&dependenciaId=-1&tem=0")
        with playwright_session() as page:  # UpstreamError si Playwright falla
            resp = page.goto(URL_CONAMER, wait_until="domcontentloaded")
            if resp is not None and resp.status == 403:
                raise UpstreamError(
                    "Akamai bloqueó el navegador (403). Ejecuta con MP_PLAYWRIGHT_HEADLESS=0.",
                    {"url": URL_CONAMER},
                )
            page.wait_for_selector("#txtSearch", timeout=15000)
            fragmentos = page.evaluate(
                """async (qs) => {
                    await fetch('/Buscador/DeleteCookie' + qs.split('&')[0], {method: 'POST'});
                    const out = {};
                    for (const k of ['SearchRegulacionResult', 'SearchInspeccionResult']) {
                        const r = await fetch('/Buscador/' + k + qs);
                        out[k] = {status: r.status, html: await r.text()};
                    }
                    return out;
                }""",
                qs,
            )
        secciones = {}
        for clave, nombre in (("SearchRegulacionResult", "regulaciones"),
                              ("SearchInspeccionResult", "inspecciones")):
            frag = fragmentos[clave]
            if frag["status"] != 200:
                secciones[nombre] = {"error": f"HTTP {frag['status']}"}
                continue
            secciones[nombre] = parse_resultados(frag["html"])
        return {
            "query": q,
            **secciones,
            "fuente": URL_CONAMER,
            "fecha_consulta": datetime.now(timezone.utc).isoformat(),
            "simulated": False,
        }


_FICHAS = {
    "Inspeccion": "FichaInspeccion?homoClave=",
    "Regulacion": "FichaRegulacion?Homoclave=",
    "Regulacionid": "FichaRegulacionid?regulacionId=",
}


def _limpio(fragmento: str) -> str:
    return " ".join(html_lib.unescape(re.sub(r"<[^>]+>", " ", fragmento)).split())


def parse_resultados(fragmento: str) -> dict[str, Any]:
    """Parsea el fragmento HTML de /Buscador/Search*Result (primera página, ≤10 items)."""
    m_err = re.search(r'value="([^"]*)" name="Error"', fragmento)
    if m_err and m_err.group(1).strip():
        return {"error": html_lib.unescape(m_err.group(1)).strip(), "resultados": []}
    resultados = []
    for bloque in fragmento.split('item-search-result"')[1:]:
        m_id = re.search(r"GoTo(\w+)\('([^']+)'\)", bloque)
        m_tit = re.search(r'item-title-search-result">(.*?)</p>', bloque, re.S)
        etiquetas = [_limpio(x) for x in re.findall(
            r'<label class="item-[a-z-]*search-result">(.*?)</label>', bloque, re.S)]
        etiquetas = [e for e in etiquetas if e]
        dependencia, tipo = None, None
        if etiquetas and "|" in etiquetas[0]:
            dependencia, tipo = (x.strip() for x in etiquetas[0].split("|", 1))
        tipo_ficha, homoclave = (m_id.group(1), m_id.group(2)) if m_id else (None, None)
        resultados.append({
            "homoclave": homoclave,
            "titulo": _limpio(m_tit.group(1)) if m_tit else None,
            "dependencia": dependencia,
            "tipo": tipo,
            "detalles": etiquetas[1:],
            "url_ficha": (URL_CONAMER + _FICHAS[tipo_ficha] + quote(homoclave)
                          if tipo_ficha in _FICHAS else None),
        })
    return {"resultados": resultados, "en_pagina": len(resultados)}
